from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .services import analyze_consultation
from .models import Consulting
import google.generativeai as genai
import os
import json

# Create your views here.

@require_http_methods(["GET"])
def analyze_consultation_view(request, call_id):
    try:
        result = analyze_consultation(call_id)
        return JsonResponse({
            "status": "success",
            "data": result
        })
    except ValueError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)

def analyze_consulting(request, call_id):
    try:
        # 데이터베이스에서 상담 데이터 조회
        consulting = Consulting.objects.get(call_id=call_id)
        
        # 기본 점수 계산
        csr_emotion_score = consulting.csr_emotion_score
        customer_emotion_score = consulting.customer_emotion_score
        efficiency_score = consulting.efficiency_score
        manual_compliance_ratio = consulting.manual_compliance_ratio
        final_score = consulting.final_score
        
        # Gemini API 설정
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        
        # 분석을 위한 데이터 준비
        analysis_data = {
            "기본 정보": {
                "상담 ID": consulting.call_id,
                "상담 일시": consulting.call_date.strftime("%Y-%m-%d %H:%M:%S"),
                "상담 시간": f"{consulting.call_duration}초",
                "침묵 시간": f"{consulting.silence}초",
                "CSR 발화 횟수": consulting.csr_speech_count,
                "고객 발화 횟수": consulting.customer_speech_count
            },
            "감정 분석": {
                "CSR 감정 점수": csr_emotion_score,
                "고객 감정 점수": customer_emotion_score,
                "전반적 감정 점수": consulting.sent_score,
                "감정 레이블": consulting.sent_label,
                "긍정적 단어 비율": consulting.positive_word_ratio,
                "공감 표현 비율": consulting.empathy_expression_ratio,
                "사과 비율": consulting.apology_ratio
            },
            "상담 품질": {
                "효율성 점수": efficiency_score,
                "매뉴얼 준수율": manual_compliance_ratio,
                "최종 점수": final_score,
                "대안 제시 횟수": consulting.alternative_solution_count,
                "스크립트 문구 사용 비율": consulting.script_phrase_ratio,
                "높임말 사용 비율": consulting.honorific_ratio,
                "확인형 멘트 비율": consulting.confirmation_ratio,
                "의뢰형 멘트 비율": consulting.request_ratio
            },
            "음성 분석": {
                "평균 음량": consulting.RMSLoudness,
                "영점 교차율": consulting.ZeroCrossingRate,
                "스펙트럼 무게중심": consulting.SpectralCentroid,
                "스펙트럼 대역폭": consulting.SpectralBandwidth,
                "스펙트럼 평탄도": consulting.SpectralFlatness,
                "롤-오프 주파수": consulting.RollOff
            },
            "상담 내용": {
                "상담 요약": consulting.Summary,
                "주요 키워드": json.loads(consulting.top_nouns),
                "갈등 여부": consulting.Conflict,
                "논쟁 여부": consulting.conflict_flag,
                "비속어 사용": consulting.Profane,
                "메인 카테고리": consulting.mid_category,
                "서브 카테고리": consulting.content_category
            }
        }
        
        # Gemini API에 전송할 프롬프트 생성
        prompt = f"""
        다음은 고객 상담 분석 데이터입니다. 이 데이터를 바탕으로 상세한 분석을 제공해주세요.

        데이터:
        {json.dumps(analysis_data, ensure_ascii=False, indent=2)}

        다음 항목들을 포함하여 분석해주세요:
        1. 상담의 전반적인 품질 평가
        2. CSR의 감정 관리와 공감 능력 분석
        3. 고객의 감정 변화와 만족도 분석
        4. 상담 효율성과 매뉴얼 준수도 분석
        5. 음성 분석을 통한 CSR의 발화 특성 분석
        6. 상담 내용의 주요 이슈와 해결 방안 분석
        7. 개선이 필요한 부분과 구체적인 개선 방안 제시

        각 항목별로 구체적인 수치와 예시를 들어 설명해주시고, 
        특히 개선이 필요한 부분에 대해서는 실질적인 개선 방안을 제시해주세요.
        """
        
        # Gemini API 호출
        response = model.generate_content(prompt)
        
        # 응답 파싱
        analysis_result = {
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": [],
            "overall_evaluation": "",
            "detailed_scores": {
                "counselor_emotion_score": csr_emotion_score,
                "customer_emotion_score": customer_emotion_score,
                "efficiency_score": efficiency_score,
                "manual_compliance_rate": manual_compliance_ratio,
                "final_score": final_score
            }
        }
        
        # Gemini API 응답을 파싱하여 결과 구조화
        response_text = response.text
        sections = response_text.split("\n\n")
        
        for section in sections:
            if "강점" in section or "장점" in section:
                analysis_result["strengths"] = [line.strip("- ") for line in section.split("\n") if line.strip().startswith("-")]
            elif "약점" in section or "개선점" in section:
                analysis_result["weaknesses"] = [line.strip("- ") for line in section.split("\n") if line.strip().startswith("-")]
            elif "개선 방안" in section or "제안" in section:
                analysis_result["improvement_suggestions"] = [line.strip("- ") for line in section.split("\n") if line.strip().startswith("-")]
            elif "종합 평가" in section or "전체 평가" in section:
                analysis_result["overall_evaluation"] = section.split(":", 1)[1].strip() if ":" in section else section.strip()
        
        return JsonResponse(analysis_result)
        
    except Consulting.DoesNotExist:
        return JsonResponse({"error": "상담 데이터를 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
