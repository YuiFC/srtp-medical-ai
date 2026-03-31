"""MIMIC-CXR 多模态胸片+报告解读与纯文本对照脚本

核心功能：
- 输入：一张胸部 X 光 JPG 图片 + 对应放射学报告文本
- 输出：
  - 多模态模型（图像+文本）解读
  - 纯文本 LLM（仅报告文本）解读
  - 与 CheXpert 14 类标签的简单对比

说明：
- 为了方便在本地/不同模型之间切换，本脚本将“调用模型”的部分封装成函数，
  目前默认实现使用 OpenAI API（可改成 Qwen-VL / LLaVA / 本地模型）。
- 请先在系统环境变量或 .env 中设置 OPENAI_API_KEY。
- 如果你后续需要，我可以帮你把模型调用部分改成 HuggingFace 本地推理版本。
"""

import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
from PIL import Image
from dotenv import load_dotenv

try:
    # OpenAI 官方 SDK（>=1.0）
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - 仅为避免导入失败中断
    OpenAI = None  # type: ignore


# 14 类 CheXpert 标签名称（与 chexpert.csv 对应）
CHEXPERT_LABELS: List[str] = [
    "Atelectasis",
    "Cardiomegaly",
    "Consolidation",
    "Edema",
    "Enlarged Cardiomediastinum",
    "Fracture",
    "Lung Lesion",
    "Lung Opacity",
    "Pleural Effusion",
    "Pneumonia",
    "Pneumothorax",
    "Pleural Other",
    "Support Devices",
    "No Finding",
]


@dataclass
class ModelConfig:
    """模型与路径配置"""

    # OpenAI / 其他兼容接口
    openai_model_multimodal: str = "gpt-4.1-mini"  # 支持 vision
    openai_model_text: str = "gpt-4.1-mini"  # 仅文本

    # 数据路径（根据你的仓库结构默认设置）
    data_root: str = os.path.join("..", "SRTP_Data")
    chexpert_csv: str = os.path.join("..", "SRTP_Data", "mimic-cxr-2.0.0-chexpert.csv")


# =====================
# 数据加载与标签匹配
# =====================


def parse_ids_from_path(image_path: str) -> Optional[Dict[str, str]]:
    """从 MIMIC-CXR-JPG 路径或文件名中解析 subject_id / study_id。

    典型路径示例：
    files/p10/p10000032/s56699142/10000032_56699142_1.jpg
    """

    basename = os.path.basename(image_path)
    m = re.match(r"(\d+)_(\d+)_", basename)
    if not m:
        return None
    subject_id, study_id = m.group(1), m.group(2)
    return {"subject_id": subject_id, "study_id": study_id}


def load_chexpert_labels(config: ModelConfig) -> pd.DataFrame:
    """加载 CheXpert 标签 CSV。

    返回的 DataFrame 至少包含 subject_id, study_id 以及 14 个标签列。
    标签值含义：1=阳性, 0=阴性, -1=不确定, NaN=未标注。
    """

    df = pd.read_csv(config.chexpert_csv)
    # 统一列名风格（官方就是这种写法，这里仅确保存在）
    missing = [c for c in CHEXPERT_LABELS if c not in df.columns]
    if missing:
        raise ValueError(f"CheXpert CSV 缺少列: {missing}")
    return df


def get_labels_for_study(df: pd.DataFrame, subject_id: str, study_id: str) -> Dict[str, Optional[float]]:
    """获取指定 subject_id + study_id 的 14 类标签。"""

    sub_id = int(subject_id)
    stu_id = int(study_id)
    row = df[(df["subject_id"] == sub_id) & (df["study_id"] == stu_id)]
    if row.empty:
        return {}
    row = row.iloc[0]
    labels: Dict[str, Optional[float]] = {}
    for lab in CHEXPERT_LABELS:
        val = row.get(lab)
        labels[lab] = float(val) if pd.notna(val) else None
    return labels


# =====================
# 模型调用封装
# =====================


