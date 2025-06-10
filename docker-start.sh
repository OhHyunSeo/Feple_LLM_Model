#!/bin/bash

echo "=============================================="
echo "    Consultlytics Docker 환경 시작"
echo "=============================================="

# 환경 변수 파일 확인
if [ ! -f "feple-server/.env" ]; then
    echo "❌ [오류] .env 파일이 존재하지 않습니다."
    echo "env_template.txt 파일을 참고하여 feple-server/.env 파일을 생성해주세요."
    exit 1
fi

echo "✅ 환경 변수 파일 확인 완료"

# Docker Compose 실행
echo "🐳 Docker 컨테이너 시작 중..."
cd feple-server

# 기존 컨테이너 정리 (선택사항)
echo "🧹 기존 컨테이너 정리 중..."
docker-compose down --remove-orphans

# 이미지 빌드 및 컨테이너 시작
echo "🔧 Docker 이미지 빌드 중..."
docker-compose build

echo "🚀 서비스 시작 중..."
docker-compose up -d db redis

# 데이터베이스가 준비될 때까지 대기
echo "⏳ 데이터베이스 준비 대기 중..."
sleep 30

# 웹 서비스 시작
echo "🌐 웹 서비스 시작 중..."
docker-compose up -d web celery_worker celery_beat

echo ""
echo "=============================================="
echo "🎉 Docker 환경이 성공적으로 시작되었습니다!"
echo "=============================================="
echo ""
echo "📊 서비스 접속 정보:"
echo "   - Web Application: http://localhost:8000"
echo "   - MySQL Database: localhost:3306"
echo "   - Redis: localhost:6379"
echo ""
echo "🔍 상태 확인:"
echo "   docker-compose ps"
echo ""
echo "📝 로그 확인:"
echo "   docker-compose logs -f [서비스명]"
echo ""
echo "🔧 분석 실행:"
echo "   docker-compose run --rm analyzer"
echo ""
echo "🛑 서비스 중지:"
echo "   docker-compose down"
echo ""
echo "==============================================" 