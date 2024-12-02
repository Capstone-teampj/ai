#from fastapi import FastAPI, HTTPException
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
import json
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드
# GPT API 키 설정
openai.api_key = os.environ.get('API_KEY')
# FastAPI 인스턴스 생성
#reviewanal_app = FastAPI()
reviewanal_router = APIRouter()

# 요청 데이터 모델 정의
class Review(BaseModel):
    id: int
    content: str
    authorUsername: str
    storeName: str
    storeId: int

# 응답 데이터 모델 정의
class ReviewAnalysis(BaseModel):
    important_reviews: dict
    summary: str

# GPT를 사용하여 리뷰 분석하는 함수
def analyze_reviews_with_gpt(reviews: List[str]) -> dict:
    """
    GPT를 사용하여 리뷰 분석: 긍정적/부정적 리뷰에서 중요한 리뷰 추출 및 총평 생성.
    reviews: 특정 매장의 모든 리뷰 텍스트 리스트
    """
    prompt = f"""
    아래는 한 매장의 리뷰 목록입니다.
    1. 전체리뷰에 대해서 긍정적인 리뷰 중에서 특히 중요한 리뷰를 5개 이내로 뽑아주세요.
    2. 전체리뷰에 대해서 부정적인 리뷰 중에서 특히 중요한 리뷰를 5개 이내로 뽑아주세요.
    3. 만약 한 리뷰에 긍정적인 평가와 부정적인 평가가 모두 있다면 문장을 분리해서 긍정,부정으로 분류한후 보여주세요.
    4. 모든 리뷰를 요약하여 매장에 대한 총평을 작성해주고 이에 따른 식당의 개선방향성을 제시해주세요.
    결과를 JSON 형식으로 반환하세요.

    리뷰 목록:
    {reviews}

    결과 예시:
    {{
        "important_reviews": {{
            "positive": [
                "음식이 정말 맛있고 직원들이 친절했어요.",
                "분위기가 매우 아늑하고 좋은 경험이었어요."
            ],
            "negative": [
                "음식이 너무 짜서 먹기 힘들었어요.",
                "주문이 너무 오래 걸렸어요."
            ]
        }},
        "summary": "대체로 음식과 분위기가 좋다는 평가가 많았지만, 일부 고객은 서비스 속도와 음식 간에 일관성이 없다고 지적했습니다. 주문에 걸리는 시간을 줄여본다면 좋을 것 같습니다."
    }}
    """
    try:
        # OpenAI GPT-3.5-turbo를 사용하여 분석
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # GPT 응답에서 JSON 추출
        result = json.loads(response['choices'][0]['message']['content'])
        return result
    except Exception as e:
        print(f"GPT 분석 중 오류 발생: {e}")
        return {
            "important_reviews": {"positive": [], "negative": []},
            "summary": "총평 생성 실패."
        }


# 리뷰 분석 API
@reviewanal_router.post("/analyze_reviews/", response_model=ReviewAnalysis)
async def analyze_reviews(reviews: List[Review]):
    """
    특정 매장에 대한 리뷰를 분석하고 중요한 리뷰와 총평을 반환합니다.
    reviews: 리뷰 리스트
    """
    try:
        # 리뷰 텍스트 리스트 추출
        reviews_text = [review.content for review in reviews]

        # GPT를 사용하여 중요한 리뷰 및 총평 분석
        analysis = analyze_reviews_with_gpt(reviews_text)
        
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

