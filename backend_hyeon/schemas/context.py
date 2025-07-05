# schemas/context.py
# 카카오톡 txt 파일 업로드 및 분석 요청/응답 스키마

from pydantic import BaseModel

# 업로드 응답용
class UploadResponse(BaseModel):
    success: bool
    message: str
    analysis_id: int

from pydantic import BaseModel

class UploadResponse(BaseModel):
    success: bool
    message: str
    analysis_id: int
