import os
import django
import json

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.consultlytics.models import Consulting

# DB에서 모든 상담 데이터 조회
consultings = Consulting.objects.all().order_by('call_id')

# 각 row의 모든 컬럼 구조와 값을 출력
for c in consultings:
    print(f"\n=== 상담 데이터: {c.call_id} ===")
    for field in Consulting._meta.fields:
        value = getattr(c, field.name)
        print(f"{field.name}: {value}") 