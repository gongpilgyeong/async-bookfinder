'''
/app/models/__init__.py
'''
# mongodb 사용 비동기 python lib
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from app.config import get_secret

# secrets.json를 사용하는 config.py 가져오기
from app.config import MONGODB_NAME, MONGODB_URL


class MongoDB:

    '''MongoDB connect/close'''
    def __int__(self):
        self.client = None
        self.engine = None

    def connect(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.engine = AIOEngine(client=self.client, database=MONGODB_NAME)
        print("Database 연결이 성공하였습니다.")

    def close(self):
        self.client.close()
        print("Database 연결이 끊어졌습니다.")


mongodb = MongoDB()
