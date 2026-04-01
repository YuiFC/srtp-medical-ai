"""
SRTP 医学AI Webapp 后端 API
提供多模态AI和纯文本LLM的放射学报告解读接口
"""

import os
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# 全局线程池，用于执行阻塞的 GLM API 调用
_executor = ThreadPoolExecutor(max_workers=4)

# 确保能导入同级目录模块
sys.path.insert(0, str(Path(__file__).parent))

from models import AnalyzeRequest, AnalysisResult, ChexpertLabels, CompareResponse
import analyzer

# 加载 code/.env 配置（项目根目录的 code/ 下）
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / "code" / ".env"
load_dotenv(ENV_FILE, override=True)

app = FastAPI(
    title="SRTP 医学AI分析API",
    description="多模态AI与纯文本LLM放射学报告解读",
    version="1.0.0",
)

# CORS：允许 Vite 开发服务器（5173）访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def dict_to_chexpert_labels(d: dict) -> ChexpertLabels:
    """将字典映射到 ChexpertLabels"""
    mapping = {
        "Atelectasis": "Atelectasis",
        "Cardiomegaly": "Cardiomegaly",
        "Consolidation": "Consolidation",
        "Edema": "Edema",
        "Enlarged Cardiomediastinum": "EnlargedCardiomediastinum",
        "EnlargedCardiomediastinum": "EnlargedCardiomediastinum",
        "Fracture": "Fracture",
        "Lung Lesion": "LungLesion",
        "LungLesion": "LungLesion",
        "Lung Opacity": "LungOpacity",
        "LungOpacity": "LungOpacity",
        "Pleural Effusion": "PleuralEffusion",
        "PleuralEffusion": "PleuralEffusion",
        "Pneumonia": "Pneumonia",
        "Pneumothorax": "Pneumothorax",
        "Pleural Other": "PleuralOther",
        "PleuralOther": "PleuralOther",
        "Support Devices": "SupportDevices",
        "SupportDevices": "SupportDevices",
        "No Finding": "NoFinding",
        "NoFinding": "NoFinding",
    }
    result = {}
    for key, value in d.items():
        mapped_key = mapping.get(key, key)
        result[mapped_key] = value
    return ChexpertLabels(**result)


def raw_to_result(raw: dict) -> AnalysisResult:
    """将原始GLM返回字典转为 AnalysisResult"""
    labels_raw = raw.get("chexpert_labels", {})
    return AnalysisResult(
        findings=raw.get("findings", ""),
        impression=raw.get("impression", ""),
        recommendations=raw.get("recommendations", ""),
        chexpert_labels=dict_to_chexpert_labels(labels_raw) if labels_raw else ChexpertLabels(),
    )


@app.get("/")
async def root():
    return {"message": "SRTP 医学AI分析API", "version": "1.0.0"}


@app.get("/debug")
async def debug():
    """Test endpoint that uses executor"""
    import time
    def blocking_func():
        time.sleep(2)
        return "done"
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, blocking_func)
    return {"result": result}


@app.get("/debug2")
async def debug2():
    """Test endpoint that makes HTTP call in executor"""
    import requests
    def http_func():
        r = requests.get("https://httpbin.org/get", timeout=10)
        return r.text[:100]
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, http_func)
    return {"result": result}


@app.get("/health")
async def health():
    api_key = os.getenv("GLM_API_KEY")
    return {
        "status": "ok",
        "glm_configured": bool(api_key),
        "glm_api_base": os.getenv("GLM_API_BASE_URL", ""),
    }


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze(req: AnalyzeRequest):
    """
    单一分析接口
    - mode=multimodal: 需要 image_base64 + report_text
    - mode=text_only: 仅需要 report_text（image_base64 可省略）
    """
    if not req.report_text.strip():
        raise HTTPException(status_code=400, detail="报告文本不能为空")

    loop = asyncio.get_event_loop()
    if req.mode == "text_only":
        raw = await loop.run_in_executor(_executor, analyzer.analyze_text_only, req.report_text)
    elif req.mode == "multimodal":
        if not req.image_base64:
            raise HTTPException(status_code=400, detail="多模态模式需要提供 image_base64")
        raw = await loop.run_in_executor(_executor, analyzer.analyze_multimodal, req.image_base64, req.report_text)
    else:
        raise HTTPException(status_code=400, detail=f"未知模式: {req.mode}")

    return raw_to_result(raw)


@app.post("/api/compare", response_model=CompareResponse)
async def compare(req: AnalyzeRequest):
    """
    对比分析接口
    同时返回多模态（图像+报告）和纯文本（仅报告）两种分析结果
    """
    if not req.report_text.strip():
        raise HTTPException(status_code=400, detail="报告文本不能为空")

    loop = asyncio.get_event_loop()
    text_raw = await loop.run_in_executor(_executor, analyzer.analyze_text_only, req.report_text)

    multimodal_raw = None
    if req.image_base64:
        multimodal_raw = await loop.run_in_executor(_executor, analyzer.analyze_multimodal, req.image_base64, req.report_text)
    else:
        # 没有图像时，多模态退化为纯文本
        multimodal_raw = text_raw

    return CompareResponse(
        multimodal=raw_to_result(multimodal_raw),
        text_only=raw_to_result(text_raw),
    )


if __name__ == "__main__":
    import uvicorn
    # 监听 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
