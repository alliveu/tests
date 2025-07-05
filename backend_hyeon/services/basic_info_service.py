# services/basic_info_service.py
# Cynario 사용자 기본정보 등록 및 조회 서비스 로직 (문서 기반)

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import user as user_model
from schemas import basic_info as basic_info_schema

# 기본정보 등록 서비스
def create_basic_info(
    db: Session,
    user_id: int,
    basic_info_data: basic_info_schema.BasicInfoRequest
) -> basic_info_schema.BasicInfoResponse:

    # 기존 기본정보가 있는 경우 삭제 (또는 업데이트)
    existing_info = db.query(user_model.BasicInfo).filter(user_model.BasicInfo.user_id == user_id).first()
    if existing_info:
        db.delete(existing_info)
        db.commit()

    # 새로운 기본정보 생성
    db_basic_info = user_model.BasicInfo(
        user_id=user_id,
        name=basic_info_data.name,
        grade_class=basic_info_data.grade_class,
        relationship_status=basic_info_data.relationship_status,
        home_phone=basic_info_data.home_phone,
        mobile_phone=basic_info_data.mobile_phone,
        address=basic_info_data.address,
    )
    db.add(db_basic_info)
    db.commit()
    db.refresh(db_basic_info)

    return basic_info_schema.BasicInfoResponse.model_validate(db_basic_info)

# 기본정보 조회 서비스
def get_basic_info(db: Session, user_id: int) -> basic_info_schema.BasicInfoResponse:
    basic_info = db.query(user_model.BasicInfo).filter(user_model.BasicInfo.user_id == user_id).first()

    if not basic_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="기본정보가 존재하지 않습니다.")

    return basic_info_schema.BasicInfoResponse.model_validate(basic_info)
