# services/user_service.py
# Cynario 회원가입, 로그인 처리 서비스 로직 (문서 기반)

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import HTTPException, status

from models import user as user_model
from schemas import user as user_schema

# 비밀번호 해싱용 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 해싱
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 회원가입 서비스
def create_user(db: Session, user_data: user_schema.SignupRequest) -> user_schema.UserResponse:
    existing_user = db.query(user_model.User).filter(user_model.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 가입된 이메일입니다.")

    hashed_pw = hash_password(user_data.password)

    db_user = user_model.User(
        email=user_data.email,
        password_hash=hashed_pw,
        name=user_data.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return user_schema.UserResponse.model_validate(db_user)

# 로그인 서비스
def authenticate_user(db: Session, login_data: user_schema.LoginRequest) -> user_schema.UserResponse:
    user = db.query(user_model.User).filter(user_model.User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="존재하지 않는 이메일입니다.")

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="비밀번호가 일치하지 않습니다.")

    return user_schema.UserResponse.model_validate(user)
