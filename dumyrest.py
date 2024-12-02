import json
import random

# 기존의 restaurants_data.json 파일을 불러옴
with open("restaurants_data.json", "r") as file:
    restaurants_data = json.load(file)

# 더미 점수 생성 함수
def generate_dummy_scores():
    return {
        "rating_score": random.randint(1, 5),
        "taste": random.randint(0, 100),
        "service": random.randint(0, 100),
        "interior": random.randint(0, 100),
        "cleanliness": random.randint(0, 100)
    }

# 각 레스토랑에 항목별 점수를 추가
for restaurant in restaurants_data:
    restaurant.update(generate_dummy_scores())

# 업데이트된 데이터를 다시 restaurants_data.json 파일에 저장
with open("restaurants_data.json", "w") as file:
    json.dump(restaurants_data, file, indent=4)

print("restaurants_data.json 파일이 업데이트되었습니다!")
