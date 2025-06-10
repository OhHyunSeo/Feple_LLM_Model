import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import datetime
import django
from django.conf import settings
from django.forms.models import model_to_dict

# 환경 변수 로드
load_dotenv()

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.consultlytics.models import Consulting

# Google API 설정
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Gemini 모델 초기화
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.2,
    google_api_key=GOOGLE_API_KEY,
    convert_system_message_to_human=True
)

def score_emotion(star: int) -> int:
    """Return 100/80/60/40/20 based on 5→1 star."""
    return max(20, (6-star)*20)

def score_efficiency(silence: int, csr: int, cust: int) -> int:
    penalty = (silence/500) + abs(csr-cust)*2
    return max(0, 100 - min(100, int(penalty)))

def score_manual(alt: int, apology: float, pos: float, eupho: float, empathy: float) -> float:
    criteria = [alt>0, apology>0, pos>0.1, eupho>0.05, empathy>0.1]
    return sum(criteria)/len(criteria)

ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["row", "agent_emotion_score", "customer_emotion_score",
                    "efficiency_score", "manual_ratio", "final_score"],
    template="""
당신은 콜센터 전문 평가 AI입니다. 아래 상담 데이터(JSON)와 계산된 중간 점수를 참고하여 분석해주세요.

[상담 데이터(JSON)]
{row}

[중간 스코어]
- 상담사 감정 점수: {agent_emotion_score}
- 고객 감정 점수: {customer_emotion_score}
- 효율성 점수: {efficiency_score}
- 매뉴얼 준수율: {manual_ratio}
- 최종 점수: {final_score}

다음 5가지 항목에 대해 분석해주세요:
1. 평가점수 (100점 만점, 숫자만)
2. 상담자 강점
3. 상담자 단점
4. 개선점
5. 코칭 멘트 (실제 상담자에게 전달할 수 있는 구체적이고 실질적인 코칭 메시지, 한 문장)

각 항목은 한 줄로 작성해주세요.
"""
)

def analyze_consultation(call_id: str) -> Dict[str, Any]:
    """상담 분석을 수행하고 결과를 반환합니다."""
    try:
        row = Consulting.objects.get(call_id=call_id)
        if not row:
            raise ValueError("call_id not found")

        # 감정 점수 계산
        agent_star = next((s for s in range(1, 6) if getattr(row, f"emo_{s}_star_score")), 3)
        cust_star = next((s for s in range(1, 6) if getattr(row, f"고객_emo_{s}_star_score")), 3)
        agent_emotion = score_emotion(agent_star)
        cust_emotion = score_emotion(cust_star)

        # 효율성 점수
        eff = score_efficiency(row.silence, row.csr_speech_count, row.customer_speech_count)

        # 메뉴얼 준수율
        manual_ratio = score_manual(
            row.alternative_solution_count,
            row.apology_ratio,
            row.positive_word_ratio,
            row.euphonious_word_ratio,
            row.empathy_expression_ratio
        ) if cust_star <= 2 else 1.0

        # 최종 점수 계산
        profanity_penalty = -20 if getattr(row, "Profane", False) else 0
        final_score = int((agent_emotion + cust_emotion + eff + manual_ratio*100)/4 + profanity_penalty)
        final_score = max(0, min(100, final_score))

        # 모델 인스턴스를 딕셔너리로 변환
        row_dict = model_to_dict(row)
        for key, value in row_dict.items():
            if isinstance(value, datetime.datetime):
                row_dict[key] = value.isoformat()

        # Gemini API를 통한 분석
        prompt_input = ANALYSIS_PROMPT.format(
            row=json.dumps(row_dict, ensure_ascii=False),
            agent_emotion_score=agent_emotion,
            customer_emotion_score=cust_emotion,
            efficiency_score=eff,
            manual_ratio=round(manual_ratio, 2),
            final_score=final_score
        )
        
        response = llm.invoke(prompt_input)
        print(f"\nLLM 원본 응답:\n{response.content}\n")
        
        # 응답을 줄 단위로 분리하여 파싱
        lines = response.content.strip().split('\n')
        result = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('1.') or line.startswith('평가점수'):
                # "1." 또는 "평가점수" 접두어를 제거하고, 숫자만 추출
                score_text = line.split('.', 1)[1].strip() if '.' in line else line.split(':', 1)[1].strip()
                result['평가점수'] = int(''.join(filter(str.isdigit, score_text)))
            elif line.startswith('2.') or line.startswith('상담자 강점'):
                result['상담자 강점'] = line.split(':', 1)[1].strip() if ':' in line else line.split('.', 1)[1].strip()
            elif line.startswith('3.') or line.startswith('상담자 단점'):
                result['상담자 단점'] = line.split(':', 1)[1].strip() if ':' in line else line.split('.', 1)[1].strip()
            elif line.startswith('4.') or line.startswith('개선점'):
                result['개선점'] = line.split(':', 1)[1].strip() if ':' in line else line.split('.', 1)[1].strip()
            elif line.startswith('5.') or line.startswith('코칭 멘트'):
                result['코칭 멘트'] = line.split(':', 1)[1].strip() if ':' in line else line.split('.', 1)[1].strip()
        
        if not all(k in result for k in ["상담자 강점", "상담자 단점", "개선점", "평가점수", "코칭 멘트"]):
            raise ValueError("필수 키가 누락되었습니다")
            
        # 결과 업데이트
        row.strength = result["상담자 강점"]
        row.weakness = result["상담자 단점"]
        row.improvement = result["개선점"]
        row.manual_compliance_ratio = manual_ratio
        row.score = final_score
        row.save()

        return {
            "call_id": call_id,
            "analysis": result,
            "scores": {
                "agent_emotion": agent_emotion,
                "customer_emotion": cust_emotion,
                "efficiency": eff,
                "manual_compliance": manual_ratio,
                "final_score": final_score
            }
        }
    except Exception as e:
        print(f"LLM 분석 중 오류 발생: {str(e)}")
        if 'response' in locals():
            print(f"LLM 응답: {response.content}")
        return None 