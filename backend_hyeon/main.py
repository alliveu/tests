from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import user  # User 모델 인식 위해 필수
from models import scenario
from models import document
from database import Base, engine
from routers import user_router
from models import analysis



app = FastAPI(
    title="Cynario API",
    description="사이버불링 대응 및 자동 문서 생성 API",
    version="1.0.0",
    debug=True
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 테이블 자동 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(user_router.router)

@app.get("/")
async def root():
    return {"message": "Cynario FastAPI 백엔드 작동 중"}

from routers import basic_info_router

app.include_router(basic_info_router.router)

from routers import scenario_router

app.include_router(scenario_router.router)

from routers import document_router

app.include_router(document_router.router)

from routers import context_router

app.include_router(context_router.router)
