import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute('DROP TABLE IF EXISTS consulting;')
    print('consulting 테이블 삭제 완료') 