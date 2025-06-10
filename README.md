# Consultlytics - AI 기반 콜센터 상담 분석 시스템

Consultlytics는 콜센터 상담 데이터를 AI를 활용하여 자동으로 분석하고 평가하는 시스템입니다. Google의 Gemini Pro 모델을 기반으로 하여 상담 품질을 종합적으로 평가하고, 상담사의 강점과 개선점을 도출합니다.

## 주요 기능

### 1. 상담 데이터 분석
- 상담 내용 자동 분석
- 감정 상태 평가 (상담사 및 고객)
- 음성 특성 분석
- 대화 효율성 평가
- 매뉴얼 준수율 평가

### 2. 평가 지표
- 감정 점수 (Emotion Score)
  - 5단계 감정 평가 (1-5 star)
  - 상담사와 고객의 감정 상태 분석
  - 100/80/60/40/20 점수 체계

- 효율성 점수 (Efficiency Score)
  - 침묵 시간 분석
  - 발화 횟수 분석
  - 최대 100점 만점

- 매뉴얼 준수율 (Manual Compliance)
  - 대안 제시 횟수
  - 사과 표현 비율
  - 긍정적 표현 비율
  - 부드러운 표현 비율
  - 공감 표현 비율

- 음성 분석 (Voice Analysis)
  - 스펙트럴 분석
  - 음성 특성 분석
  - MFCC 분석

### 3. AI 기반 코칭
- 상담사 강점 도출
- 개선점 식별
- 맞춤형 코칭 멘트 생성

## 기술 스택

### 백엔드
- Python 3.x
- Django 5.2.1
- Django REST Framework 3.16.0
- Celery 5.5.2
- Redis 6.1.0

### AI/ML
- Google Gemini Pro
- LangChain 0.1.12
- LangChain Google Genai 0.0.11

### 데이터베이스
- MySQL
- SQLAlchemy 2.0.28

### 기타
- Python-dotenv 1.1.0
- Requests 2.32.3

## 설치 방법

### 1. 저장소 클론
```bash
git clone [repository-url]
cd feple-server
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
- `env_template.txt` 파일을 참고하여 `.env` 파일을 생성:
```bash
cp env_template.txt .env
```

- `.env` 파일을 편집하여 실제 값들을 설정:
```env
# 필수 설정
DJANGO_SECRET_KEY=your-django-secret-key-here
GOOGLE_API_KEY=your-google-api-key-here
DB_PASSWORD=your-database-password

# 선택적 설정 (기본값 사용 가능)
DEBUG=True
DB_NAME=feple
DB_USER=root
DB_HOST=localhost
DB_PORT=3306
```

### 5. 데이터베이스 설정
```bash
# MySQL 데이터베이스 생성
python create_analysis_db.py
python create_table.py

# Django 마이그레이션
python manage.py migrate
```

### 6. 로그 디렉토리 생성
```bash
mkdir logs
```

## 프로젝트 구조

```
feple-server/
├── apps/
│   └── consultlytics/
│       ├── models.py      # 데이터베이스 모델
│       └── services.py    # 비즈니스 로직
├── config/                # Django 설정
├── manage.py             # Django 관리 스크립트
├── run_analysis.py       # 메인 분석 스크립트
├── LLM_automated.py      # AI 분석 로직
├── create_sample_data.py # 샘플 데이터 생성
└── requirements.txt      # 의존성 목록
```

## 사용 방법

### 1. 상담 데이터 분석 실행
```bash
python run_analysis.py
```

### 2. 분석 결과 조회
```bash
python query_analysis_results.py
```

### 3. 샘플 데이터 생성
```bash
python create_sample_data.py
```

## 데이터베이스 스키마

### analysis_results 테이블
- id: INT (Primary Key)
- call_id: VARCHAR(20)
- evaluation_score: INT
- strengths: TEXT
- weaknesses: TEXT
- improvements: TEXT
- coaching_message: TEXT
- created_at: TIMESTAMP

## 주요 개선사항 (v2.0)

### 🔒 보안 강화
- 환경 변수를 통한 모든 중요 정보 관리
- Django SECRET_KEY 및 데이터베이스 비밀번호 보호
- 프로덕션 환경용 보안 설정 추가

### 🚀 성능 최적화
- 병렬 처리를 통한 분석 속도 향상
- 배치 처리로 메모리 사용량 최적화
- 데이터베이스 쿼리 최적화

### 🛠️ 코드 품질 개선
- 공통 유틸리티 모듈 추가
- 에러 처리 및 로깅 강화
- 타입 힌트 및 문서화 개선

### 📊 모니터링 & 로깅
- 구조화된 로깅 시스템
- 분석 진행률 및 성공률 추적
- 상세한 에러 리포팅

## 주의사항

1. **필수 요구사항**:
   - Google API 키 설정 필수
   - MySQL 데이터베이스 서버 실행 필요
   - Python 3.8+ 권장

2. **환경 설정**:
   - `.env` 파일에 모든 중요 정보 설정
   - 프로덕션 환경에서는 `DEBUG=False` 설정

3. **데이터 관리**:
   - 데이터베이스 초기화 시 기존 데이터 백업 권장
   - 분석 결과는 JSON 및 DB에 이중 저장

4. **성능 고려사항**:
   - 대량 데이터 처리 시 배치 크기 조정 가능
   - API 호출 제한 고려하여 동시 처리 수 조정

## 성능 최적화

1. 대량의 데이터 처리
   - Celery를 통한 비동기 처리
   - 배치 처리 지원

2. 메모리 관리
   - 대용량 데이터 청크 처리
   - 효율적인 메모리 사용

3. API 호출 최적화
   - 요청 캐싱
   - 배치 처리

## 라이선스

[라이선스 정보]

## 기여 방법

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 연락처

[연락처 정보] 