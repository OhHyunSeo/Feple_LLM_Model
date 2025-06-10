@echo off
echo =============================================
echo    Consultlytics 상담 분석 시스템 v2.0
echo =============================================
echo.

REM 환경 변수 파일 확인
if not exist "feple-server\.env" (
    echo [오류] .env 파일이 존재하지 않습니다.
    echo env_template.txt 파일을 참고하여 .env 파일을 생성해주세요.
    echo.
    pause
    exit /b 1
)

REM 가상환경 활성화
echo [1/6] 가상환경 활성화 중...
if exist "feple-server\venv\Scripts\activate.bat" (
    call feple-server\venv\Scripts\activate
) else (
    echo [경고] 가상환경이 존재하지 않습니다. 전역 Python 환경을 사용합니다.
)

REM 디렉토리 이동
cd feple-server

REM 로그 디렉토리 생성
echo [2/6] 로그 디렉토리 확인/생성 중...
if not exist "logs" mkdir logs

REM 필요한 패키지 설치
echo [3/6] 패키지 설치/업데이트 중...
pip install -r requirements.txt --quiet

REM 데이터베이스 마이그레이션
echo [4/6] 데이터베이스 마이그레이션 중...
python manage.py migrate --verbosity=1

REM 샘플 데이터 생성 (선택사항)
echo [5/6] 샘플 데이터 확인 중...
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.consultlytics.models import Consulting
count = Consulting.objects.count()
if count == 0:
    print('샘플 데이터가 없습니다. create_sample_data.py를 실행하세요.')
else:
    print(f'기존 데이터 {count}개 발견. 분석을 계속 진행합니다.')
"

REM 분석 실행
echo [6/6] 상담 분석 실행 중...
echo =============================================
python run_analysis.py

echo.
echo =============================================
echo 분석이 완료되었습니다!
echo 결과 파일: analysis_results.json
echo 로그 파일: logs/consultlytics.log
echo =============================================
pause 