def get_openai_client() -> Optional["OpenAI"]:
    """初始化 OpenAI 客户端（如果未安装 SDK 或未设置 key，则返回 None）。"""

    load_dotenv(override=False)
    api_key = os.getenv("OPENAI_API_KEY")
    if OpenAI is None or not api_key:
        return None
    return OpenAI(api_key=api_key)


def build_system_prompt() -> str:
    """统一的系统提示词：多模态 / 纯文本均可复用。"""

    return (
        "你是一名放射科主治医师，需要根据胸部 X 光片和放射学报告，"
        "输出结构化的中文解读结果，用于科普给普通患者。"
        "请严格按照 JSON 格式输出，键包括: "
        "`findings`(主要影像学发现), `impression`(综合印象), "
        "`recommendations`(随访或治疗建议), `chexpert_labels`(14 类标签判断)。"
        "其中 `chexpert_labels` 是一个对象，键为 14 个疾病名，值为 'positive'、'negative' 或 'uncertain'。"
    )


def build_user_prompt_for_text(report_text: str) -> str:
    """仅基于报告文本的用户提示词。"""

    return (
        "以下是胸部 X 光的英文放射学报告全文。"
        "请忽略可能出现的患者姓名等隐私信息，只关注影像学内容。\n\n"
        f"[放射学报告]\n{report_text}\n\n"
        "请根据以上报告内容完成结构化解读，并输出 JSON。"
    )


def build_user_prompt_for_multimodal(report_text: str) -> str:
    """基于图像 + 文本的用户提示词（图像在 message 的 content 中单独传入）。"""

    return (
        "我会提供一张胸部 X 光图像以及对应的英文放射学报告，"
        "请你结合图像和报告一起进行判断。如果图像与报告描述不符，"
        "以图像为主，但在印象中说明差异。\n\n"
        f"[放射学报告]\n{report_text}\n\n"
        "请输出 JSON 结果。"
    )


