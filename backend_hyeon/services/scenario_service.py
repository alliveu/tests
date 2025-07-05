# services/scenario_service.py
# Cynario 시나리오 생성 서비스 로직 (문서 기반)

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import scenario as scenario_model
from models import user as user_model
from schemas import scenario as scenario_schema

def create_scenario(
    db: Session,
    user_id: int,
    scenario_data: scenario_schema.ScenarioCreateRequest
) -> scenario_schema.ScenarioResponse:
    """
    시나리오 생성:
    - analysis_id, basic_info_id, additional_prompt 기반
    - Claude 연동 부분은 아직 제외 (나중에 연결)
    """

    # 기본정보 존재 여부 확인
    basic_info = db.query(user_model.BasicInfo).filter(user_model.BasicInfo.id == scenario_data.basic_info_id).first()
    if not basic_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="기본정보를 찾을 수 없습니다.")

    # analysis_id 존재 여부 확인 (생략 가능, 현재는 패스)

    # Claude 연동 없이 샘플 시나리오 JSON 생성
    scenario_json = {
        "overview": "샘플 시나리오 개요",
        "who": basic_info.name,
        "when": "2025-07-02",
        "where": basic_info.address or "알 수 없음",
        "what": "샘플 사건 내용",
        "how": "샘플 사건 진행 방식",
        "why": "샘플 사건 발생 이유"
    }

    db_scenario = scenario_model.Scenario(
        user_id=user_id,
        analysis_id=scenario_data.analysis_id,
        basic_info_id=scenario_data.basic_info_id,
        scenario_result=scenario_json
    )

    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)

    return scenario_schema.ScenarioResponse.model_validate(db_scenario)

# services/scenario_service.py (추가)

from typing import List

def get_scenarios(db: Session, user_id: int) -> List[scenario_schema.ScenarioResponse]:
    scenario_list = db.query(scenario_model.Scenario).filter(scenario_model.Scenario.user_id == user_id).all()
    return [scenario_schema.ScenarioResponse.model_validate(s) for s in scenario_list]


# services/scenario_service.py (추가)

def update_scenario(
    db: Session,
    scenario_id: int,
    user_id: int,
    update_data: scenario_schema.ScenarioUpdateRequest
) -> scenario_schema.ScenarioResponse:
    scenario = db.query(scenario_model.Scenario).filter(
        scenario_model.Scenario.id == scenario_id,
        scenario_model.Scenario.user_id == user_id
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="시나리오를 찾을 수 없습니다.")

    # 수정 가능한 필드만 업데이트
    if update_data.analysis_id is not None:
        scenario.analysis_id = update_data.analysis_id
    if update_data.basic_info_id is not None:
        scenario.basic_info_id = update_data.basic_info_id
    if update_data.additional_prompt is not None:
        scenario.additional_prompt = update_data.additional_prompt
    if update_data.scenario_result is not None:
        scenario.scenario_result = update_data.scenario_result

    db.commit()
    db.refresh(scenario)

    return scenario_schema.ScenarioResponse.model_validate(scenario)

# services/scenario_service.py (추가)

def delete_scenario(
    db: Session,
    scenario_id: int,
    user_id: int
) -> None:
    scenario = db.query(scenario_model.Scenario).filter(
        scenario_model.Scenario.id == scenario_id,
        scenario_model.Scenario.user_id == user_id
    ).first()

    if not scenario:
        raise HTTPException(status_code=404, detail="시나리오를 찾을 수 없습니다.")

    db.delete(scenario)
    db.commit()
