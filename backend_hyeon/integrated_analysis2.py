import os
import sys
import json
import logging
import asyncio
import re  # 명시적으로 상단에 import
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('analysis.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("school_violence_analysis")

# 환경 변수 로드
# from dotenv import load_dotenv
# load_dotenv()
import os
load_dotenv()
api_key = os.environ["ANTHROPIC_API_KEY"]

import requests
# kakao_parser.py 내용
def parse_kakao_chat(file_content):
    """ 카카오톡 대화 파일을 파싱하여 메시지 목록 반환
        [{'sender': '보낸 사람',
          'timestamp': '2025-04-29 22:13',
          'content': '메시지 내용'}, ...]
    """
    messages = []
    current_date = None
    
    # 디버깅을 위한 카운터
    date_lines = 0
    message_lines = 0
    
    # 줄별로 처리
    for line in file_content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 날짜 행 파싱 (예: "--------------- 2025년 4월 29일 화요일 ---------------")
        date_match = re.search(r'(\d{4})년\s+(\d{1,2})월\s+(\d{1,2})일', line)
        if date_match:
            year, month, day = map(int, date_match.groups())
            current_date = datetime(year, month, day)
            date_lines += 1
            logger.debug(f"날짜 인식: {year}년 {month}월 {day}일")
            continue
        
        # 메시지 행 파싱 (예: "[최대한] [오후 10:13] 야 하승현 너 눈을 왜 그렇게 떠")
        msg_match = re.match(r'^\[([^\]]+)\]\s+\[([^\]]+)\]\s+(.+)$', line)
        if msg_match and current_date:
            sender, time_str, content = msg_match.groups()
            
            # 시간 파싱 (오전/오후 처리)
            time_match = re.search(r'(\d+):(\d+)', time_str)
            if time_match:
                hour, minute = map(int, time_match.groups())
                if '오후' in time_str and hour < 12:
                    hour += 12
                elif '오전' in time_str and hour == 12:
                    hour = 0
                
                # 메시지 객체 생성
                timestamp = current_date.replace(hour=hour, minute=minute)
                messages.append({
                    'sender': sender,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M'),
                    'content': content
                })
                message_lines += 1
                
    return messages

# api_client.py 내용
# import anthropic
import json
import logging
import os
from datetime import datetime

async def call_claude_api(prompt, system_prompt=None):
    """Anthropic Claude API 호출 함수
    
    Args:
        prompt (str): 사용자 프롬프트
        system_prompt (str, optional): 시스템 프롬프트
    
    Returns:
        dict: JSON 형식의 API 응답 결과
    """
    try:
        # API 키 및 설정 
        ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
        MODEL = os.environ.get("MODEL", "claude-3-5-sonnet-20240620")  # sonnet-3.5로 변경
        MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "8192"))  # 토큰 수 8192
        TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.2"))
        
        # API 키 검증
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        
        logger.info(f"Claude API 호출 준비: 모델={MODEL}, 최대 토큰={MAX_TOKENS}, 온도={TEMPERATURE}")
        
        # 기본 시스템 프롬프트 설정
        if system_prompt is None:
            system_prompt = "당신은 학교폭력 사례 분석 전문가입니다. 카카오톡 대화를 분석하여 사이버불링 여부와 심각도를 평가하고 JSON 형식으로 응답하세요."
        
        # API 요청 헤더와 데이터
        headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        logger.info("Claude API 호출 시작")
        start_time = datetime.now()
        
        # API 요청
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Claude API 호출 완료: 소요 시간={duration:.2f}초")
        
        # 응답 처리
        if response.status_code == 200:
            result = response.json()
            content = result.get("content", [{}])[0].get("text", "")
            
            # JSON 부분만 추출
            json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
            match = re.search(json_pattern, content)
            
            if match:
                json_str = match.group(1)
                logger.info("마크다운 코드 블록에서 JSON 추출됨")
            else:
                json_str = content
                logger.info("텍스트 전체를 JSON으로 처리")
            
            # 응답이 JSON 형식인지 검증
            try:
                json_result = json.loads(json_str)
                logger.info("JSON 파싱 성공")
                return json_result
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 실패: {e}")
                return {"error": "JSON 파싱 실패", "raw_response": content}
        else:
            logger.error(f"API 호출 실패: {response.status_code} - {response.text}")
            return {"error": f"API 호출 실패: {response.status_code}", "raw_response": response.text}
    
    except Exception as e:
        logger.error(f"Claude API 호출 중 오류 발생: {e}")
        raise

