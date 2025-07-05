# schemas/basic_info.py
# Cynario 사용자 기본 정보 요청/응답 스키마 (문서 기반)

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 기본정보 등록 요청용
class BasicInfoRequest(BaseModel):
    name: str
    grade_class: Optional[str] = None
    relationship_status: Optional[str] = None
    home_phone: Optional[str] = None
    mobile_phone: Optional[str] = None
    address: Optional[str] = None

# 기본정보 응답용
class BasicInfoResponse(BasicInfoRequest):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2: ORM 객체 → Pydantic 변환 허용