def call_text_only_llm(report_text: str, config: ModelConfig) -> Dict:
    """调用纯文本 LLM，对报告进行解读。

    返回一个 Python dict，如果解析失败则抛出异常或返回空结构。
    """

    client = get_openai_client()
    if client is None:
        raise RuntimeError("OpenAI SDK 未安装或 OPENAI_API_KEY 未设置，无法调用文本模型。")

    sys_prompt = build_system_prompt()
    user_prompt = build_user_prompt_for_text(report_text)

    resp = client.chat.completions.create(
        model=config.openai_model_text,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    content = resp.choices[0].message.content
    assert content is not None
    return json.loads(content)


def call_multimodal_llm(image_path: str, report_text: str, config: ModelConfig) -> Dict:
    """调用多模态 LLM（图像 + 文本）。

    这里示例使用 OpenAI 兼容接口（例如 gpt-4.1-mini / gpt-4o）。
    如果你使用 Qwen-VL / LLaVA，本函数需要替换为相应的推理代码。
    """

    client = get_openai_client()
    if client is None:
        raise RuntimeError("OpenAI SDK 未安装或 OPENAI_API_KEY 未设置，无法调用多模态模型。")

    sys_prompt = build_system_prompt()
    user_prompt = build_user_prompt_for_multimodal(report_text)

    # OpenAI vision 接口：content 是一个列表，包含 text 与 image_url 两种类型
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    base64_image = "data:image/jpeg;base64," + image_bytes.encode("base64").decode("utf-8")  # type: ignore[attr-defined]

    resp = client.chat.completions.create(
        model=config.openai_model_multimodal,
        messages=[
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": base64_image}},
                ],
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    content = resp.choices[0].message.content
    assert content is not None
    return json.loads(content)


# =====================
# 结果对比与打印
# =====================


def compare_with_chexpert(pred_labels: Dict, gt_labels: Dict[str, Optional[float]]) -> Dict[str, Dict[str, Optional[str]]]:
    """将 LLM 预测标签与 CheXpert 真值进行逐项对比。

    返回结构：{label_name: {"pred": str or None, "gt": str or None}}
    其中 gt 使用 'positive'/'negative'/'uncertain'/None 四种表达。
    """

    def map_gt(v: Optional[float]) -> Optional[str]:
        if v is None:
            return None
        if v > 0:
            return "positive"
        if v < 0:
            return "uncertain"  # CheXpert 中 -1 通常表示不确定
        return "negative"

    result: Dict[str, Dict[str, Optional[str]]] = {}
    for lab in CHEXPERT_LABELS:
        pred_val = None
        if isinstance(pred_labels, dict):
            raw = pred_labels.get(lab)
            if isinstance(raw, str):
                pred_val = raw.lower()
        gt_val = map_gt(gt_labels.get(lab)) if gt_labels else None
        result[lab] = {"pred": pred_val, "gt": gt_val}
    return result


def pretty_print_results(
    image_path: str,
    multimodal_res: Dict,
    text_res: Dict,
    chexpert_comparison_multi: Dict[str, Dict[str, Optional[str]]],
    chexpert_comparison_text: Dict[str, Dict[str, Optional[str]]],
) -> None:
    """终端打印对比结果，方便你在问卷或实验中使用。"""

    print("=" * 80)
    print(f"图像路径: {image_path}")
    print("=" * 80)

    print("[多模态模型（图像+报告）解读]\n")
    print("主要发现:", multimodal_res.get("findings"))
    print("综合印象:", multimodal_res.get("impression"))
    print("建议:", multimodal_res.get("recommendations"))
    print("\n与 CheXpert 标签对比 (multi):")
    for lab, vals in chexpert_comparison_multi.items():
        print(f"- {lab}: pred={vals['pred']}, gt={vals['gt']}")

    print("\n" + "-" * 80)
    print("[纯文本 LLM（仅报告）解读]\n")
    print("主要发现:", text_res.get("findings"))
    print("综合印象:", text_res.get("impression"))
    print("建议:", text_res.get("recommendations"))
    print("\n与 CheXpert 标签对比 (text-only):")
    for lab, vals in chexpert_comparison_text.items():
        print(f"- {lab}: pred={vals['pred']}, gt={vals['gt']}")


# =====================
# 主流程（命令行接口）
# =====================


def main() -> None:
    parser = argparse.ArgumentParser(description="MIMIC-CXR 多模态胸片+报告解读与对比")
    parser.add_argument("--image", required=True, help="胸片 JPG 图像路径（MIMIC-CXR-JPG 文件）")
    report_group = parser.add_mutually_exclusive_group(required=True)
    report_group.add_argument("--report-text", help="直接传入放射学报告全文（英文）")
    report_group.add_argument("--report-file", help="放射学报告 txt 文件路径")
    args = parser.parse_args()

    image_path = args.image
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"找不到图像文件: {image_path}")

    # 读取报告文本
    if args.report_text:
        report_text = args.report_text
    else:
        with open(args.report_file, "r", encoding="utf-8") as f:  # type: ignore[arg-type]
            report_text = f.read()

    # 简单验证图像能否打开（如果只是用 API，可选）
    _ = Image.open(image_path).convert("RGB")

    config = ModelConfig()

    # 解析 subject_id / study_id 并加载 CheXpert 标签
    ids = parse_ids_from_path(image_path)
    chexpert_labels: Dict[str, Optional[float]] = {}
    if ids is not None:
        df = load_chexpert_labels(config)
        chexpert_labels = get_labels_for_study(df, ids["subject_id"], ids["study_id"])
    else:
        print("警告：未能从文件名解析出 subject_id / study_id，将无法对比 CheXpert 标签。")

    # 调用多模态与纯文本模型
    multimodal_res = call_multimodal_llm(image_path, report_text, config)
    text_res = call_text_only_llm(report_text, config)

    multi_cmp = compare_with_chexpert(multimodal_res.get("chexpert_labels", {}), chexpert_labels)
    text_cmp = compare_with_chexpert(text_res.get("chexpert_labels", {}), chexpert_labels)

    pretty_print_results(image_path, multimodal_res, text_res, multi_cmp, text_cmp)


if __name__ == "__main__":
    main()
