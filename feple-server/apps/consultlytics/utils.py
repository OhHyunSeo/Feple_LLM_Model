"""
Consultlytics 공통 유틸리티 모듈
코드 중복을 제거하고 재사용 가능한 함수들을 제공합니다.
"""

import os
import json
import datetime
import decimal
from typing import Dict, Any, List, Optional
import logging
from django.forms.models import model_to_dict
from .models import Consulting

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """JSON 직렬화를 위한 커스텀 인코더"""
    
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)


def serialize_for_llm(obj: Any) -> Any:
    """LLM 분석을 위한 데이터 직렬화"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: serialize_for_llm(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_for_llm(v) for v in obj]
    return obj


def get_consulting_data_structured(consulting: Consulting) -> Dict[str, Any]:
    """상담 데이터를 구조화된 형태로 변환"""
    try:
        data = {
            "basic_info": {
                "call_id": consulting.call_id,
                "call_date": consulting.call_date.isoformat() if consulting.call_date else None,
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
        
        return serialize_for_llm(data)
        
    except Exception as e:
        logger.error(f"상담 데이터 구조화 중 오류 발생: {str(e)}")
        return {}


def get_all_consulting_data(limit: Optional[int] = None) -> List[Consulting]:
    """모든 상담 데이터를 조회 (페이징 지원)"""
    try:
        queryset = Consulting.objects.all().order_by('call_id')
        if limit:
            queryset = queryset[:limit]
        return list(queryset)
    except Exception as e:
        logger.error(f"상담 데이터 조회 중 오류 발생: {str(e)}")
        return []


def get_latest_consulting_data() -> Optional[Consulting]:
    """최신 상담 데이터 조회"""
    try:
        return Consulting.objects.latest('created_at')
    except Consulting.DoesNotExist:
        logger.warning("상담 데이터가 존재하지 않습니다.")
        return None
    except Exception as e:
        logger.error(f"최신 상담 데이터 조회 중 오류 발생: {str(e)}")
        return None


def save_analysis_results_to_file(results: List[Dict], filename: str = "analysis_results.json") -> bool:
    """분석 결과를 파일로 저장"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        logger.info(f"분석 결과가 {filename} 파일에 저장되었습니다.")
        return True
    except Exception as e:
        logger.error(f"분석 결과 파일 저장 중 오류 발생: {str(e)}")
        return False


def validate_api_key() -> bool:
    """API 키 유효성 검사"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error("GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")
        return False
    
    if len(api_key) < 10:  # 최소 길이 검사
        logger.error("GOOGLE_API_KEY가 너무 짧습니다.")
        return False
    
    return True


def get_db_connection_info() -> Dict[str, str]:
    """데이터베이스 연결 정보 반환"""
    return {
        "analysis_db_uri": os.getenv("ANALYSIS_DB_URI", "mysql://root:1234@localhost:3306/feple_analysis"),
        "main_db_uri": f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '1234')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'feple')}"
    }


def format_analysis_result(call_id: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """분석 결과를 표준 형식으로 포맷팅"""
    return {
        "call_id": call_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "analysis": analysis_result,
        "status": "completed" if analysis_result else "failed"
    }


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """리스트를 청크 단위로 분할"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def safe_get_attribute(obj: Any, attr_name: str, default_value: Any = None) -> Any:
    """안전한 속성 접근"""
    try:
        return getattr(obj, attr_name, default_value)
    except Exception as e:
        logger.warning(f"속성 '{attr_name}' 접근 중 오류: {str(e)}")
        return default_value 