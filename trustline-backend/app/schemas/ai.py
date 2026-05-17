from pydantic import BaseModel, Field


class AIAnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)


class AIAnalyzeResponse(BaseModel):
    input_text: str
    distress_prediction: str
    distress_confidence: float
    emotion_prediction: str
    emotion_confidence: float
