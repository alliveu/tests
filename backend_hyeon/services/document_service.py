# services/document_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import document as document_model
from schemas import document as document_schema

def create_document(
    db: Session,
    user_id: int,
    document_data: document_schema.DocumentCreateRequest
) -> document_schema.DocumentResponse:

    # 샘플 문서 JSON (추후 Claude 연동)
    document_json = {
        "title": "샘플 문서 제목",
        "content": "샘플 문서 내용입니다.",
        "date": "2025-07-02"
    }

    db_document = document_model.Document(
        user_id=user_id,
        scenario_id=document_data.scenario_id,
        basic_info_id=document_data.basic_info_id,
        document_result=document_json
    )

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return document_schema.DocumentResponse.model_validate(db_document)

# services/document_service.py (추가)

from typing import List

def get_documents(db: Session, user_id: int) -> List[document_schema.DocumentResponse]:
    document_list = db.query(document_model.Document).filter(document_model.Document.user_id == user_id).all()
    return [document_schema.DocumentResponse.model_validate(doc) for doc in document_list]

# services/document_service.py (추가)

def update_document(
    db: Session,
    document_id: int,
    user_id: int,
    update_data: document_schema.DocumentUpdateRequest
) -> document_schema.DocumentResponse:
    document = db.query(document_model.Document).filter(
        document_model.Document.id == document_id,
        document_model.Document.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    # 수정 가능한 필드만 업데이트
    if update_data.scenario_id is not None:
        document.scenario_id = update_data.scenario_id
    if update_data.basic_info_id is not None:
        document.basic_info_id = update_data.basic_info_id
    if update_data.document_result is not None:
        document.document_result = update_data.document_result

    db.commit()
    db.refresh(document)

    return document_schema.DocumentResponse.model_validate(document)

# services/document_service.py (추가)

def delete_document(
    db: Session,
    document_id: int,
    user_id: int
) -> None:
    document = db.query(document_model.Document).filter(
        document_model.Document.id == document_id,
        document_model.Document.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    db.delete(document)
    db.commit()
