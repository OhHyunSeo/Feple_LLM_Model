import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES LIKE 'consulting';")
    result = cursor.fetchone()
    if result:
        print('consulting 테이블이 존재합니다.')
    else:
        print('consulting 테이블이 존재하지 않습니다.') 