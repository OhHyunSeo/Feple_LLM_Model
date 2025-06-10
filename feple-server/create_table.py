import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# 데이터베이스 설정
DB_URI = os.getenv("DB_URI", "mysql://root:1234@localhost:3306/feple")
engine = create_engine(DB_URI)

def create_analysis_results_table():
    """분석 결과를 저장할 새로운 테이블을 생성합니다."""
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS analysis_results;"))
            conn.execute(text("""
                CREATE TABLE analysis_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    call_id VARCHAR(20) NOT NULL,
                    evaluation_score INT NOT NULL,
                    strengths TEXT NOT NULL,
                    weaknesses TEXT NOT NULL,
                    improvements TEXT NOT NULL,
                    coaching_message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_call_id (call_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
        print("테이블이 성공적으로 재생성되었습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    create_analysis_results_table() 