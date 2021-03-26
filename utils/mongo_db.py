import pymongo
from model.singleton import Singleton
from config import MONGO_DB_URL


class MongoDB(metaclass=Singleton):
    def __init__(self) -> None:
        super().__init__()
        self.client = pymongo.MongoClient(MONGO_DB_URL)
        self.db = self.client["youtubeBot"]
