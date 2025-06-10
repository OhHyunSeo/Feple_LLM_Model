import os
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import django
from django.conf import settings
from django.forms.models import model_to_dict
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.consultlytics.models import Consulting
from apps.consultlytics.services import analyze_consultation
from apps.consultlytics.utils import (
    get_all_consulting_data,
    get_db_connection_info,
    validate_api_key
)

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logger = logging.getLogger(__name__)

def save_analysis_results_to_db(consulting_data: Consulting, analysis_result: Dict[str, Any]) -> bool:
    """
    분석 결과를 별도 데이터베이스에 저장합니다.
    
    Args:
        consulting_data: 상담 데이터 객체
        analysis_result: 분석 결과 딕셔너리
        
    Returns:
        저장 성공 여부
    """
    try:
        # 데이터베이스 연결 정보 가져오기
        db_info = get_db_connection_info()
        analysis_db_uri = db_info["analysis_db_uri"]
        
        engine = create_engine(analysis_db_uri)
        
        # 분석 결과에서 필요한 데이터 추출
        analysis_data = analysis_result.get("analysis", {})
        scores = analysis_result.get("scores", {})
        
        # 분석 결과 저장
        with engine.begin() as conn:
            sql = text("""
                INSERT INTO analysis_results (
                    call_id, evaluation_score, strengths, weaknesses,
                    improvements, coaching_message, agent_emotion_score,
                    customer_emotion_score, efficiency_score, 
                    manual_compliance_ratio, final_score, created_at
                ) VALUES (
                    :call_id, :evaluation_score, :strengths, :weaknesses,
                    :improvements, :coaching_message, :agent_emotion_score,
                    :customer_emotion_score, :efficiency_score,
                    :manual_compliance_ratio, :final_score, NOW()
                ) ON DUPLICATE KEY UPDATE
                    evaluation_score = VALUES(evaluation_score),
                    strengths = VALUES(strengths),
                    weaknesses = VALUES(weaknesses),
                    improvements = VALUES(improvements),
                    coaching_message = VALUES(coaching_message),
                    agent_emotion_score = VALUES(agent_emotion_score),
                    customer_emotion_score = VALUES(customer_emotion_score),
                    efficiency_score = VALUES(efficiency_score),
                    manual_compliance_ratio = VALUES(manual_compliance_ratio),
                    final_score = VALUES(final_score),
                    updated_at = NOW()
            """)
            
            conn.execute(sql, {
                "call_id": consulting_data.call_id,
                "evaluation_score": analysis_data.get("평가점수", 0),
                "strengths": analysis_data.get("상담자 강점", ""),
                "weaknesses": analysis_data.get("상담자 단점", ""),
                "improvements": analysis_data.get("개선점", ""),
                "coaching_message": analysis_data.get("코칭 멘트", ""),
                "agent_emotion_score": scores.get("agent_emotion", 0),
                "customer_emotion_score": scores.get("customer_emotion", 0),
                "efficiency_score": scores.get("efficiency", 0),
                "manual_compliance_ratio": scores.get("manual_compliance", 0.0),
                "final_score": scores.get("final_score", 0)
            })
        
        logger.info(f"분석 결과가 성공적으로 저장되었습니다: {consulting_data.call_id}")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 저장 중 오류 발생 ({consulting_data.call_id}): {str(e)}")
        return False
    except Exception as e:
        logger.error(f"분석 결과 저장 중 예상치 못한 오류 ({consulting_data.call_id}): {str(e)}")
        return False


def process_single_consultation(consulting: Consulting) -> bool:
    """
    단일 상담 데이터를 처리합니다.
    
    Args:
        consulting: 상담 데이터 객체
        
    Returns:
        처리 성공 여부
    """
    try:
        logger.info(f"상담 데이터 처리 시작: {consulting.call_id}")
        
        # 상담 데이터 분석
        analysis_result = analyze_consultation(consulting.call_id)
        
        if not analysis_result:
            logger.error(f"상담 분석 실패: {consulting.call_id}")
            return False
            
        # 분석 결과를 별도 DB에 저장
        if save_analysis_results_to_db(consulting, analysis_result):
            logger.info(f"상담 데이터 처리 완료: {consulting.call_id}")
            return True
        else:
            logger.error(f"분석 결과 저장 실패: {consulting.call_id}")
            return False
            
    except Exception as e:
        logger.error(f"상담 데이터 처리 중 오류 ({consulting.call_id}): {str(e)}")
        return False


def main():
    """
    메인 함수: DB에서 데이터를 가져와 분석하고 결과를 저장합니다.
    """
    try:
        # API 키 유효성 검사
        if not validate_api_key():
            logger.error("Google API 키가 설정되지 않았거나 유효하지 않습니다.")
            print("Google API 키를 확인해주세요.")
            return
        
        logger.info("자동 분석 프로세스 시작")
        
        # DB에서 상담 데이터 가져오기
        consultings = get_all_consulting_data()
        
        if not consultings:
            logger.warning("처리할 상담 데이터가 없습니다.")
            print("처리할 상담 데이터가 없습니다.")
            return
        
        logger.info(f"총 {len(consultings)}개의 상담 데이터 처리 시작")
        
        # 처리 통계
        success_count = 0
        failure_count = 0
        
        # 각 상담 데이터 처리
        for i, consulting in enumerate(consultings, 1):
            print(f"진행률: {i}/{len(consultings)} ({i/len(consultings)*100:.1f}%) - {consulting.call_id}")
            
            if process_single_consultation(consulting):
                success_count += 1
            else:
                failure_count += 1
        
        # 최종 결과 출력
        total_count = len(consultings)
        print(f"\n{'='*60}")
        print(f"자동 분석 완료")
        print(f"{'='*60}")
        print(f"총 처리: {total_count}개")
        print(f"성공: {success_count}개")
        print(f"실패: {failure_count}개")
        print(f"성공률: {success_count/total_count*100:.1f}%" if total_count > 0 else "성공률: 0%")
        print(f"{'='*60}")
        
        logger.info(f"자동 분석 프로세스 완료: 성공 {success_count}개, 실패 {failure_count}개")
        
    except Exception as e:
        logger.error(f"메인 프로세스 실행 중 오류: {str(e)}")
        print(f"프로그램 실행 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 