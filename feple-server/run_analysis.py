import os
import json
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
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
from apps.consultlytics.utils import (
    get_all_consulting_data, 
    save_analysis_results_to_file, 
    format_analysis_result,
    chunk_list,
    validate_api_key
)

# 로깅 설정
logger = logging.getLogger(__name__)

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

def analyze_single_consultation(consulting_data: Consulting) -> Dict[str, Any]:
    """
    단일 상담 데이터 분석
    
    Args:
        consulting_data: 상담 데이터 객체
        
    Returns:
        분석 결과 딕셔너리
    """
    try:
        logger.info(f"상담 분석 시작: {consulting_data.call_id}")
        result = analyze_consultation(consulting_data.call_id)
        
        if result:
            logger.info(f"상담 분석 완료: {consulting_data.call_id}")
            return format_analysis_result(consulting_data.call_id, result.get("analysis", {}))
        else:
            logger.error(f"상담 분석 실패: {consulting_data.call_id}")
            return format_analysis_result(consulting_data.call_id, {})
            
    except Exception as e:
        logger.error(f"상담 분석 중 오류 발생 ({consulting_data.call_id}): {str(e)}")
        return format_analysis_result(consulting_data.call_id, {})


def analyze_consultations_batch(consulting_data_list: List[Consulting], 
                              max_workers: int = 3,
                              batch_size: int = 10) -> List[Dict[str, Any]]:
    """
    배치 단위로 상담 데이터를 분석 (병렬 처리)
    
    Args:
        consulting_data_list: 분석할 상담 데이터 리스트
        max_workers: 최대 동시 실행 스레드 수
        batch_size: 배치 크기
        
    Returns:
        분석 결과 리스트
    """
    all_results = []
    total_count = len(consulting_data_list)
    
    logger.info(f"총 {total_count}개의 상담 데이터 분석 시작")
    
    # 배치 단위로 처리
    for batch_num, batch in enumerate(chunk_list(consulting_data_list, batch_size), 1):
        logger.info(f"배치 {batch_num} 처리 중 ({len(batch)}개 항목)")
        
        # 병렬 처리
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_consulting = {
                executor.submit(analyze_single_consultation, consulting): consulting 
                for consulting in batch
            }
            
            batch_results = []
            for future in as_completed(future_to_consulting):
                consulting = future_to_consulting[future]
                try:
                    result = future.result()
                    batch_results.append(result)
                    
                    # 진행 상황 출력
                    completed = len(all_results) + len(batch_results)
                    logger.info(f"진행률: {completed}/{total_count} ({completed/total_count*100:.1f}%)")
                    
                except Exception as e:
                    logger.error(f"배치 처리 중 오류 ({consulting.call_id}): {str(e)}")
                    batch_results.append(format_analysis_result(consulting.call_id, {}))
        
        all_results.extend(batch_results)
        
        # 배치 완료 로그
        logger.info(f"배치 {batch_num} 완료")
    
    logger.info(f"전체 분석 완료: {len(all_results)}개 결과")
    return all_results


def print_analysis_summary(results: List[Dict[str, Any]]) -> None:
    """분석 결과 요약 출력"""
    total_count = len(results)
    successful_count = sum(1 for r in results if r.get("status") == "completed")
    failed_count = total_count - successful_count
    
    print(f"\n{'='*60}")
    print(f"분석 결과 요약")
    print(f"{'='*60}")
    print(f"총 분석 요청: {total_count}개")
    print(f"성공: {successful_count}개")
    print(f"실패: {failed_count}개")
    print(f"성공률: {successful_count/total_count*100:.1f}%" if total_count > 0 else "성공률: 0%")
    print(f"{'='*60}\n")


def main():
    """메인 함수"""
    try:
        # API 키 유효성 검사
        if not validate_api_key():
            logger.error("Google API 키가 설정되지 않았거나 유효하지 않습니다.")
            print("Google API 키를 확인해주세요.")
            return
        
        # 상담 데이터 조회
        logger.info("상담 데이터 조회 시작")
        consulting_data_list = get_all_consulting_data()
        
        if not consulting_data_list:
            logger.warning("분석할 데이터가 없습니다.")
            print("분석할 데이터가 없습니다.")
            return
        
        logger.info(f"총 {len(consulting_data_list)}개의 상담 데이터 발견")
        
        # 병렬 분석 실행
        print(f"상담 데이터 분석을 시작합니다... (총 {len(consulting_data_list)}개)")
        all_results = analyze_consultations_batch(
            consulting_data_list, 
            max_workers=3,  # API 제한을 고려하여 동시 요청 수 제한
            batch_size=10
        )
        
        # 결과 요약 출력
        print_analysis_summary(all_results)
        
        # 개별 결과 출력 (처음 3개만)
        for i, result in enumerate(all_results[:3]):
            print(f"\n{'='*50}")
            print(f"상담 데이터 분석 결과 {i+1} (CALL_ID: {result.get('call_id', 'Unknown')})")
            print(f"{'='*50}")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print(f"{'='*50}\n")
        
        if len(all_results) > 3:
            print(f"... 외 {len(all_results) - 3}개 결과는 파일을 확인해주세요.")
        
        # 결과 파일 저장
        if save_analysis_results_to_file(all_results):
            print("✅ 분석 결과가 analysis_results.json 파일에 저장되었습니다.")
        else:
            print("❌ 파일 저장 중 오류가 발생했습니다.")
            
    except Exception as e:
        logger.error(f"메인 함수 실행 중 오류: {str(e)}")
        print(f"프로그램 실행 중 오류가 발생했습니다: {str(e)}")

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



        