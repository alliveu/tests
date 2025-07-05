# schemas/user.py
# Cynario 회원가입, 로그인, 응답용 Pydantic 스키마 (문서 기반)

from pydantic import BaseModel, EmailStr
from datetime import datetime

# 회원가입 요청용
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

# 로그인 요청용
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 사용자 응답용
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str

    class Config:
        from_attributes = True  # Pydantic v2: ORM 객체 변환 허용
