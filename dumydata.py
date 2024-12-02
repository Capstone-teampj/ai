from faker import Faker
import random
import json

# Faker 및 기타 설정
fake = Faker()
num_restaurants = 1000  # 식당 개수

# 데이터 저장을 위한 리스트 초기화
restaurants_data = []

# 식당 데이터 생성
for i in range(1, num_restaurants + 1):
    total_tables = random.randint(0, 20)
    empty_tables = random.randint(0, total_tables) if total_tables > 0 else 0

    # 혼잡도 계산
    if total_tables > 0:
        occupancy_rate = (total_tables - empty_tables) / total_tables
        if occupancy_rate == 0:
            congestion_level = 0
        elif occupancy_rate < 0.25:
            congestion_level = 1
        elif occupancy_rate < 0.5:
            congestion_level = 2
        elif occupancy_rate < 0.75:
            congestion_level = 3
        else:
            congestion_level = 4
    else:
        congestion_level = 0  # totalTables가 0이면 congestionLevel도 0으로 설정

    restaurants_data.append({
        "id": i,
        "name": f"rest{i}",
        "address": fake.address(),
        "phone": f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
        "category": random.choice(["korean", "japanese", "chinese", "western", "vegan"]),
        "latitude": float(fake.latitude()),
        "longitude": float(fake.longitude()),
        "totalTables": total_tables,
        "emptyTables": empty_tables,
        "congestionLevel": congestion_level
    })

# 데이터 JSON 형식으로 저장하는 함수
def save_data_to_json(data, filename):
    with open(f"{filename}.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

# 데이터 저장
save_data_to_json(restaurants_data, "restaurants_data")

print("restaurants_data.json 파일로 데이터가 저장되었습니다.")
