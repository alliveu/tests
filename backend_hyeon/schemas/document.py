# schemas/document.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 문서 생성 요청
class DocumentCreateRequest(BaseModel):
    scenario_id: int
    basic_info_id: int
    additional_prompt: Optional[str] = None

# 문서 응답
class DocumentResponse(BaseModel):
    id: int
    user_id: int
    scenario_id: int
    basic_info_id: int
    document_result: dict
    created_at: datetime

    class Config:
        from_attributes = True

# schemas/document.py (추가)

from typing import List

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]

# schemas/document.py (추가)

class DocumentUpdateRequest(BaseModel):
    scenario_id: Optional[int] = None
    basic_info_id: Optional[int] = None
    document_result: Optional[dict] = None
