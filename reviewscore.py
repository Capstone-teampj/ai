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
#reviewscore_app = FastAPI()
reviewscore_router = APIRouter()

# 요청 데이터 모델 정의
class Review(BaseModel):
    id: int
    content: str
    rating: int
    authorUsername: str
    storeName: str
    storeId: int

# 응답 데이터 모델 정의
class StoreScore(BaseModel):
    storeId: int
    ratingscore: float  # 리뷰의 평균 평점
    taste: int
    service: int
    interior: int
    cleanliness: int

# GPT를 사용하여 리뷰를 분석하는 함수
def analyze_review_with_gpt(review_text: str) -> dict:
    """
    GPT를 사용하여 리뷰 텍스트를 분석.
    review_text: 리뷰 텍스트
    """
    prompt = f"""
    아래 리뷰에 대해 각 항목(taste, service, interior, cleanliness)에 대해 다음 기준으로 평가하세요:
    - 언급이 없으면 2
    - 긍정적인 경우 1
    - 부정적인 경우 0
    
    리뷰: "{review_text}"
    결과는 JSON 형식으로 반환:
    {{
        "taste": [0, 1, or 2],
        "service": [0, 1, or 2],
        "interior": [0, 1, or 2],
        "cleanliness": [0, 1, or 2]
    }}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        # GPT 응답에서 JSON 추출
        result = json.loads(response['choices'][0]['message']['content'])
        return result
    except Exception as e:
        print(f"GPT 분석 중 오류 발생: {e}")
        return {"taste": 2, "service": 2, "interior": 2, "cleanliness": 2}

# 매장 점수를 계산하는 함수
def calculate_store_scores(reviews: List[Review]) -> StoreScore:
    """
    여러 리뷰를 기반으로 매장 점수를 계산.
    reviews: 특정 매장의 리뷰 리스트
    """
    # 초기값을 1/2로 설정 (긍정적 평가 비율로 계산)
    total_scores = {"taste": 0.5, "service": 0.5, "interior": 0.5, "cleanliness": 0.5}
    total_counts = {"taste": 1, "service": 1, "interior": 1, "cleanliness": 1}  # 각 카테고리의 분모

    total_rating = 0  # 전체 리뷰의 rating 합계
    review_count = 0  # 리뷰 개수

    for review in reviews:
        review_analysis = analyze_review_with_gpt(review.content)  # GPT 분석 결과

        for category in total_scores.keys():
            if review_analysis[category] == 1:
                # 긍정(1) → 분자와 분모 각각 증가
                total_scores[category] += 1
                total_counts[category] += 1
            elif review_analysis[category] == 0:
                # 부정(0) → 분모만 증가
                total_counts[category] += 1
            # 언급 없음(2)인 경우에는 아무것도 증가시키지 않음

        # 리뷰 개수는 모든 카테고리에 동일하게 증가
        review_count += 1

        # 리뷰의 rating 합산
        total_rating += review.rating

    # 점수를 백분위로 변환 (소수점 첫째 자리에서 반올림)
    for category in total_scores.keys():
        # (긍정적인 평가 비율 / 총 리뷰 수)로 점수 계산
        score = total_scores[category] / total_counts[category]
        total_scores[category] = round(score * 100)  # 백분위로 변환하여 0~100으로 스케일링

    # 평균 평점 계산
    average_rating = round(total_rating / review_count, 2)  # 소수점 둘째 자리까지 반올림

    # StoreScore 형식으로 반환
    return StoreScore(
        storeId=reviews[0].storeId,
        ratingscore=average_rating,
        taste=total_scores["taste"],
        service=total_scores["service"],
        interior=total_scores["interior"],
        cleanliness=total_scores["cleanliness"],
    )



# 특정 매장 리뷰 분석 API
@reviewscore_router.post("/scoring_reviews/", response_model=List[StoreScore])
async def scoring_reviews(reviews: List[Review]):
    """
    특정 매장에 대한 리뷰를 분석하고 점수를 계산.
    reviews: 리뷰 리스트
    """
    try:
        # 리뷰를 매장별로 그룹화 (여기서는 하나의 매장만 있다고 가정)
        if not reviews:
            raise HTTPException(status_code=400, detail="리뷰 데이터가 없습니다.")

        store_scores = calculate_store_scores(reviews)
        return [store_scores]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))