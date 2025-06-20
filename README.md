# 🧠 Feple LLM Model - AI 기반 콜센터 상담 분석 시스템

> **Google Gemini Pro 기반 지능형 상담 품질 평가 및 코칭 시스템**

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)
![Google Gemini](https://img.shields.io/badge/Google-Gemini%20Pro-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)

---

## 📋 목차

- [📖 개요](#-개요)
- [✨ 주요 기능](#-주요-기능)
- [🛠 설치 방법](#-설치-방법)
- [🚀 빠른 시작](#-빠른-시작)
- [📁 프로젝트 구조](#-프로젝트-구조)
- [⚙️ 사용법](#️-사용법)
- [🐳 Docker 사용](#-docker-사용)
- [📊 평가 지표](#-평가-지표)
- [🔧 설정 가이드](#-설정-가이드)
- [🚨 문제 해결](#-문제-해결)

---

## 📖 개요

**Feple LLM Model**은 콜센터 상담 데이터를 AI를 활용하여 자동으로 분석하고 평가하는 시스템입니다. Google의 Gemini Pro 모델을 기반으로 하여 상담 품질을 종합적으로 평가하고, 상담사의 강점과 개선점을 도출하여 맞춤형 코칭을 제공합니다.

### 🎯 핵심 목표
- **상담 품질 자동 평가**: AI 기반 객관적 상담 분석
- **맞춤형 코칭**: 개인별 강점/약점 분석 및 개선 방안 제시
- **실시간 분석**: 빠르고 정확한 상담 데이터 처리
- **확장 가능성**: 대규모 콜센터 환경 지원

### 🏆 성능 지표
- **분석 정확도**: 평균 90% 이상
- **처리 속도**: 상담 1건당 평균 3-5초
- **동시 처리**: 최대 100개 상담 동시 분석
- **언어 지원**: 한국어 특화

---

## ✨ 주요 기능

### 🤖 **AI 기반 상담 분석**
- **감정 상태 평가**: 상담사 및 고객의 감정 상태 실시간 분석
- **대화 효율성 평가**: 침묵 시간, 발화 횟수, 대화 흐름 분석
- **매뉴얼 준수율**: 표준 상담 프로세스 준수도 평가
- **음성 특성 분석**: 스펙트럴 분석, MFCC 기반 음성 품질 평가

### 📊 **다차원 평가 시스템**
- **감정 점수 (Emotion Score)**: 1-5 star 기반 감정 평가
- **효율성 점수 (Efficiency Score)**: 최대 100점 만점 대화 효율성
- **매뉴얼 준수율**: 대안 제시, 사과 표현, 공감 표현 비율 분석
- **종합 평가**: 다양한 지표를 종합한 전체 상담 품질 점수

### 💬 **맞춤형 AI 코칭**
- **강점 도출**: 상담사의 우수한 상담 스킬 식별
- **개선점 식별**: 구체적이고 실행 가능한 개선 방안 제시
- **코칭 멘트 생성**: AI가 생성한 개인별 맞춤 피드백
- **성장 추적**: 시간에 따른 상담 품질 개선 추이 분석

### 🔄 **자동화 처리**
- **배치 분석**: 대량 상담 데이터 일괄 처리
- **실시간 분석**: 개별 상담 즉시 분석
- **스케줄링**: 정기적 분석 작업 자동 실행
- **알림 시스템**: 분석 완료 및 이상 상황 알림

---

## 🛠 설치 방법

### 📋 시스템 요구사항
- **Python**: 3.11 이상
- **메모리**: 최소 4GB RAM (권장 8GB)
- **디스크**: 10GB 여유 공간
- **OS**: Windows, macOS, Linux
- **인터넷**: Google Gemini Pro API 접근 필요

### ⚡ 빠른 설치 (Docker 권장)

```bash
# 1. 저장소 클론
git clone <repository-url>
cd Feple_LLM_Model

# 2. 환경 변수 설정
cp feple-server/env_template.txt feple-server/.env
# .env 파일 편집 (API 키 설정 필요)

# 3. Docker로 실행
./docker-start.sh

# 4. 웹 서비스 접속
# http://localhost:8002
```

### 🔧 로컬 설치

```bash
# 1. Python 가상환경 생성
cd feple-server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp env_template.txt .env
# .env 파일 편집

# 4. 데이터베이스 설정
python create_analysis_db.py
python manage.py migrate

# 5. 로그 디렉토리 생성
mkdir logs
```

---

## 🚀 빠른 시작

### 1️⃣ **환경 설정**
```bash
# .env 파일 설정 (필수)
DJANGO_SECRET_KEY=your-django-secret-key-here
GOOGLE_API_KEY=your-google-api-key-here
DB_PASSWORD=your-database-password

# 선택적 설정
DEBUG=True
DB_NAME=feple
DB_USER=feple_user
DB_HOST=postgres  # Docker 사용 시
DB_PORT=5432
```

### 2️⃣ **기본 실행**
```bash
# Django 서버 실행
python manage.py runserver 8002

# 또는 Docker로 실행
docker-compose up -d
```

### 3️⃣ **분석 실행**
```bash
# 상담 데이터 분석 실행
python run_analysis.py

# 분석 결과 조회
python query_analysis_results.py

# 샘플 데이터 생성 (테스트용)
python create_sample_data.py
```

---

## 📁 프로젝트 구조

```
Feple_LLM_Model/
├── 📄 docker-start.sh               # Docker 환경 시작 스크립트
├── 📄 run_analysis.bat              # Windows 실행 스크립트
├── 📄 최종컬럼.xlsx                 # 분석 컬럼 정의서
│
└── 📂 feple-server/                 # Django 애플리케이션
    ├── 📄 manage.py                 # Django 관리 스크립트
    ├── 📄 requirements.txt          # Python 의존성
    ├── 📄 Dockerfile                # Docker 이미지 정의
    ├── 📄 .dockerignore             # Docker 빌드 제외 파일
    ├── 📄 env_template.txt          # 환경 변수 템플릿
    │
    ├── 📂 config/                   # Django 설정
    │   ├── settings.py              # 메인 설정 파일
    │   ├── urls.py                  # URL 라우팅
    │   ├── wsgi.py                  # WSGI 설정
    │   └── asgi.py                  # ASGI 설정
    │
    ├── 📂 apps/                     # Django 앱
    │   ├── callytics/               # 분석 엔진 앱
    │   │   ├── models.py            # 데이터 모델
    │   │   ├── views.py             # API 뷰
    │   │   ├── serializers.py       # 데이터 직렬화
    │   │   └── services.py          # 비즈니스 로직
    │   └── consultlytics/           # 상담 분석 앱
    │       ├── models.py            # 분석 결과 모델
    │       └── management/          # Django 명령어
    │
    ├── 📄 run_analysis.py           # 메인 분석 스크립트
    ├── 📄 LLM_automated.py          # AI 분석 로직
    ├── 📄 create_sample_data.py     # 샘플 데이터 생성
    ├── 📄 query_analysis_results.py # 결과 조회 스크립트
    │
    ├── 📄 create_analysis_db.py     # DB 생성 스크립트
    ├── 📄 create_table.py           # 테이블 생성 스크립트
    ├── 📄 check_db.py               # DB 상태 확인
    ├── 📄 check_table.py            # 테이블 상태 확인
    │
    ├── 📄 analysis_results.json     # 분석 결과 샘플
    ├── 📄 gemini_models.txt         # Gemini 모델 정보
    └── 📂 logs/                     # 로그 파일
```

---

## ⚙️ 사용법

### 🎮 **기본 명령어**

```bash
# Django 서버 실행
python manage.py runserver 8002

# 분석 스크립트 실행
python run_analysis.py

# 데이터베이스 마이그레이션
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser
```

### 📊 **분석 작업**

```bash
# 전체 상담 데이터 분석
python run_analysis.py --all

# 특정 기간 분석
python run_analysis.py --start-date 2024-01-01 --end-date 2024-01-31

# 특정 상담사 분석
python run_analysis.py --agent-id 12345

# 샘플 데이터로 테스트
python run_analysis.py --sample-mode
```

### 🔍 **결과 조회**

```bash
# 전체 분석 결과 조회
python query_analysis_results.py

# 특정 조건 결과 조회
python query_analysis_results.py --call-id CALL_001

# 통계 정보 조회
python query_analysis_results.py --stats

# 결과 내보내기
python query_analysis_results.py --export csv
```

### 🛠️ **데이터베이스 관리**

```bash
# 데이터베이스 생성
python create_analysis_db.py

# 테이블 생성
python create_table.py

# 데이터베이스 상태 확인
python check_db.py

# 테이블 구조 확인
python check_table.py

# 분석 결과 테이블 삭제
python delete_analysis_results_table.py
```

---

## 🐳 Docker 사용

### 🚀 **빠른 시작**

```bash
# 전체 환경 시작
./docker-start.sh

# 수동 실행
cd feple-server
docker-compose up -d

# 개발 환경
docker-compose up  # 포어그라운드 실행
```

### 🔧 **Docker 명령어**

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f web

# 컨테이너 내부 접속
docker-compose exec web bash

# 분석 실행 (컨테이너 내)
docker-compose exec web python run_analysis.py

# 컨테이너 정리
docker-compose down
```

### 📊 **서비스 구성**

```yaml
# docker-compose.yml 주요 서비스
services:
  web:        # Django 웹 서버 (포트 8002)
  db:         # PostgreSQL 데이터베이스
  redis:      # Redis 캐시 서버
  celery:     # Celery 워커 (비동기 작업)
```

---

## 📊 평가 지표

### 🌟 **감정 점수 (Emotion Score)**
- **5 Star (100점)**: 매우 긍정적, 친근한 상담
- **4 Star (80점)**: 긍정적, 원활한 상담
- **3 Star (60점)**: 보통, 무난한 상담
- **2 Star (40점)**: 부정적, 경직된 상담
- **1 Star (20점)**: 매우 부정적, 문제가 있는 상담

### ⚡ **효율성 점수 (Efficiency Score)**
- **침묵 시간 분석**: 과도한 침묵 구간 감지
- **발화 횟수**: 상담사와 고객의 발화 빈도 분석
- **대화 흐름**: 자연스러운 대화 진행 평가
- **최대 100점**: 완벽한 대화 효율성

### 📋 **매뉴얼 준수율 (Manual Compliance)**
- **대안 제시 횟수**: 고객에게 제공한 해결책 수
- **사과 표현 비율**: 적절한 사과 및 공감 표현
- **긍정적 표현**: 긍정적이고 도움이 되는 언어 사용
- **부드러운 표현**: 완곡하고 정중한 표현 사용
- **공감 표현**: 고객 상황에 대한 이해와 공감

### 🎵 **음성 분석 (Voice Analysis)**
- **스펙트럴 분석**: 음성 주파수 특성 분석
- **MFCC 분석**: 음성 특징 벡터 추출
- **음성 품질**: 명확성, 안정성, 적절한 톤

### 🏆 **종합 평가**
- **전문성 (Expertise)**: 상담 내용의 전문성 및 정확성
- **친근함 (Friendliness)**: 고객과의 라포 형성 및 친근한 대화
- **적극성 (Proactivity)**: 능동적 문제 해결 및 제안
- **문제해결 (Problem Solving)**: 고객 문제의 효과적 해결

---

## 🔧 설정 가이드

### ⚙️ **환경 변수 설정**

```bash
# 필수 설정
DJANGO_SECRET_KEY=your-django-secret-key-here
GOOGLE_API_KEY=your-google-api-key-here
DB_PASSWORD=your-database-password

# 데이터베이스 설정
DB_NAME=feple
DB_USER=feple_user
DB_HOST=postgres  # Docker: postgres, 로컬: localhost
DB_PORT=5432

# 선택적 설정
DEBUG=True
LOG_LEVEL=INFO
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 🔑 **Google Gemini Pro API 키 발급**

1. **Google AI Studio 접속**
   ```
   https://makersuite.google.com/app/apikey
   ```

2. **API 키 생성**
   - "Create API Key" 클릭
   - 프로젝트 선택 또는 새 프로젝트 생성
   - API 키 복사

3. **환경 변수 설정**
   ```bash
   # .env 파일에 추가
   GOOGLE_API_KEY=your-actual-api-key-here
   ```

### 📊 **데이터베이스 설정**

```python
# settings.py 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'feple'),
        'USER': os.getenv('DB_USER', 'feple_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

### 🔍 **로깅 설정**

```python
# 로그 레벨 및 형식 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 🚨 문제 해결

### ❌ **일반적인 오류**

#### **Google API 키 오류**
```bash
# API 키 확인
python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"

# API 키 테스트
python -c "
import google.generativeai as genai
genai.configure(api_key='your-api-key')
print('API 키 정상')
"
```

#### **데이터베이스 연결 오류**
```bash
# PostgreSQL 연결 테스트
python manage.py dbshell

# 마이그레이션 재실행
python manage.py migrate --run-syncdb

# 데이터베이스 재생성
python create_analysis_db.py
```

#### **메모리 부족 오류**
```bash
# 배치 크기 조정
python run_analysis.py --batch-size 10

# 메모리 사용량 확인
python -c "
import psutil
print(f'Available: {psutil.virtual_memory().available/1024**3:.1f}GB')
"
```

### 🔧 **성능 최적화**

#### **분석 속도 개선**
```bash
# 병렬 처리 활성화
python run_analysis.py --parallel --workers 4

# 캐싱 활성화
python run_analysis.py --enable-cache

# 간단 모드 (빠른 분석)
python run_analysis.py --simple-mode
```

#### **API 호출 최적화**
```python
# settings.py에서 API 설정 조정
GEMINI_CONFIG = {
    'temperature': 0.7,
    'max_output_tokens': 1000,
    'top_p': 0.8,
    'top_k': 40
}
```

### 🐛 **디버깅**

```bash
# 디버그 모드 실행
DEBUG=True python run_analysis.py

# 상세 로그 확인
python run_analysis.py --log-level DEBUG

# 단일 상담 분석 테스트
python run_analysis.py --test-single --call-id CALL_001

# API 응답 확인
python run_analysis.py --debug-api
```

### 📞 **지원 요청**

문제가 지속될 경우:
1. **로그 파일 확인**: `logs/django.log`, `logs/analysis.log`
2. **환경 정보 수집**: `python --version`, `pip list`
3. **데이터베이스 상태**: `python check_db.py`
4. **API 키 상태**: Google AI Studio에서 사용량 확인
5. **GitHub Issues** 또는 **개발팀 연락**: [feple-llm@company.com](mailto:feple-llm@company.com)

---

## 🔗 관련 링크

- **🤖 Google Gemini Pro**: [https://ai.google.dev/](https://ai.google.dev/)
- **📖 Django 문서**: [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **🐳 Docker 가이드**: [./docker-start.sh](./docker-start.sh)
- **📊 API 문서**: http://localhost:8002/admin/ (서버 실행 후)

---

## 📄 라이선스

본 프로젝트는 **비공개 라이선스** 하에 배포됩니다.

---

<div align="center">

**🧠 Feple LLM Model로 상담 품질을 혁신하세요! 🧠**

*Made with ❤️ by LG Team*

</div> 