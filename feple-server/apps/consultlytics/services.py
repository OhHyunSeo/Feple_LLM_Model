import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import datetime
import django
from django.conf import settings
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist

# 환경 변수 로드
load_dotenv()

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.consultlytics.models import Consulting
from .utils import validate_api_key, safe_get_attribute

# 로거 설정
logger = logging.getLogger(__name__)

# Google API 설정 및 유효성 검사
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not validate_api_key():
    logger.error("Google API 키 설정에 문제가 있습니다.")
    raise ValueError("Google API 키가 올바르게 설정되지 않았습니다.")

genai.configure(api_key=GOOGLE_API_KEY)

# Gemini 모델 초기화 (에러 처리 포함)
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.2,
        google_api_key=GOOGLE_API_KEY,
        convert_system_message_to_human=True
    )
    logger.info("Gemini 모델이 성공적으로 초기화되었습니다.")
except Exception as e:
    logger.error(f"Gemini 모델 초기화 실패: {str(e)}")
    llm = None

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

def analyze_consultation(call_id: str) -> Optional[Dict[str, Any]]:
    """
    상담 분석을 수행하고 결과를 반환합니다.
    
    Args:
        call_id: 분석할 상담의 고유 ID
        
    Returns:
        분석 결과 딕셔너리 또는 None (오류 발생 시)
    """
    if not llm:
        logger.error("Gemini 모델이 초기화되지 않았습니다.")
        return None
        
    try:
        # 상담 데이터 조회
        try:
            row = Consulting.objects.get(call_id=call_id)
        except ObjectDoesNotExist:
            logger.error(f"call_id '{call_id}'에 해당하는 상담 데이터를 찾을 수 없습니다.")
            return None
        except Exception as e:
            logger.error(f"데이터베이스 조회 중 오류 발생: {str(e)}")
            return None

        logger.info(f"상담 데이터 분석 시작: {call_id}")

        # 감정 점수 계산 (안전한 속성 접근)
        agent_star = 3  # 기본값
        for s in range(1, 6):
            if safe_get_attribute(row, f"emo_{s}_star_score", 0) > 0:
                agent_star = s
                break
                
        cust_star = 3  # 기본값
        for s in range(1, 6):
            if safe_get_attribute(row, f"고객_emo_{s}_star_score", 0) > 0:
                cust_star = s
                break

        agent_emotion = score_emotion(agent_star)
        cust_emotion = score_emotion(cust_star)

        # 효율성 점수 (안전한 속성 접근)
        silence = safe_get_attribute(row, "silence", 0)
        csr_speech_count = safe_get_attribute(row, "csr_speech_count", 0)
        customer_speech_count = safe_get_attribute(row, "customer_speech_count", 0)
        eff = score_efficiency(silence, csr_speech_count, customer_speech_count)

        # 메뉴얼 준수율 (안전한 속성 접근)
        if cust_star <= 2:
            manual_ratio = score_manual(
                safe_get_attribute(row, "alternative_solution_count", 0),
                safe_get_attribute(row, "apology_ratio", 0.0),
                safe_get_attribute(row, "positive_word_ratio", 0.0),
                safe_get_attribute(row, "euphonious_word_ratio", 0.0),
                safe_get_attribute(row, "empathy_expression_ratio", 0.0)
            )
        else:
            manual_ratio = 1.0

        # 최종 점수 계산
        profanity_penalty = -20 if safe_get_attribute(row, "Profane", False) else 0
        final_score = int((agent_emotion + cust_emotion + eff + manual_ratio*100)/4 + profanity_penalty)
        final_score = max(0, min(100, final_score))

        # 모델 인스턴스를 딕셔너리로 변환 (안전한 변환)
        try:
            row_dict = model_to_dict(row)
            for key, value in row_dict.items():
                if isinstance(value, datetime.datetime):
                    row_dict[key] = value.isoformat()
        except Exception as e:
            logger.error(f"모델 데이터 변환 중 오류: {str(e)}")
            return None

        # Gemini API를 통한 분석
        try:
            prompt_input = ANALYSIS_PROMPT.format(
                row=json.dumps(row_dict, ensure_ascii=False),
                agent_emotion_score=agent_emotion,
                customer_emotion_score=cust_emotion,
                efficiency_score=eff,
                manual_ratio=round(manual_ratio, 2),
                final_score=final_score
            )
            
            response = llm.invoke(prompt_input)
            logger.info(f"LLM 응답 수신: {call_id}")
            
        except Exception as e:
            logger.error(f"LLM API 호출 중 오류 발생: {str(e)}")
            return None
        
        # 응답 파싱
        try:
            result = _parse_llm_response(response.content)
            if not result:
                logger.error(f"LLM 응답 파싱 실패: {call_id}")
                return None
                
        except Exception as e:
            logger.error(f"응답 파싱 중 오류: {str(e)}")
            return None
            
        # 결과 업데이트
        try:
            row.strength = result.get("상담자 강점", "")
            row.weakness = result.get("상담자 단점", "")
            row.improvement = result.get("개선점", "")
            row.manual_compliance_ratio = manual_ratio
            row.score = final_score
            row.save()
            
            logger.info(f"분석 결과 저장 완료: {call_id}")
            
        except Exception as e:
            logger.error(f"분석 결과 저장 중 오류: {str(e)}")
            # 저장 실패해도 분석 결과는 반환

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
        logger.error(f"상담 분석 중 예상치 못한 오류 발생 ({call_id}): {str(e)}")
        return None


def _parse_llm_response(response_content: str) -> Optional[Dict[str, Any]]:
    """
    LLM 응답을 파싱하여 구조화된 결과를 반환합니다.
    
    Args:
        response_content: LLM의 원본 응답 텍스트
        
    Returns:
        파싱된 결과 딕셔너리 또는 None
    """
    try:
        lines = response_content.strip().split('\n')
        result = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('1.') or line.startswith('평가점수'):
                # 점수 추출
                score_text = line.split('.', 1)[1].strip() if '.' in line else line.split(':', 1)[1].strip()
                try:
                    result['평가점수'] = int(''.join(filter(str.isdigit, score_text)))
                except (ValueError, IndexError):
                    result['평가점수'] = 0
                    
            elif line.startswith('2.') or line.startswith('상담자 강점'):
                result['상담자 강점'] = _extract_content(line)
                
            elif line.startswith('3.') or line.startswith('상담자 단점'):
                result['상담자 단점'] = _extract_content(line)
                
            elif line.startswith('4.') or line.startswith('개선점'):
                result['개선점'] = _extract_content(line)
                
            elif line.startswith('5.') or line.startswith('코칭 멘트'):
                result['코칭 멘트'] = _extract_content(line)
        
        # 필수 키 확인
        required_keys = ["상담자 강점", "상담자 단점", "개선점", "평가점수", "코칭 멘트"]
        if not all(k in result for k in required_keys):
            missing_keys = [k for k in required_keys if k not in result]
            logger.warning(f"필수 키가 누락되었습니다: {missing_keys}")
            
            # 누락된 키에 대해 기본값 설정
            for key in missing_keys:
                if key == "평가점수":
                    result[key] = 0
                else:
                    result[key] = "분석 결과 없음"
            
        return result
        
    except Exception as e:
        logger.error(f"LLM 응답 파싱 중 오류: {str(e)}")
        return None


def _extract_content(line: str) -> str:
    """라인에서 내용을 추출합니다."""
    try:
        if ':' in line:
            return line.split(':', 1)[1].strip()
        elif '.' in line:
            return line.split('.', 1)[1].strip()
        else:
            return line.strip()
    except (IndexError, AttributeError):
        return "내용 추출 실패" 