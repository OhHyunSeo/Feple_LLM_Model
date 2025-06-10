@echo off
echo 상담 분석 시스템 실행 스크립트
echo ============================

REM 가상환경 활성화
call venv\Scripts\activate

REM 필요한 패키지 설치
echo 패키지 설치 중...
pip install -r requirements.txt

REM 데이터베이스 마이그레이션
echo 데이터베이스 마이그레이션 중...
python manage.py migrate

REM 샘플 데이터 생성
echo 샘플 데이터 생성 중...
python create_sample_data.py

REM 분석 실행
echo 분석 실행 중...
python run_analysis.py

echo ============================
echo 분석이 완료되었습니다.
pause 