# 프롬프트 생성 함수
def create_analysis_prompt(parsed_messages_list, file_names, additional_info):
    """
    분석용 프롬프트 생성 -> 여러 카카오톡 텍스트 파일을 통합하여 생성
    
    Args:
        parsed_messages_list: 각 파일의 파싱된 메시지 목록
        file_names: 파일 이름의 리스트
        additional_info: 부가 상황 정보
        
    Returns:
        str: Claude API에 전달할 프롬프트
    """
    # 파일별로 파싱하고 통합
    formatted_messages = ""
    for i, (messages, file_name) in enumerate(zip(parsed_messages_list, file_names)):
        # 파일 구분자 추가
        formatted_messages += f"\n[파일 {i+1}: {file_name}]\n"
        
        # 해당 파일의 메시지 추가
        for msg in messages:
            formatted_messages += f"[{msg['sender']}] [{msg['timestamp']}] {msg['content']}\n"
        
        formatted_messages += "\n" # 파일 간 구분
    
    # 프롬프트 템플릿 구성
    prompt = """<role>당신은 학교폭력 사례 분석에 10년 이상의 경험을 가진 교육심리학자이자 청소년 상담 전문가입니다. 특히 사이버불링 분석에 전문성을 갖추고 있으며, 청소년들의 언어 사용 패턴과 은밀한 괴롭힘 방식에 정통합니다.</role>

<task>제공된 카카오톡 대화와 추가 정보를 분석하여 날짜별 또는 주제별로 대화를 그룹화하고, 각 대화 그룹 내에서 발생한 사이버불링을 분석하세요. 분석 시 맥락을 고려하여 가해자, 피해자, 핵심 메시지를 식별하고 구체적인 사이버불링 유형과 그 이유를 자세히 설명해주세요.</task>

<school_violence_types>
1. 언어 폭력
 - 여러 사람 앞에서 상대방의 명예를 훼손하는 구체적인 말(성격, 능력, 배경 등)을 하거나 그런 내용의 글을 인터넷, SNS 등으로 퍼뜨리는 행위(명예훼손)
 ※ 내용이 진실이라고 하더라도 범죄이고, 허위인 경우에는 형법상 가중 처벌 대상이 됨.
 - 여러 사람 앞에서 모욕적인 용어(생김새에 대한 놀림, 병신, 바보 등 상대방을 비하하는 내용)를 지속적으로 말하거나 그런 내용의 글을 인터넷, SNS 등으로 퍼뜨리는 행위(모욕)
 - 신체 등에 해를 끼칠 듯한 언행("죽을래" 등)과 문자메시지 등으로 겁을 주는 행위(협박)
2. 강요
 - 속칭 빵 셔틀, 와이파이 셔틀, 과제 대행, 게임 대행, 심부름 강요 등 의사에 반하는 행동을 강요하는 행위(강제적 심부름)
 - 폭행 또는 협박으로 상대방의 권리행사를 방해하거나 해야 할 의무가 없는 일을 하게 하는 행위(강요)
 - 돈을 걷어오라고 하는 행위
3. 따돌림
 - 집단적으로 상대방을 의도적이고 반복적으로 피하는 행위
 - 싫어하는 말로 바보 취급 등 놀리기, 빈정거림, 면박주기, 겁주는 행동, 골탕 먹이기, 비웃기
 - 다른 학생들과 어울리지 못하도록 막는 행위
4. 성폭력
 - 성적인 말과 행동을 함으로써 상대방이 성적 굴욕감, 수치감을 느끼도록 하는 행위
 - 상대방의 동의 없이 성적수치심을 주는 신체 사진을 촬영하는 행위
 - 상대방에게 동의를 구하지 않고 의도적으로 성적 수치심을 주는 대화, 야한 사진, 야한 동영상 등을 전달하는 행위
5. 사이버폭력
 - 사이버 언어폭력, 사이버 명예훼손, 사이버 갈취, 사이버 스토킹, 사이버 따돌림, 사이버 영상 유포 등 정보통신기기를 이용하여 괴롭히는 행위
 - 특정인에 대해 모욕적 언사나 욕설 등을 인터넷 게시판, 채팅, 카페등에올리는행위. 특정인에 대한 저격글이 그 한 형태임
 - 특정인에 대한 허위 글이나 개인의 사생활에 관한 사실을 인터넷, SNS 등을 통해 불특정 다수에 공개하는 행위
 - 성적 수치심을 주거나 위협하는 내용, 조롱하는 글, 그림, 동영상 등을 정보통신망을 통해 유포하는 행위
 - 공포심이나 불안감을 유발하는 문자, 음향, 영상 등을 휴대폰 등 정보통신망을 통해 반복적으로 보내는 행위
 - 정보통신망을 이용하여 딥페이크 영상 등(인공지능 기술 등을 이용하여 학생의 얼굴·신체 또는 음성을 대상으로 대상자의 의사에 반하여 성적 욕망 또는 불쾌감을 유발할 수 있는 형태로 편집·합성·가공한 촬영물 또는 음성물)을 제작·배포하는 행위
</school_violence_types>

<step_1>대화 그룹 식별</step_1>
카카오톡 대화를 다음 기준으로 그룹화하세요:
- 날짜별 구분 (예: 2025년 5월 5일, 2025년 5월 8일)
- 시간적 연속성 (짧은 시간 내에 이어진 대화)
- 주제별 연관성 (같은 주제나 사건에 관한 대화)

각 대화 그룹에 대해:
- 시작 및 종료 시간 기록
- 참여자 목록 작성
- 주요 주제 또는 사건 식별

<step_2>대화 그룹별 사이버불링 분석</step_2>
각 대화 그룹 내에서 사이버불링 분석:
- 피해자와 가해자 식별
- 그룹 내 핵심 문제 메시지 추출 (5개 내외)
- 각 메시지가 어떤 유형의 사이버불링에 해당하는지 분류
- 메시지가 사이버불링에 해당하는 이유 설명
- 대화 맥락과 집단 역학 관계 분석

<step_3>종합 평가</step_3>
전체 대화를 통합적으로 분석하여:
- 전체 사이버불링 패턴 파악
- 주요 가해자 및 가해 패턴 식별
- 피해자의 반응 및 심리 상태 추정
- 괴롭힘의 시간적 변화 및 심화 과정 분석
- 전체 심각도 평가"""

    context_info=f"""
<context>
[카카오톡 대화 내용]
{formatted_messages}
[추가 정보]
피해자: {additional_info.get('victim_name', '')}
채팅방: {additional_info.get('chat_room_name', '')}
</context>
"""
    few_shot_example = """<few_shot_example>
카카오톡 대화 예시:

--------------- 2025년 2월 15일 토요일 ---------------
[김태현] [오후 8:30] 진호야 너 인스타 프사 왜 저모양이냐
[박진호] [오후 8:31] 뭐가?
[이수민] [오후 8:32] ㅋㅋㅋㅋㅋㅋ진짜 못생겼더라
[김태현] [오후 8:32] 얼굴이 너무 커서 화면에 꽉 차더라
[정민아] [오후 8:33] 사진 바꾸는 게 좋을 것 같아
[최준영] [오후 8:33] 성형해야 할 듯ㅋㅋㅋ
[박진호] [오후 8:34] 그냥 평소 모습인데...
[김태현] [오후 8:35] 그러니까 못생겼다는 거지
[이수민] [오후 8:35] 얼굴 크기 실화냐 ㅋㅋㅋ
[최준영] [오후 8:36] 그냥 돼지얼굴이라 생각하면 됨
[정민아] [오후 8:36] 너무 심한 것 같은데...
[김태현] [오후 8:37] 팩트만 말한 건데 뭐가 심해
[박진호] [오후 8:40] ...
[최준영] [오후 8:41] 삭제해 그냥ㅋㅋ
[이수민] [오후 8:41] 아 그거 인스타 말고 페북에도 올렸지 않았어?
[김태현] [오후 8:42] 맞아 둘 다 똑같이 못생김ㅋㅋㅋ
[박진호] [오후 8:43] 그만해...
[정민아] [오후 8:44] 진호야 신경쓰지마
[최준영] [오후 8:45] 울려고?ㅋㅋㅋㅋㅋ
[김태현] [오후 8:45] 울음소리가 들려ㅋㅋㅋㅋ

--------------- 2025년 2월 20일 목요일 ---------------
[김태현] [오후 4:15] 야 진호 사진 봤어?
[최준영] [오후 4:16] 뭔 사진?
[김태현] [오후 4:16] 쟤 옛날 졸업사진 찾았음
[이수민] [오후 4:17] 어디서 찾았어?
[김태현] [오후 4:17] 중학교 앨범에 있던 거
[김태현] [오후 4:17] 이모티콘
[정민아] [오후 4:18] 이건 좀...
[최준영] [오후 4:18] ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ
[이수민] [오후 4:19] 진짜 못생겼다
[김태현] [오후 4:20] 이거 너네 단톡방이랑 SNS에 다 뿌릴거임
[최준영] [오후 4:20] 개웃기겠다
[정민아] [오후 4:21] 그건 좀 심한 것 같아
[김태현] [오후 4:22] 너도 웃었잖아
[박진호] [오후 4:25] 제발 그러지 마...
[김태현] [오후 4:26] 뭐 어쩔건데? 해볼래?
[이수민] [오후 4:27] 선처 바란다면 돈 줘ㅋㅋㅋ
[최준영] [오후 4:27] 밥이라도 사든가ㅋㅋㅋ
[박진호] [오후 4:28] 그럴 필요 없잖아...
[김태현] [오후 4:29] 만원만 줘봐
[정민아] [오후 4:30] 그만해 제발
[이수민] [오후 4:30] 야 이거 올리면 진짜 웃기겠다
[김태현] [오후 4:31] 인스타에 올렸음 ㅋㅋ
[최준영] [오후 4:32] 댓글 달러 가야겠다
[박진호] [오후 4:33] 삭제해줘... 제발...
[김태현] [오후 4:34] 3만원 줘봐 그럼 생각해볼게

--------------- 2025년 2월 28일 금요일 ---------------
[정민아] [오후 7:10] 진호야 왜 학교 안 왔어?
[박진호] [오후 7:30] 몸이 안 좋아서...
[김태현] [오후 7:31] 근데 사진 올리고 댓글 개많이 달렸더라
[이수민] [오후 7:32] 우리 학교 애들 다 봤을 듯
[최준영] [오후 7:32] 다른 반 애들도 다 웃었대
[박진호] [오후 7:33] 그것 때문에 학교 못 갔어...
[정민아] [오후 7:34] 심하게 했네 너네
[김태현] [오후 7:35] 그냥 장난인데 뭘 그래
[이수민] [오후 7:35] 우리가 뭐 잘못했다고 학교를 안 와?
[최준영] [오후 7:36] 너 때문에 선생님이 우리한테 뭐라고 했잖아
[박진호] [오후 7:37] 나 신고한 거 아니야...
[김태현] [오후 7:38] 거짓말 하지마 니가 선생님한테 일렀잖아
[박진호] [오후 7:38] 아니라니까...
[이수민] [오후 7:39] 어차피 너밖에 없잖아
[정민아] [오후 7:40] 그만 괴롭혀
[최준영] [오후 7:40] 아 진짜 짜증나네
[김태현] [오후 7:41] 너 내일도 안 올 거야?
[박진호] [오후 7:42] ...
[김태현] [오후 7:42] 답장해 병신아
[박진호] [오후 7:43] 제발 그만해...
[최준영] [오후 7:44] 울지마 찐따야

분석 결과 JSON:
{{
  "analysis_result": {{
    "victim": "박진호",
    "chat_room": "우리반 단톡방",
    "time_period": {{
      "start": "2025-02-15 20:30",
      "end": "2025-02-28 19:44"
    }},
    "perpetrators": ["김태현", "이수민", "최준영"],
    "conversation_groups": [
      {{
        "id": 1,
        "topic": "SNS 프로필 사진 외모 비하",
        "start_time": "2025-02-15 20:30",
        "end_time": "2025-02-15 20:45",
        "participants": ["김태현", "박진호", "이수민", "정민아", "최준영"],
        "victim": "박진호",
        "perpetrators": ["김태현", "이수민", "최준영"],
        "key_messages": [
          {{
            "sender": "김태현",
            "timestamp": "2025-02-15 20:32",
            "content": "얼굴이 너무 커서 화면에 꽉 차더라",
            "problem": "피해자의 외모 직접적 비하 및 모욕"
          }},
          {{
            "sender": "최준영",
            "timestamp": "2025-02-15 20:33",
            "content": "성형해야 할 듯ㅋㅋㅋ",
            "problem": "외모 비하 및 모욕적 제안"
          }},
          {{
            "sender": "김태현",
            "timestamp": "2025-02-15 20:35",
            "content": "그러니까 못생겼다는 거지",
            "problem": "명시적인 외모 비하 및 모욕"
          }},
          {{
            "sender": "최준영",
            "timestamp": "2025-02-15 20:36",
            "content": "그냥 돼지얼굴이라 생각하면 됨",
            "problem": "심각한 외모 모욕 및 동물에 비유하는 심한 비하"
          }},
          {{
            "sender": "최준영",
            "timestamp": "2025-02-15 20:45",
            "content": "울려고?ㅋㅋㅋㅋㅋ",
            "problem": "피해자의 감정적 고통을 조롱"
          }}
        ],
        "bullying_types": ["외모 비하", "모욕", "언어폭력", "집단 괴롭힘"],
        "severity": 4,
        "context_description": "이 대화에서는 피해자의 SNS 프로필 사진을 대상으로 한 심각한 외모 비하와 모욕이 발생했습니다. 김태현이 처음 화제를 꺼낸 후 이수민과 최준영이 적극 가담하며 피해자의 외모를 '못생겼다', '돼지얼굴'과 같은 심한 표현으로 비하했습니다. 피해자가 '그냥 평소 모습'이라고 자신을 방어하려 했으나, 오히려 그것을 빌미로 '그러니까 못생겼다'는 식의 추가적인 모욕이 이어졌습니다. 피해자가 '그만해...'라고 불편함을 표현했음에도 가해자들은 '울려고?'라며 감정적 고통까지 조롱했습니다. 정민아만이 '너무 심한 것 같은데...'라고 말했으나 가해 행위를 적극적으로 제지하지는 않았습니다. 이는 여러 명이 한 명을 대상으로 한 명백한 집단 괴롭힘에 해당합니다."
      }},
      {{
        "id": 2,
        "topic": "졸업사진 유출 및 금전 요구",
        "start_time": "2025-02-20 16:15",
        "end_time": "2025-02-20 16:34",
        "participants": ["김태현", "박진호", "이수민", "정민아", "최준영"],
        "victim": "박진호",
        "perpetrators": ["김태현", "이수민", "최준영"],
        "key_messages": [
          {{
            "sender": "김태현",
            "timestamp": "2025-02-20 16:17",
            "content": "중학교 앨범에 있던 거",
            "problem": "피해자의 동의 없이 개인 사진 공유"
          }},
          {{
            "sender": "김태현",
            "timestamp": "2025-02-20 16:20",
            "content": "이거 너네 단톡방이랑 SNS에 다 뿌릴거임",
            "problem": "개인정보 유출 위협 및 협박"
          }},
          {{
            "sender": "이수민",
            "timestamp": "2025-02-20 16:27",
            "content": "선처 바란다면 돈 줘ㅋㅋㅋ",
            "problem": "금전 요구 및 갈취 시도"
          }},
          {{
            "sender": "김태현",
            "timestamp": "2025-02-20 16:29",
            "content": "만원만 줘봐",
            "problem": "명시적인 금전 갈취"
          }},
          {{
            "sender": "김태현",
            "timestamp": "2025-02-20 16:34",
            "content": "3만원 줘봐 그럼 생각해볼게",
            "problem": "금액 상향 및 지속적 갈취"
          }}
        ],
        "bullying_types": ["사이버 갈취", "협박", "사이버 명예훼손", "개인정보 유출"],
        "severity": 5,
        "context_description": "이 대화에서는 피해자의 중학교 졸업사진을 동의 없이 공유하고, 이를 SNS에 유포하겠다는 협박과 함께 금전을 요구하는 심각한 사이버 갈취 행위가 발생했습니다. 김태현이 피해자의 졸업사진을 공유한 후, 이를 더 널리 퍼뜨리겠다고 협박했습니다. 이수민과 최준영이 이에 적극 동조하며 '선처 바란다면 돈을 줘', '밥이라도 사든가'라는 식으로 갈취에 가담했습니다. 피해자가 '그럴 필요 없잖아...'라고 거부 의사를 표현했음에도 김태현은 금액을 구체적으로 명시하며('만원만 줘봐', '3만원 줘봐') 갈취를 시도했습니다. 실제로 피해자의 사진을 인스타그램에 허락 없이 올렸다고 언급하며 피해를 가중시켰습니다. 이는 단순한 괴롭힘을 넘어 명백한 사이버 갈취 및 협박으로, 법적으로도 처벌 가능한 심각한 사이버폭력에 해당합니다."
      }},
      {{
        "id": 3,
        "topic": "결석 관련 추가 괴롭힘",
        "start_time": "2025-02-28 19:10",
        "end_time": "2025-02-28 19:44",
        "participants": ["김태현", "박진호", "이수민", "정민아", "최준영"],
        "victim": "박진호",
        "perpetrators": ["김태현", "이수민", "최준영"],
        "key_messages": [
          {{
            "sender": "박진호",
            "timestamp": "2025-02-28 19:33",
            "content": "그것 때문에 학교 못 갔어...",
            "problem": "사이버불링으로 인한 실제 등교 거부 상황 발생"
          }},
          {{
            "sender": "이수민",
            "timestamp": "2025-02-28 19:35",
            "content": "우리가 뭐 잘못했다고 학교를 안 와?",
            "problem": "가해 행위 부정 및 책임 전가"
          }},
          {{
            "sender": "김태현",
            "timestamp": "2025-02-28 19:38",
            "content": "거짓말 하지마 니가 선생님한테 일렀잖아",
            "problem": "피해자 비난 및 역전된 피해자화"
          }},
          {{
            "sender": "김태현",
            "timestamp": "2025-02-28 19:42",
            "content": "답장해 병신아",
            "problem": "직접적인 모욕적 표현 및 언어폭력"
          }},
          {{
            "sender": "최준영",
            "timestamp": "2025-02-28 19:44",
            "content": "울지마 찐따야",
            "problem": "심각한 모욕 및 혐오 표현 사용"
          }}
        ],
        "bullying_types": ["언어폭력", "모욕", "집단 괴롭힘", "역전된 피해자화"],
        "severity": 5,
        "context_description": "이 대화에서는 이전의 사이버불링으로 인해 피해자가 학교에 등교하지 못하는 상황에서도 추가적인 괴롭힘이 이어졌습니다. 피해자가 '그것(사진 유포) 때문에 학교 못 갔어...'라고 고통을 표현했으나, 가해자들은 오히려 '우리가 뭐 잘못했다고'라며 자신들의 행동을 정당화했습니다. 김태현은 피해자가 교사에게 신고했다고 비난하며 '거짓말 하지마'라고 공격했고, 피해자가 '아니라니까...'라고 해명했음에도 '어차피 너밖에 없잖아'라며 계속 압박했습니다. 대화 후반부에는 '병신아', '찐따야'와 같은 심각한 모욕적 표현까지 사용했습니다. 이 사례는 지속적인 괴롭힘이 실제 등교 거부라는 심각한 결과로 이어졌으며, 피해자의 고통에 대한 무시와 추가적인 언어폭력이 결합된 매우 심각한 사이버불링 사례입니다."
      }}
    ],
    "patterns": {{
      "repetitive": true,
      "group_bullying": true,
      "ignored_discomfort": true,
      "escalation": true
    }},
    "overall_assessment": {{
      "is_cyberbullying": true,
      "severity_level": 5,
      "main_types": ["외모 비하", "언어폭력", "사이버 갈취", "집단 괴롭힘"],
      "key_evidence": [1, 2, 3]
    }},
    "context_info": {{
      "awareness_route": "피해자의 등교 거부 및 담임교사 상담",
      "bullying_period": "2025년 2월부터 지속",
      "relationship_context": "같은 반 친구들 사이의 지속적 괴롭힘",
      "additional_bullying": "SNS에 피해자 사진 무단 유포 및 갈취",
      "additional_context": "피해자는 내성적인 성격으로, 지속된 괴롭힘으로 인해 심리적 고통이 심각하여 등교 거부까지 이어짐"
    }}
  }}
}}
</few_shot_example>
<important>응답은 반드시 유효한 JSON 형식이어야 하며, 분석 내용과 해석은 포함하지 말고 순수한 JSON만 반환하세요.</important>"""
    
    return f"{prompt}\n{context_info}\n{few_shot_example}"

