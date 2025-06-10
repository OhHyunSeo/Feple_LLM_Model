import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# feple_analysis DB에 접속
DB_URI = os.getenv("ANALYSIS_DB_URI", "mysql://root:1234@localhost:3306/feple_analysis")
engine = create_engine(DB_URI)

def query_analysis_results():
    """분석 결과를 조회하고 출력합니다."""
    try:
        with engine.connect() as conn:
            # 모든 분석 결과 조회
            result = conn.execute(text("""
                SELECT call_id, evaluation_score, strengths, weaknesses, 
                       improvements, coaching_message, created_at
                FROM analysis_results
                ORDER BY call_id
            """))
            
            print("\n=== 상담 분석 결과 조회 ===\n")
            for row in result:
                print(f"\nCALL_ID: {row.call_id}")
                print(f"평가점수: {row.evaluation_score}")
                print(f"상담자 강점: {row.strengths}")
                print(f"상담자 단점: {row.weaknesses}")
                print(f"개선점: {row.improvements}")
                print(f"코칭 멘트: {row.coaching_message}")
                print(f"분석 시간: {row.created_at}")
                print("-" * 80)
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    query_analysis_results() 