# models/scenario.py
# Cynario 시나리오 DB 모델 (문서 기반)

from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from models import user  # User 모델 인식 위해 필수
from models import scenario

from database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_id = Column(Integer, nullable=False)
    basic_info_id = Column(Integer, nullable=False)
    scenario_result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계 설정 (선택)
    user = relationship("User", backref="scenarios")
