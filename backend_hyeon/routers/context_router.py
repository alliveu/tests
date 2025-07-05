# routers/context_router.py
# 카카오톡 txt 업로드 및 분석 엔드포인트

from fastapi import APIRouter, Depends, UploadFile, Form
from sqlalchemy.orm import Session

from database import get_db
from services import context_service
from schemas import context as context_schema

router = APIRouter(
    prefix="/api/upload",
    tags=["Upload"]
)

@router.post("/context", response_model=context_schema.UploadResponse)
async def upload_kakao_chat(
    file: UploadFile,
    prompt_info: str = Form(""),  # 선택적으로 추가 프롬프트 전달
    user_id: int = 1,  # JWT 연동 시 교체 예정
    db: Session = Depends(get_db)
):
    """
    카카오톡 txt 파일 업로드 및 분석 API
    - 파일 업로드 후 파싱 및 분석 → DB 저장
    - analysis_id 반환
    """
    result = context_service.upload_and_analyze_kakao_chat(db, user_id, file, prompt_info)
    return result

