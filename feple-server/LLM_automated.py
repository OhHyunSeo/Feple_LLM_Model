import os
import json
import requests
from dotenv import load_dotenv
import django
from django.conf import settings
from django.forms.models import model_to_dict
from sqlalchemy import create_engine, text

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.consultlytics.models import Consulting

# 환경 변수 로드
load_dotenv()

# API 키 설정
API_KEY = os.getenv('GOOGLE_API_KEY')
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={API_KEY}"

def get_consulting_data_from_db():
    """데이터베이스에서 최신 상담 데이터를 가져옵니다."""
    try:
        # 최신 상담 데이터 조회
        consultings = Consulting.objects.all().order_by('call_id')
        return consultings
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {str(e)}")
        return []

def analyze_consultation(consulting_data):
    """Google API를 사용하여 상담 데이터를 분석합니다."""
    try:
        # API 요청 데이터 준비
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"상담 데이터 분석: {json.dumps(model_to_dict(consulting_data))}"
                        }
                    ]
                }
            ]
        }
        
        # API 요청 보내기
        response = requests.post(API_URL, json=data)
        response.raise_for_status()  # 오류 발생 시 예외 발생
        
        # API 응답에서 분석 결과 추출
        result = response.json()
        return result
    except Exception as e:
        print(f"API 분석 중 오류 발생: {str(e)}")
        return None

def save_analysis_results(consulting_data, analysis_result):
    """분석 결과를 새로운 DB에 저장합니다."""
    try:
        # 분석 결과 DB 연결
        DB_URI = os.getenv("ANALYSIS_DB_URI", "mysql://root:1234@localhost:3306/feple_analysis")
        engine = create_engine(DB_URI)
        
        # 분석 결과 저장
        with engine.begin() as conn:
            sql = text("""
                INSERT INTO analysis_results (
                    call_id, evaluation_score, strengths, weaknesses,
                    improvements, coaching_message
                ) VALUES (
                    :call_id, :evaluation_score, :strengths, :weaknesses,
                    :improvements, :coaching_message
                ) ON DUPLICATE KEY UPDATE
                    evaluation_score = VALUES(evaluation_score),
                    strengths = VALUES(strengths),
                    weaknesses = VALUES(weaknesses),
                    improvements = VALUES(improvements),
                    coaching_message = VALUES(coaching_message)
            """)
            
            conn.execute(sql, {
                "call_id": consulting_data.call_id,
                "evaluation_score": analysis_result.get("평가점수", 0),
                "strengths": analysis_result.get("상담자 강점", ""),
                "weaknesses": analysis_result.get("상담자 단점", ""),
                "improvements": analysis_result.get("개선점", ""),
                "coaching_message": analysis_result.get("코칭 멘트", "")
            })
        
        print(f"분석 결과가 성공적으로 저장되었습니다: {consulting_data.call_id}")
    except Exception as e:
        print(f"분석 결과 저장 중 오류 발생: {str(e)}")

def main():
    """메인 함수: DB에서 데이터를 가져와 분석하고 결과를 저장합니다."""
    # DB에서 상담 데이터 가져오기
    consultings = get_consulting_data_from_db()
    
    for consulting in consultings:
        # 상담 데이터 분석
        analysis_result = analyze_consultation(consulting)
        
        if analysis_result:
            # 분석 결과 저장
            save_analysis_results(consulting, analysis_result)

if __name__ == "__main__":
    main() 