# 통합 분석 함수
async def analyze_chat_files(file_paths, additional_info):
    """
    여러 카카오톡 채팅 파일을 통합하여 분석하는 함수
    
    Args:
        file_paths: 카카오톡 텍스트 파일 경로 목록
        additional_info: 부가 상황 정보
        
    Returns:
        Dict: 분석 결과
    """
    try:
        # 모든 파일의 메시지를 통합 처리
        all_parsed_messages = []
        file_names = []
        
        for file_path in file_paths:
            # 파일 이름 저장
            file_names.append(os.path.basename(file_path))
            
            # 1. 파일 읽기
            logger.info(f"파일 '{file_path}' 읽기 시작")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"파일 읽기 완료: {len(content)} 바이트")
            
            # 2. 파일 파싱
            logger.info(f"파일 '{file_path}' 메시지 파싱 시작")
            parsed_messages = parse_kakao_chat(content)
            logger.info(f"파싱 완료: {len(parsed_messages)}개 메시지")
            
            all_parsed_messages.append(parsed_messages)
        
        # 3. 프롬프트 생성 (파일별로 메시지 유지)
        logger.info("통합 분석 프롬프트 생성")
        prompt = create_analysis_prompt(all_parsed_messages, file_names, additional_info)
        logger.info(f"프롬프트 생성 완료: {len(prompt)} 문자")
        
        # 4. API 호출
        logger.info("Claude API 호출")
        result = await call_claude_api(prompt)
        
        # 5. 결과 후처리
        if isinstance(result, dict) and "error" not in result:
            logger.info("분석 성공")
            
            # 메타데이터 추가
            analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            result["analysis_id"] = analysis_id
            result["created_at"] = datetime.now().isoformat()
            result["file_names"] = file_names
            
            # 결과 저장
            output_dir = "analysis_results"
            os.makedirs(output_dir, exist_ok=True)
            output_file = sys.argv[3]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"분석 결과가 '{output_file}'에 저장되었습니다.")
        else:
            logger.error("분석 실패")
            if isinstance(result, dict) and "error" in result:
                logger.error(f"오류: {result['error']}")
        
        return result
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}
    

