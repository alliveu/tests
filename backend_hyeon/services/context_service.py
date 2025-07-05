# services/context_service.py
# 카카오톡 txt 업로드 분석 서비스 로직

import logging
logger = logging.getLogger("uvicorn")
logger.info("[FastAPI] 0")

# logging.basicConfig(level=logging.INFO)
# logging.info("[FastAPI] integrated_analysis2.py 호출 직전: 분석 프로세스 시작 (logging)")


from sqlalchemy.orm import Session
from fastapi import UploadFile
from models import analysis as analysis_model
from schemas import context as context_schema

import json

def parse_kakao_txt(file_content: str) -> dict:
    """
    카카오톡 txt 파일 파싱 (샘플 버전)
    - 실제로는 메시지/사용자/시간/본문 추출
    """
    lines = file_content.splitlines()
    messages = []

    for line in lines:
        if line.strip():
            messages.append({"message": line.strip()})

    return {"messages": messages}

import subprocess
import os
import uuid
from datetime import datetime




from sqlalchemy.orm import Session
from fastapi import UploadFile
from models import analysis as analysis_model
from schemas import context as context_schema

import json
import os
import uuid
from datetime import datetime

# Gemini API 호출 함수 추가
def call_gemini_api_from_text(kakao_text: str, prompt_info: dict) -> dict:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # 프롬프트 구성
    prompt = f"""
아래는 카카오톡 대화 내용입니다:
{kakao_text}

아래는 추가 정보입니다:
{json.dumps(prompt_info, ensure_ascii=False)}

위의 데이터를 기반으로 사이버불링 여부를 JSON으로 분석해줘.
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON returned by Gemini API",
            "raw_text": response.text
        }

import subprocess
import json
import os
import uuid
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models import analysis as analysis_model
from schemas import context as context_schema

def upload_and_analyze_kakao_chat(
    db: Session,
    user_id: int,
    file: UploadFile,
    prompt_info: str
) -> context_schema.UploadResponse:
    # 📌 업로드 경로 준비
    upload_dir = f"./uploads/{datetime.now().strftime('%Y-%m-%d')}"
    os.makedirs(upload_dir, exist_ok=True)

    txt_path = os.path.join(upload_dir, f"{uuid.uuid4()}.txt")
    json_path = os.path.join(upload_dir, f"{uuid.uuid4()}.json")
    out_path = os.path.join(upload_dir, f"{uuid.uuid4()}_output.json")

    # 📌 파일 저장
    with open(txt_path, "wb") as f:
        f.write(file.file.read())

    # 📌 prompt_info JSON 저장
    try:
        prompt_info_dict = json.loads(prompt_info) if prompt_info else {}
    except json.JSONDecodeError:
        prompt_info_dict = {"raw_prompt_info": prompt_info}

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(prompt_info_dict, f, ensure_ascii=False, indent=2)

    # ✅ 여기에 로그 유지
    logger.info("[FastAPI] 1")

    # 📌 integrated_analysis2.py subprocess 호출
    result = subprocess.run(
        [
            "python", "integrated_analysis2.py",
            txt_path,
            json_path,
            out_path
        ],
        text=True,
        encoding="utf-8"
    )

    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise Exception(f"integrated_analysis2.py 실행 실패:\n{result.stderr}")

    # 📌 결과 JSON 로드
    with open(out_path, "r", encoding="utf-8") as f:
        analysis_result = json.load(f)

    # 📌 DB 저장
    db_analysis = analysis_model.Analysis(
        user_id=user_id,
        file_name=file.filename,
        analysis_result=analysis_result
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    return context_schema.UploadResponse(
        success=True,
        message="integrated_analysis2.py 기반 카카오톡 분석 완료",
        analysis_id=db_analysis.id
    )

