import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# feple DB에 접속
DB_URI = os.getenv("DB_URI", "mysql://root:1234@localhost:3306/feple")
engine = create_engine(DB_URI)

def delete_analysis_results_table():
    try:
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS analysis_results;"))
        print("feple 데이터베이스의 analysis_results 테이블이 삭제되었습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    delete_analysis_results_table() 