# 단일 파일 분석 함수 (이 함수를 추가하여 메인에서 호출할 수 있게 함)
async def analyze_chat_file(file_path, additional_info):
    """
    단일 카카오톡 채팅 파일을 분석하는 함수
    
    Args:
        file_path: 카카오톡 텍스트 파일 경로
        additional_info: 부가 상황 정보
        
    Returns:
        Dict: 분석 결과
    """
    try:
        # 1. 파일 읽기
        logger.info(f"파일 '{file_path}' 읽기 시작")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"파일 읽기 완료: {len(content)} 바이트")
        
        # 2. 파일 파싱
        logger.info("카카오톡 메시지 파싱 시작")
        parsed_messages = parse_kakao_chat(content)
        logger.info(f"파싱 완료: {len(parsed_messages)}개 메시지")
        
        # 3. 단일 파일 형태로 변환하여 통합 분석 함수에 전달
        return await analyze_chat_files([file_path], additional_info)
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e)}

# 메인 함수
async def main():
    """메인 함수"""
    print("메인 함수 실행 중...")
    
    # 명령행 인자 처리
    if len(sys.argv) > 1:
        # 특정 파일 경로가 제공된 경우
        file_paths = sys.argv[1:]
    else:
        # 사용자 입력 요청
        file_input = input("카카오톡 텍스트 파일 경로를 입력하세요 (여러 파일은 쉼표로 구분): ")
        file_paths = [path.strip() for path in file_input.split(',')]
    
    # 파일 존재 확인
    valid_file_paths = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            valid_file_paths.append(file_path)
        else:
            logger.error(f"파일이 존재하지 않습니다: {file_path}")
    
    if not valid_file_paths:
        logger.error("유효한 파일이 없습니다.")
        return
    
    logger.info(f"처리할 파일 목록: {', '.join(valid_file_paths)}")
    
    # 추가 정보 로드
    try:
        additional_info_path = input("부가 상황 정보 JSON 파일 경로를 입력하세요 (없으면 Enter): ")
        if additional_info_path and os.path.exists(additional_info_path):
            with open(additional_info_path, 'r', encoding='utf-8') as f:
                additional_info = json.load(f)
            logger.info(f"부가 상황 정보를 '{additional_info_path}'에서 로드했습니다.")
        else:
            # 기본 부가 정보
            additional_info = {
                "victim_name": "최서현",
                "chat_room_name": "3-2반 단체톡방",
                "awareness_route": "본인이 직접 피해를 경험함",
                "bullying_period": "반복적으로 발생 (약 4개월간)",
                "relationship_context": "같은 반 친구들",
                "additional_bullying": "학교에서 직접적인 괴롭힘도 있었음",
                "additional_context": "이전에도 비슷한 언어폭력이 있었으나 이번처럼 심각하지는 않았음"
            }
            logger.info("기본 부가 상황 정보를 사용합니다.")
    except Exception as e:
        logger.error(f"부가 정보 로드 중 오류 발생: {e}")
        return
    
    # 분석 실행
    result = None
    if len(valid_file_paths) == 1:
        # 단일 파일 분석
        logger.info("===== 단일 파일 분석 시작 =====")
        result = await analyze_chat_file(valid_file_paths[0], additional_info)
    else:
        # 여러 파일 통합 분석
        logger.info("===== 다중 파일 통합 분석 시작 =====")
        result = await analyze_chat_files(valid_file_paths, additional_info)
    
    # 결과 출력
    if isinstance(result, dict) and "error" not in result:
        logger.info("===== 분석 성공 =====")
        
        # 간략한 결과 출력
        if "analysis_result" in result:
            analysis = result["analysis_result"]
            logger.info(f"피해자: {analysis.get('victim', 'N/A')}")
            logger.info(f"가해자: {', '.join(analysis.get('perpetrators', ['N/A']))}")
            logger.info(f"사이버불링 여부: {analysis.get('overall_assessment', {}).get('is_cyberbullying', 'N/A')}")
            logger.info(f"심각도: {analysis.get('overall_assessment', {}).get('severity_level', 'N/A')}/5")
            
            main_types = analysis.get('overall_assessment', {}).get('main_types', [])
            if main_types:
                logger.info(f"주요 불링 유형: {', '.join(main_types)}")
    else:
        logger.error("===== 분석 실패 =====")
        logger.error(f"오류: {result.get('error', '알 수 없는 오류')}")

if __name__ == "__main__":
    print("스크립트 시작")
    # .env 파일 로드
    # load_dotenv()
    
    # API 키 확인
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("오류: ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        sys.exit(1)
    
    print("비동기 메인 함수 실행")
    # 비동기 메인 함수 실행
    asyncio.run(main())
    print("스크립트 종료")