# routers/basic_info_router.py
# Cynario 사용자 기본정보 등록 및 조회 라우터 (문서 기반)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import basic_info as basic_info_schema
from services import basic_info_service

router = APIRouter(
    prefix="/api/user",
    tags=["BasicInfo"]
)

# (임시) 사용자 인증 없이 user_id 직접 전달 방식
# JWT 연동 시 user_id는 토큰에서 추출하여 사용 예정

# 기본정보 등록
@router.post("/basic-info", response_model=basic_info_schema.BasicInfoResponse)
def create_basic_info(
    basic_info_data: basic_info_schema.BasicInfoRequest,
    user_id: int = 1,  # 테스트용 user_id 하드코딩
    db: Session = Depends(get_db)
):
    """
    사용자 기본정보 등록 API
    """
    basic_info = basic_info_service.create_basic_info(db, user_id, basic_info_data)
    return basic_info

# 기본정보 조회
@router.get("/basic-info", response_model=basic_info_schema.BasicInfoResponse)
def get_basic_info(
    user_id: int = 1,  # 테스트용 user_id 하드코딩
    db: Session = Depends(get_db)
):
    """
    사용자 기본정보 조회 API
    """
    basic_info = basic_info_service.get_basic_info(db, user_id)
    return basic_info
