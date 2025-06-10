from django.core.management.base import BaseCommand
from apps.consultlytics.models import Consulting
import random
import json
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = '샘플 데이터를 생성합니다.'

    def handle(self, *args, **kwargs):
        # 기존 데이터 삭제
        Consulting.objects.all().delete()

        # 샘플 데이터 생성
        for i in range(11):
            # 기본 데이터
            consulting = Consulting.objects.create(
                call_id=f'CALL_{i+1:03d}',
                call_date=datetime.now() - timedelta(days=i),
                call_duration=random.randint(300, 1800),
                silence=random.randint(30, 180),
                csr_speech_count=random.randint(20, 50),
                customer_speech_count=random.randint(15, 40),
                csr_emotion_score=random.uniform(3.0, 5.0),
                customer_emotion_score=random.uniform(3.0, 5.0),
                efficiency_score=random.randint(80, 100),
                manual_compliance_ratio=random.uniform(0.8, 1.0),
                final_score=random.randint(60, 90),
                positive_word_ratio=random.uniform(0.6, 0.9),
                empathy_expression_ratio=random.uniform(0.7, 0.95),
                apology_ratio=random.uniform(0.1, 0.3),
                alternative_solution_count=random.randint(2, 5),
                consulting_content=f"상담 내용 샘플 {i+1}",
                Extension="wav",
                Path=f"/data/calls/call_{i+1:03d}.wav",
                Rate=16000,
                BitDepth=16,
                Channels=1,
                Duration=random.randint(300, 1800),
                MinFreq=20,
                MaxFreq=8000,
                RMSLoudness=random.uniform(-30, -10),
                ZeroCrossingRate=random.uniform(0.1, 0.3),
                SpectralCentroid=random.uniform(1000, 3000),
                SpectralBandwidth=random.uniform(1000, 5000),
                SpectralFlatness=random.uniform(0.1, 0.5),
                RollOff=random.uniform(3000, 7000),
                Chroma_stft=json.dumps([random.uniform(0, 1) for _ in range(12)]),
                SpectralContrast=json.dumps([random.uniform(0, 1) for _ in range(7)]),
                Tonnetz=json.dumps([random.uniform(-1, 1) for _ in range(6)]),
                MFCC_0_13=json.dumps([random.uniform(-100, 100) for _ in range(14)]),
                Summary=f"상담 요약 샘플 {i+1}",
                Conflict=random.choice([True, False]),
                Speaker="CSR",
                Sequence=1,
                StartTime=0,
                EndTime=random.randint(300, 1800),
                Content=f"발화 내용 샘플 {i+1}",
                Sentiment=random.choice(["positive", "neutral", "negative"]),
                Profane=random.choice([True, False]),
                top_nouns=json.dumps(["시간", "서비스", "문제", "해결", "고객", "제품", "안내", "문의", "처리", "확인"]),
                sent_score=random.uniform(-1, 1),
                sent_label=random.choice(["positive", "neutral", "negative"]),
                mid_category=random.choice(["상품문의", "서비스문의", "불만처리", "기타문의"]),
                content_category=random.choice(["가입", "해지", "변경", "요금", "기타"]),
                script_phrase_ratio=random.uniform(0.6, 0.9),
                honorific_ratio=random.uniform(0.7, 0.95),
                confirmation_ratio=random.uniform(0.3, 0.6),
                request_ratio=random.uniform(0.2, 0.5),
                conflict_flag=random.choice([True, False])
            )

            self.stdout.write(self.style.SUCCESS(f'Successfully created sample data for call_id: {consulting.call_id}')) 