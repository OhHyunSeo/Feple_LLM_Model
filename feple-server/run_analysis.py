import os
import json
import requests
from dotenv import load_dotenv
import django
import datetime
from django.conf import settings
from django.forms.models import model_to_dict
import decimal

# 환경 변수 로드
load_dotenv()

# Django 환경 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.consultlytics.models import Consulting
from apps.consultlytics.services import analyze_consultation

# API 키 설정
API_KEY = os.getenv('GOOGLE_API_KEY')
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={API_KEY}"

def get_consulting_data_from_db():
    """데이터베이스에서 최신 상담 데이터를 가져옵니다."""
    try:
        # Django 환경 설정
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        from apps.consultlytics.models import Consulting
        
        # 최신 상담 데이터 조회
        consulting = Consulting.objects.latest('created_at')
        
        # 모든 필드를 포함한 데이터 구조화
        data = {
            "basic_info": {
                "call_id": consulting.call_id,
                "call_date": consulting.call_date.isoformat(),
                "call_duration": consulting.call_duration,
                "silence": consulting.silence,
                "csr_speech_count": consulting.csr_speech_count,
                "customer_speech_count": consulting.customer_speech_count,
                "consulting_content": consulting.consulting_content,
                "summary": consulting.Summary
            },
            "emotion_analysis": {
                "csr_emotion": {
                    "score": consulting.csr_emotion_score,
                    "star_scores": {
                        "1_star": consulting.emo_1_star_score,
                        "2_star": consulting.emo_2_star_score,
                        "3_star": consulting.emo_3_star_score,
                        "4_star": consulting.emo_4_star_score,
                        "5_star": consulting.emo_5_star_score
                    },
                    "sentiment": consulting.Sentiment,
                    "sent_score": consulting.sent_score,
                    "sent_label": consulting.sent_label
                },
                "customer_emotion": {
                    "score": consulting.customer_emotion_score,
                    "star_scores": {
                        "1_star": consulting.고객_emo_1_star_score,
                        "2_star": consulting.고객_emo_2_star_score,
                        "3_star": consulting.고객_emo_3_star_score,
                        "4_star": consulting.고객_emo_4_star_score,
                        "5_star": consulting.고객_emo_5_star_score
                    }
                },
                "positive_word_ratio": consulting.positive_word_ratio,
                "empathy_expression_ratio": consulting.empathy_expression_ratio,
                "euphonious_word_ratio": consulting.euphonious_word_ratio,
                "apology_ratio": consulting.apology_ratio
            },
            "quality_analysis": {
                "efficiency_score": consulting.efficiency_score,
                "final_score": consulting.final_score,
                "manual_compliance_ratio": consulting.manual_compliance_ratio,
                "script_metrics": {
                    "script_phrase_ratio": consulting.script_phrase_ratio,
                    "honorific_ratio": consulting.honorific_ratio,
                    "confirmation_ratio": consulting.confirmation_ratio,
                    "request_ratio": consulting.request_ratio,
                    "alternative_solution_count": consulting.alternative_solution_count
                }
            },
            "voice_analysis": {
                "audio_characteristics": {
                    "sample_rate": consulting.Rate,
                    "bit_depth": consulting.BitDepth,
                    "channels": consulting.Channels,
                    "duration": consulting.Duration,
                    "extension": consulting.Extension,
                    "path": consulting.Path
                },
                "spectral_analysis": {
                    "min_freq": consulting.MinFreq,
                    "max_freq": consulting.MaxFreq,
                    "rms_loudness": consulting.RMSLoudness,
                    "zero_crossing_rate": consulting.ZeroCrossingRate,
                    "spectral_centroid": consulting.SpectralCentroid,
                    "spectral_bandwidth": consulting.SpectralBandwidth,
                    "spectral_flatness": consulting.SpectralFlatness,
                    "roll_off": consulting.RollOff,
                    "chroma_stft": consulting.Chroma_stft,
                    "spectral_contrast": consulting.SpectralContrast,
                    "tonnetz": consulting.Tonnetz,
                    "mfcc": consulting.MFCC_0_13
                }
            },
            "content_analysis": {
                "categories": {
                    "mid_category": consulting.mid_category,
                    "content_category": consulting.content_category
                },
                "conflict": consulting.Conflict,
                "conflict_flag": consulting.conflict_flag,
                "profanity": consulting.Profane,
                "top_nouns": consulting.top_nouns,
                "speech_sequence": {
                    "speaker": consulting.Speaker,
                    "sequence": consulting.Sequence,
                    "start_time": consulting.StartTime,
                    "end_time": consulting.EndTime,
                    "content": consulting.Content
                }
            },
            "analysis_results": {
                "strength": consulting.strength,
                "weakness": consulting.weakness,
                "improvement": consulting.improvement,
                "score": consulting.score
            }
        }
        
        return data
    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {str(e)}")
        return None

def serialize_for_llm(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: serialize_for_llm(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_for_llm(v) for v in obj]
    return obj

def analyze_consulting_data(consulting_data):
    """상담 데이터 분석 및 코칭 코멘트 생성"""
    try:
        result = analyze_consultation(consulting_data.call_id)
        return result["analysis"]
    except Exception as e:
        print(f"LLM 분석 중 오류 발생: {str(e)}")
        return None

def main():
    # 모든 상담 데이터 조회
    consulting_data_list = Consulting.objects.all().order_by('call_id')
    
    if not consulting_data_list:
        print("분석할 데이터가 없습니다.")
        return
        
    all_results = []
    # 각 상담 데이터별 분석 실행
    for consulting_data in consulting_data_list:
        print(f"\n{'='*50}")
        print(f"상담 데이터 분석 결과 (CALL_ID: {consulting_data.call_id})")
        print(f"{'='*50}")
        
        # 분석 실행
        analysis_result = analyze_consulting_data(consulting_data)
        
        # 분석 결과 출력
        print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
        print(f"\n{'='*50}\n")
        
        # 파일 저장용 리스트에 추가
        all_results.append({
            "call_id": consulting_data.call_id,
            "analysis": analysis_result
        })

    # 모든 결과를 파일로 저장
    with open("analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("\n분석 결과가 analysis_results.json 파일에 저장되었습니다.")

if __name__ == "__main__":
    main()

# (임시) 모델 리스트 출력 함수는 주석 처리 또는 삭제
# def print_available_gemini_models():
#     import requests
#     API_KEY = ""
#     url = "https://generativelanguage.googleapis.com/v1/models"
#     headers = {"x-goog-api-key": API_KEY}
#     try:
#         response = requests.get(url, headers=headers)
#         print("\n=== Gemini 모델 리스트 조회 결과 ===")
#         print(response.status_code)
#         print(response.text)
#     except Exception as e:
#         print(f"모델 리스트 조회 중 오류 발생: {str(e)}")



        