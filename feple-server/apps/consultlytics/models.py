"""
apps/consultlytics/models.py

이 파일은 LightGBM 기반 'Consultlytics' 서비스의 결과를 저장하기 위해
다중 테이블로 정규화된 Django 모델 정의를 담고 있습니다.
각 테이블은 상담 세션(Session), 명사 분석(TopNoun), 감정 점수(EmotionScore),
카테고리(Category), 스크립트 지표(ScriptMetric), 최종 결과(ResultClassification)를
별도 관리하며, 관계 설정 및 필드 설명을 자세히 작성했습니다.

< 마이그레이션 안내 >
1) 앱 생성·등록 후
   $ python manage.py makemigrations consultlytics
2) 테이블 생성/변경 반영
   $ python manage.py migrate

<사용 예시>
  from apps.consultlytics.models import Session, EmotionScore, ResultClassification
  # 모델 인스턴스를 생성·조회하여 ORM으로 데이터 관리 가능
"""

from django.db import models


class Session(models.Model):
    """
    상담 세션의 기본 정보 저장
      - session_id       : 상담 세션 고유 ID
      - speech_count     : 총 발화(turn) 수
      - consulting_text  : 전체 상담 텍스트
      - asr_segments     : ASR 분할 발화 JSON
    """
    session_id      = models.CharField(max_length=100, primary_key=True, verbose_name="세션 ID", help_text="상담 세션 고유 식별자")
    speech_count    = models.IntegerField(verbose_name="총 발화 수", help_text="상담 세션에서 인식된 총 발화 수")
    consulting_text= models.TextField(verbose_name="상담 텍스트", help_text="원본 상담 대화 전체 내용")
    asr_segments    = models.JSONField(verbose_name="ASR 세그먼트", help_text="고객/상담사 발화를 분리한 JSON 리스트")
    created_at      = models.DateTimeField(auto_now_add=True, verbose_name="분석 시각")

    def __str__(self):
        return f"Session {self.session_id}"


