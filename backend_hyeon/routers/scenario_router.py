# routers/scenario_router.py
# Cynario 시나리오 생성 라우터 (문서 기반)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import scenario as scenario_schema
from services import scenario_service

router = APIRouter(
    prefix="/api/scenario",
    tags=["Scenario"]
)

# (임시) JWT 미사용, user_id 하드코딩
@router.post("/create", response_model=scenario_schema.ScenarioResponse)
def create_scenario(
    scenario_data: scenario_schema.ScenarioCreateRequest,
    user_id: int = 1,  # 추후 JWT로 교체 예정
    db: Session = Depends(get_db)
):
    """
    시나리오 생성 API
    - analysis_id, basic_info_id 기반 시나리오 생성
    - Claude 연동 없이 샘플 JSON으로 저장
    """
    scenario = scenario_service.create_scenario(db, user_id, scenario_data)
    return scenario

# routers/scenario_router.py (추가)

@router.get("/archive/scenarios", response_model=scenario_schema.ScenarioListResponse)
def get_scenario_list(
    user_id: int = 1,  # JWT 연동 시 토큰에서 추출 예정
    db: Session = Depends(get_db)
):
    """
    시나리오 목록 조회 API
    """
    scenario_list = scenario_service.get_scenarios(db, user_id)
    return {"scenarios": scenario_list}

# routers/scenario_router.py (추가)

@router.patch("/{scenario_id}", response_model=scenario_schema.ScenarioResponse)
def update_scenario(
    scenario_id: int,
    update_data: scenario_schema.ScenarioUpdateRequest,
    user_id: int = 1,  # JWT 연동 시 교체 예정
    db: Session = Depends(get_db)
):
    """
    시나리오 수정 API
    """
    scenario = scenario_service.update_scenario(db, scenario_id, user_id, update_data)
    return scenario

# routers/scenario_router.py (추가)

@router.delete("/{scenario_id}")
def delete_scenario(
    scenario_id: int,
    user_id: int = 1,  # JWT 연동 시 교체 예정
    db: Session = Depends(get_db)
):
    """
    시나리오 삭제 API
    """
    scenario_service.delete_scenario(db, scenario_id, user_id)
    return {"success": True, "message": "시나리오가 삭제되었습니다."}
