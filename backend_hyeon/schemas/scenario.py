# schemas/scenario.py
# Cynario 시나리오 요청/응답 스키마 (문서 기반)

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 시나리오 생성 요청용
class ScenarioCreateRequest(BaseModel):
    analysis_id: int
    basic_info_id: int
    additional_prompt: Optional[str] = None

# 시나리오 응답용
class ScenarioResponse(BaseModel):
    id: int
    user_id: int
    analysis_id: int
    basic_info_id: int
    scenario_result: dict
    created_at: datetime

    class Config:
        from_attributes = True  # ORM 객체 → Pydantic 변환 허용

# schemas/scenario.py (추가)

from typing import List

class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioResponse]

# schemas/scenario.py (추가)

from typing import Optional

class ScenarioUpdateRequest(BaseModel):
    analysis_id: Optional[int] = None
    basic_info_id: Optional[int] = None
    additional_prompt: Optional[str] = None
    scenario_result: Optional[dict] = None
