from fastapi import FastAPI
from reviewscore import reviewscore_router
from reviewanal import reviewanal_router
from recommend import recommend_router

app = FastAPI()

# 각 기능의 API를 통합
app.include_router(reviewscore_router, prefix="/reviewscore", tags=["Review Score"])
#app.include_router(reviewscore_app, prefix="/reviewscore", tags=["Review Score"])
app.include_router(reviewanal_router, prefix="/reviewanal", tags=["Review Analysis"])
#app.include_router(reviewanal_app, prefix="/reviewanal", tags=["Review Analysis"])
app.include_router(recommend_router, prefix="/recommend", tags=["Recommendation"])
#app.include_router(recommend_app, prefix="/recommend", tags=["Recommendation"])