class TopNoun(models.Model):
    """
    세션별 주요 명사 Top10 저장
      - session (FK)
      - nouns   : 명사 리스트(JSON)
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name="세션", related_name="top_nouns")
    nouns   = models.JSONField(verbose_name="Top10 명사", help_text="추출된 상위 10개 명사 리스트")

    def __str__(self):
        return f"Top Nouns for {self.session.session_id}"


class EmotionScore(models.Model):
    """
    고객/상담사별 1~5★ 감정 비율 및 평균·레이블 저장
      - session          : 세션 FK
      - actor            : 'customer' or 'agent'
      - star1~star5      : 1★~5★ 비율 (float)
      - avg_score        : 평균 감정 점수
      - label            : 분류된 감정 레이블
    """
    ACTOR_CHOICES = [("customer", "고객"), ("agent", "상담사")]

    session   = models.ForeignKey(Session, on_delete=models.CASCADE, verbose_name="세션", related_name="emotion_scores")
    actor     = models.CharField(max_length=10, choices=ACTOR_CHOICES, verbose_name="행위자", help_text="점수 대상: 고객 또는 상담사")
    star1     = models.FloatField(verbose_name="1★ 비율")
    star2     = models.FloatField(verbose_name="2★ 비율")
    star3     = models.FloatField(verbose_name="3★ 비율")
    star4     = models.FloatField(verbose_name="4★ 비율")
    star5     = models.FloatField(verbose_name="5★ 비율")
    avg_score = models.FloatField(verbose_name="평균 점수", help_text="1~5★ 비율의 가중 평균")
    label     = models.CharField(max_length=50, verbose_name="감정 레이블", help_text="평균 점수 기반 분류 라벨")

    class Meta:
        unique_together = ("session", "actor")

    def __str__(self):
        return f"Emotion({self.actor}) @ {self.session.session_id}"


class Category(models.Model):
    """
    상담/유형 카테고리 및 결과 분류 정보 저장
      - session            : 세션 FK
      - mid_category       : 중분류 이름
      - content_category   : 상담 유형 카테고리 이름
      - mid_category_id    : 중분류 ID
      - result_label       : 최종 결과 레이블
      - label_id           : 결과 레이블 ID
    """
    session          = models.OneToOneField(Session, on_delete=models.CASCADE, verbose_name="세션", related_name="category")
    mid_category     = models.CharField(max_length=100, verbose_name="상담 카테고리")
    content_category = models.CharField(max_length=100, verbose_name="상담 유형")
    mid_category_id  = models.IntegerField(verbose_name="카테고리 ID")
    result_label     = models.CharField(max_length=50, verbose_name="최종 결과 레이블")
    label_id         = models.IntegerField(verbose_name="결과 레이블 ID")

    def __str__(self):
        return f"Category @ {self.session.session_id}"


class ScriptMetric(models.Model):
    """
    상담사 스크립트 및 커뮤니케이션 지표 저장
      - session                  : 세션 FK
      - script_phrase_ratio      : 스크립트 준수 비율
      - honorific_ratio          : 존댓말 비율
      - positive_word_ratio      : 긍정 단어 비율
      - euphonious_word_ratio    : 완곡어 사용 비율
      - confirmation_ratio       : 확인 멘트 비율
      - empathy_ratio            : 공감 멘트 비율
      - apology_ratio            : 사과 멘트 비율
      - request_ratio            : 의뢰 멘트 비율
      - alternative_count        : 대안 제안 횟수
      - conflict_flag            : 갈등 발생 여부
      - manual_compliance_ratio  : 매뉴얼 준수 비율
    """
    session               = models.OneToOneField(Session, on_delete=models.CASCADE, verbose_name="세션", related_name="script_metrics")
    script_phrase_ratio   = models.FloatField(verbose_name="스크립트 준수 비율")
    honorific_ratio       = models.FloatField(verbose_name="존댓말 비율")
    positive_word_ratio   = models.FloatField(verbose_name="긍정 단어 비율")
    euphonious_word_ratio = models.FloatField(verbose_name="완곡어 사용 비율")
    confirmation_ratio    = models.FloatField(verbose_name="확인 멘트 비율")
    empathy_ratio         = models.FloatField(verbose_name="공감 멘트 비율")
    apology_ratio         = models.FloatField(verbose_name="사과 멘트 비율")
    request_ratio         = models.FloatField(verbose_name="의뢰 멘트 비율")
    alternative_count     = models.IntegerField(verbose_name="대안 제안 횟수")
    conflict_flag         = models.BooleanField(default=False, verbose_name="갈등 여부", choices=[(False, "없음"),(True, "있음")])
    manual_compliance_ratio = models.FloatField(verbose_name="매뉴얼 준수 비율")

    def __str__(self):
        return f"ScriptMetric @ {self.session.session_id}"


class ResultClassification(models.Model):
    """
    예측 모델의 최종 결과 저장
      - session     : 세션 FK
      - label       : 만족/미흡/추가 상담 필요/해결 불가
    """
    session = models.OneToOneField(Session, on_delete=models.CASCADE, verbose_name="세션", related_name="result")
    label   = models.CharField(max_length=50, verbose_name="결과 레이블", help_text="만족, 미흡, 추가 상담 필요, 해결 불가")

    def __str__(self):
        return f"Result {self.label} @ {self.session.session_id}"


class Meta:
    verbose_name = "Consultlytics 모델 결과"
    verbose_name_plural = "Consultlytics 모델 결과들"


class Consulting(models.Model):
    call_id = models.CharField(max_length=100, primary_key=True)
    call_date = models.DateTimeField(auto_now_add=True)
    call_duration = models.IntegerField(default=0)
    silence = models.IntegerField(default=0)
    csr_speech_count = models.IntegerField(default=0)
    customer_speech_count = models.IntegerField(default=0)
    csr_emotion_score = models.FloatField(default=0.0)
    customer_emotion_score = models.FloatField(default=0.0)
    efficiency_score = models.IntegerField(default=0)
    final_score = models.IntegerField(default=0)
    alternative_solution_count = models.IntegerField(default=0)
    apology_ratio = models.FloatField(default=0.0)
    positive_word_ratio = models.FloatField(default=0.0)
    euphonious_word_ratio = models.FloatField(default=0.0)
    empathy_expression_ratio = models.FloatField(default=0.0)
    
    # 감정 점수 (1-5)
    emo_1_star_score = models.BooleanField(default=False)
    emo_2_star_score = models.BooleanField(default=False)
    emo_3_star_score = models.BooleanField(default=False)
    emo_4_star_score = models.BooleanField(default=False)
    emo_5_star_score = models.BooleanField(default=False)
    
    # 고객 감정 점수 (1-5)
    고객_emo_1_star_score = models.BooleanField(default=False)
    고객_emo_2_star_score = models.BooleanField(default=False)
    고객_emo_3_star_score = models.BooleanField(default=False)
    고객_emo_4_star_score = models.BooleanField(default=False)
    고객_emo_5_star_score = models.BooleanField(default=False)
    
    # 분석 결과
    strength = models.TextField(null=True, blank=True)
    weakness = models.TextField(null=True, blank=True)
    improvement = models.TextField(null=True, blank=True)
    manual_compliance_ratio = models.FloatField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # === [최종컬럼.xlsx 기반 확장 컬럼] ===
    consulting_content = models.TextField(null=True, blank=True, verbose_name="상담 대화 전체 텍스트")
    Extension = models.CharField(max_length=10, null=True, blank=True, verbose_name="파일 확장자")
    Path = models.TextField(null=True, blank=True, verbose_name="파일 저장 경로")
    Rate = models.IntegerField(null=True, blank=True, verbose_name="샘플링 레이트")
    BitDepth = models.IntegerField(null=True, blank=True, verbose_name="비트 깊이")
    Channels = models.IntegerField(null=True, blank=True, verbose_name="채널 수")
    Duration = models.IntegerField(null=True, blank=True, verbose_name="전체 프레임 수")
    MinFreq = models.IntegerField(null=True, blank=True, verbose_name="최소 주파수")
    MaxFreq = models.IntegerField(null=True, blank=True, verbose_name="최대 주파수")
    RMSLoudness = models.FloatField(null=True, blank=True, verbose_name="평균 음량 RMS")
    ZeroCrossingRate = models.FloatField(null=True, blank=True, verbose_name="영점 교차율")
    SpectralCentroid = models.FloatField(null=True, blank=True, verbose_name="스펙트럼 무게중심")
    SpectralBandwidth = models.FloatField(null=True, blank=True, verbose_name="스펙트럼 대역폭")
    SpectralFlatness = models.FloatField(null=True, blank=True, verbose_name="스펙트럼 평탄도")
    RollOff = models.FloatField(null=True, blank=True, verbose_name="롤-오프 주파수")
    Chroma_stft = models.JSONField(null=True, blank=True, verbose_name="크로마 STFT")
    SpectralContrast = models.JSONField(null=True, blank=True, verbose_name="스펙트럴 대비")
    Tonnetz = models.JSONField(null=True, blank=True, verbose_name="Tonnetz 특성")
    MFCC_0_13 = models.JSONField(null=True, blank=True, verbose_name="멜-주파수 켑스트럼 계수 0~13")
    Summary = models.TextField(null=True, blank=True, verbose_name="통화 요약 텍스트")
    Conflict = models.BooleanField(null=True, blank=True, verbose_name="갈등 플래그")
    Speaker = models.CharField(max_length=20, null=True, blank=True, verbose_name="발화자 구분")
    Sequence = models.IntegerField(null=True, blank=True, verbose_name="파일 내 발화 순번")
    StartTime = models.IntegerField(null=True, blank=True, verbose_name="발화 시작 프레임 번호")
    EndTime = models.IntegerField(null=True, blank=True, verbose_name="발화 종료 프레임 번호")
    Content = models.TextField(null=True, blank=True, verbose_name="발화 내용 텍스트")
    Sentiment = models.CharField(max_length=20, null=True, blank=True, verbose_name="감정 레이블")
    Profane = models.BooleanField(null=True, blank=True, verbose_name="비속어 사용 플래그")
    top_nouns = models.JSONField(null=True, blank=True, verbose_name="상위 명사 키워드 10개")
    sent_score = models.FloatField(null=True, blank=True, verbose_name="전반적 감정 점수")
    sent_label = models.CharField(max_length=20, null=True, blank=True, verbose_name="평균 감정 레이블")
    mid_category = models.CharField(max_length=100, null=True, blank=True, verbose_name="메인 카테고리")
    content_category = models.CharField(max_length=100, null=True, blank=True, verbose_name="서브 카테고리")
    script_phrase_ratio = models.FloatField(null=True, blank=True, verbose_name="스크립트 필수 문구 사용 비율")
    honorific_ratio = models.FloatField(null=True, blank=True, verbose_name="높임말·존댓말 비율")
    confirmation_ratio = models.FloatField(null=True, blank=True, verbose_name="확인형 멘트 비율")
    request_ratio = models.FloatField(null=True, blank=True, verbose_name="의뢰형 멘트 비율")
    conflict_flag = models.BooleanField(null=True, blank=True, verbose_name="논쟁 여부")
    
    class Meta:
        db_table = 'consulting'
        ordering = ['-created_at']


class ConsultingDetail(models.Model):
    consulting = models.ForeignKey(Consulting, on_delete=models.CASCADE, related_name='details')
    speaker = models.CharField(max_length=20)
    content = models.TextField()
    timestamp = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'consulting_detail'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.speaker} - {self.timestamp}"
