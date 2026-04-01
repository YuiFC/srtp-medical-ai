"""
GLM-4.6V 调用模块（通过独立子进程 + curl -v）
支持多模态（图像+报告）和纯文本两种模式
"""

import os
import json
import base64
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# 加载 code/.env 配置
PROJECT_ROOT = Path(__file__).parent.parent.parent
CODE_DIR = PROJECT_ROOT / "code"
ENV_FILE = CODE_DIR / ".env"
load_dotenv(ENV_FILE, override=False)

GLM_API_KEY = os.getenv("GLM_API_KEY")
GLM_API_BASE = os.getenv("GLM_API_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
GLM_MODEL_MULTIMODAL = "glm-4.6v"
GLM_MODEL_TEXT = "glm-4.6v"

# 启动器脚本路径
LAUNCHER = Path(__file__).parent / "glm_caller.py"


def build_system_prompt() -> str:
    return (
        "你是一名放射科主治医师，需要根据胸部X光片和放射学报告，"
        "输出结构化的中文解读结果，用于科普给普通患者。"
        "请严格按照JSON格式输出，键包括："
        "findings（主要影像学发现），impression（综合印象），"
        "recommendations（随访或治疗建议），chexpert_labels（14类标签判断）。"
        "其中chexpert_labels是一个对象，键为14个疾病名，值为positive、negative或uncertain（不确定）。"
        "请不要输出任何解释性文字或Markdown标记，仅输出一个合法的JSON对象。"
    )


def build_text_prompt(report_text: str) -> str:
    return (
        "以下是胸部X光的英文放射学报告全文。"
        "请忽略可能出现的患者姓名等隐私信息，只关注影像学内容。\n\n"
        f"[放射学报告]\n{report_text}\n\n"
        "请根据以上报告内容完成结构化解读，并仅输出JSON。"
    )


def build_multimodal_prompt(report_text: str) -> str:
    return (
        "我会提供一张胸部X光图像以及对应的英文放射学报告，"
        "请你结合图像和报告一起进行判断。如果图像与报告描述不符，"
        "以图像为主，但在印象中说明差异。\n\n"
        f"[放射学报告]\n{report_text}\n\n"
        "请严格按照前述JSON结构，仅输出JSON。"
    )


def cleanup_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```") and text.endswith("```"):
        inner = text.strip("`").strip()
        if inner.lower().startswith("json"):
            inner = inner[4:].lstrip()
        text = inner
    if not text.lstrip().startswith("{"):
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            text = text[first: last + 1]
    return text.strip()


def parse_json_response(response_text: str) -> dict:
    cleaned = cleanup_json_text(response_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        preview = cleaned[:300].replace("\n", " ")
        raise RuntimeError(f"GLM返回内容不是合法JSON。前300字符: {preview}") from e


def _call_glm_via_launcher(messages: list, model: str) -> str:
    """
    通过 glm_caller.py 脚本调用 GLM API
    脚本内部使用 curl -v 确保在 uvicorn 线程池环境中正常工作
    """
    input_data = {
        "api_key": GLM_API_KEY,
        "api_base": GLM_API_BASE,
        "model": model,
        "messages": messages,
    }
    input_json = json.dumps(input_data, ensure_ascii=False)

    result = subprocess.run(
        [sys.executable, str(LAUNCHER)],
        input=input_json,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(f"GLM调用失败: {result.stderr[:200]}")

    # launcher 输出的是纯 JSON
    try:
        output = json.loads(result.stdout)
        if "error" in output:
            raise RuntimeError(f"GLM返回错误: {output['error']}")
        # launcher 返回 GLM API 的原始响应（包含 choices）
        return json.dumps(output)
    except json.JSONDecodeError:
        raise RuntimeError(f"GLM launcher 返回非JSON: {result.stdout[:200]}")


def call_glm(messages: list, model: str) -> str:
    """调用 GLM API 并从响应中提取文本内容"""
    raw = _call_glm_via_launcher(messages, model)
    data = json.loads(raw)
    if not data.get("choices"):
        raise RuntimeError("GLM返回结果中缺少choices")
    return data["choices"][0]["message"]["content"]


def analyze_text_only(report_text: str) -> dict:
    """纯文本模式：仅根据报告文本进行分析"""
    sys_prompt = build_system_prompt()
    user_prompt = build_text_prompt(report_text)
    combined = sys_prompt + "\n\n" + user_prompt

    response_text = call_glm(
        messages=[{"role": "user", "content": combined}],
        model=GLM_MODEL_TEXT,
    )

    return parse_json_response(response_text)


def analyze_multimodal(image_base64: str, report_text: str) -> dict:
    """多模态模式：结合图像和报告文本进行分析"""
    sys_prompt = build_system_prompt()
    user_prompt = build_multimodal_prompt(report_text)
    combined = sys_prompt + "\n\n" + user_prompt

    response_text = call_glm(
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
                {"type": "text", "text": combined},
            ],
        }],
        model=GLM_MODEL_MULTIMODAL,
    )

    return parse_json_response(response_text)
