from pydantic import BaseModel
from typing import Optional, List


class AnalyzeRequest(BaseModel):
    """分析请求"""
    image_base64: Optional[str] = None  # base64 encoded image (optional)
    report_text: str                    # radiology report text
    mode: str = "multimodal"            # "multimodal" or "text_only"


class ChexpertLabels(BaseModel):
    """CheXpert 14类标签"""
    Atelectasis: Optional[str] = None
    Cardiomegaly: Optional[str] = None
    Consolidation: Optional[str] = None
    Edema: Optional[str] = None
    EnlargedCardiomediastinum: Optional[str] = None
    Fracture: Optional[str] = None
    LungLesion: Optional[str] = None
    LungOpacity: Optional[str] = None
    PleuralEffusion: Optional[str] = None
    Pneumonia: Optional[str] = None
    Pneumothorax: Optional[str] = None
    PleuralOther: Optional[str] = None
    SupportDevices: Optional[str] = None
    NoFinding: Optional[str] = None


class AnalysisResult(BaseModel):
    """分析结果"""
    findings: str                       # 主要影像学发现
    impression: str                     # 综合印象
    recommendations: str                 # 随访或治疗建议
    chexpert_labels: ChexpertLabels     # 14类CheXpert标签判断


class CompareResponse(BaseModel):
    """对比分析结果"""
    multimodal: AnalysisResult
    text_only: AnalysisResult
