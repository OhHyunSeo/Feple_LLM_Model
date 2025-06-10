import json
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# 분석 결과는 feple_analysis DB에 저장
DB_URI = os.getenv("ANALYSIS_DB_URI", "mysql://root:1234@localhost:3306/feple_analysis")
engine = create_engine(DB_URI)

def save_analysis_results():
    """analysis_results.json 파일의 데이터를 데이터베이스에 저장합니다."""
    try:
        # JSON 파일 읽기
        with open('analysis_results.json', 'r', encoding='utf-8') as f:
            results = json.load(f)

        # 데이터베이스에 저장
        with engine.begin() as conn:
            for result in results:
                call_id = result.get('call_id')
                analysis = result.get('analysis', {})
                if not call_id or not analysis:
                    continue

                # SQL 쿼리 작성
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

                # 데이터 준비
                params = {
                    'call_id': call_id,
                    'evaluation_score': analysis.get('평가점수'),
                    'strengths': analysis.get('상담자 강점'),
                    'weaknesses': analysis.get('상담자 단점'),
                    'improvements': analysis.get('개선점'),
                    'coaching_message': analysis.get('코칭 멘트')
                }

                # 쿼리 실행
                conn.execute(sql, params)
                print(f"{call_id}의 분석 결과가 저장되었습니다.")

        print("모든 분석 결과가 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    save_analysis_results() 