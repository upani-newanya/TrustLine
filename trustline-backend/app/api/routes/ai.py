from fastapi import APIRouter

from app.ml.inference import analyze_text
from app.schemas.ai import AIAnalyzeRequest, AIAnalyzeResponse

router = APIRouter()


@router.post("/analyze", response_model=AIAnalyzeResponse)
def analyze(payload: AIAnalyzeRequest):
    return analyze_text(payload.text)
