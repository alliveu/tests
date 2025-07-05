# routers/document_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import document as document_schema
from services import document_service

router = APIRouter(
    prefix="/api/document",
    tags=["Document"]
)

@router.post("/create3", response_model=document_schema.DocumentResponse)
@router.post("/create9", response_model=document_schema.DocumentResponse)
@router.post("/create10", response_model=document_schema.DocumentResponse)
@router.post("/create24", response_model=document_schema.DocumentResponse)
def create_document(
    document_data: document_schema.DocumentCreateRequest,
    user_id: int = 1,  # JWT 연동 시 교체
    db: Session = Depends(get_db)
):
    """
    문서 생성 API
    """
    document = document_service.create_document(db, user_id, document_data)
    return document

# routers/document_router.py (추가)

@router.get("/archive/documents", response_model=document_schema.DocumentListResponse)
def get_document_list(
    user_id: int = 1,  # JWT 연동 시 교체 예정
    db: Session = Depends(get_db)
):
    """
    문서 목록 조회 API
    """
    documents = document_service.get_documents(db, user_id)
    return {"documents": documents}

# routers/document_router.py (추가)

@router.patch("/{document_id}", response_model=document_schema.DocumentResponse)
def update_document(
    document_id: int,
    update_data: document_schema.DocumentUpdateRequest,
    user_id: int = 1,  # JWT 연동 시 교체 예정
    db: Session = Depends(get_db)
):
    """
    문서 수정 API
    """
    document = document_service.update_document(db, document_id, user_id, update_data)
    return document

# routers/document_router.py (추가)

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    user_id: int = 1,  # JWT 연동 시 교체 예정
    db: Session = Depends(get_db)
):
    """
    문서 삭제 API
    """
    document_service.delete_document(db, document_id, user_id)
    return {"success": True, "message": "문서가 삭제되었습니다."}
