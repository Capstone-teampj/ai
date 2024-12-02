import os
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드
print(os.environ.get('API_KEY'))