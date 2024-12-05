#from fastapi import FastAPI, HTTPException
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from surprise import Dataset, Reader, KNNBasic

# FastAPI 인스턴스 생성
#recommend_app = FastAPI()
recommend_router = APIRouter()

# 입력 데이터 모델 정의
class Store(BaseModel):
    storeId: int
    storeType: str
    ratingscore: float
    taste: int
    service: int
    interior: int
    cleanliness: int

class RecommendRequest(BaseModel):
    preferType: str
    preferCategories: str
    storelist: List[Store]

class RecommendResponse(BaseModel):
    recommendedStoreIds: List[int]

# 추천 API 엔드포인트
@recommend_router.post("/recommend", response_model=RecommendResponse)
def recommend_stores(request: RecommendRequest):
    """
    사용자의 선호 유형(prefer_type)과 평가 항목(prefer_categories)을 기준으로
    상위 5개 매장을 추천합니다.
    """
    # 1. 데이터 전처리
    try:
        store_data = pd.DataFrame([store.dict() for store in request.storelist])
        filtered_stores = store_data[store_data['storeType'] == request.prefer_type]

        if filtered_stores.empty:
            raise HTTPException(status_code=404, detail="선호하는 매장 유형이 없습니다.")

        # 2. Surprise 데이터셋 준비
        chosen_metric = request.prefer_categories
        if chosen_metric not in ["ratingscore", "taste", "service", "interior", "cleanliness"]:
            raise HTTPException(status_code=400, detail=f"잘못된 평가 항목: {chosen_metric}")

        reader = Reader(rating_scale=(0, 100))  # 평가 항목의 점수 범위 설정 (예: taste, service 등은 0~100)
        filtered_stores['user_id'] = 1  # 더미 사용자 ID 추가
        dataset = Dataset.load_from_df(filtered_stores[['user_id', 'storeId', chosen_metric]], reader)
        trainset = dataset.build_full_trainset()

        # 3. 추천 알고리즘 학습 및 예측
        algo = KNNBasic()
        algo.fit(trainset)

        # 4. 추천 점수 계산
        recommendations = []
        for store_id in filtered_stores['storeId'].unique():
            prediction = algo.predict(uid=1, iid=store_id)
            recommendations.append((store_id, prediction.est))

        # 5. 추천 결과 정렬 및 상위 5개 추출
        recommendations.sort(key=lambda x: x[1], reverse=True)
        top_5_stores = [store_id for store_id, score in recommendations[:5]]

        return {"recommendedStoreIds": top_5_stores}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 생성 중 오류 발생: {str(e)}")
