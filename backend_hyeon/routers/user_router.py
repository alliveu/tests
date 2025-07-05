# routers/user_router.py
# Cynario 회원가입, 로그인 라우터 (문서 기반)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import user as user_schema
from services import user_service

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)

# 회원가입 엔드포인트
@router.post("/signup", response_model=user_schema.UserResponse)
def signup(user_data: user_schema.SignupRequest, db: Session = Depends(get_db)):
    """
    회원가입 API
    - email, password, name 전달
    - 이메일 중복 확인 후 계정 생성
    """
    user = user_service.create_user(db, user_data)
    return user

# 로그인 엔드포인트
@router.post("/login", response_model=user_schema.UserResponse)
def login(login_data: user_schema.LoginRequest, db: Session = Depends(get_db)):
    """
    로그인 API
    - email, password 전달
    - 이메일/비밀번호 확인 후 사용자 정보 반환
    """
    user = user_service.authenticate_user(db, login_data)
    return user
