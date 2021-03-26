from dataclasses import dataclass
from datetime import datetime
from utils.mongo_db import MongoDB


@dataclass
class Video:
    title: str
    channel_name: str
    url: str
    comment: str
    create_at: datetime

    def __init__(self, title, channel_name, url, comment, create_at):
        self.mongo_db = MongoDB()
        self.title = title
        self.channel_name = channel_name
        self.url = url
        self.comment = comment
        self.create_at = create_at

    def insert(self):
        col = self.mongo_db.db["videos"]
        col.insert_one(
            {
                "title": self.title,
                "channelName": self.channel_name,
                "url": self.url,
                "comment": self.comment,
                "createdAt": self.create_at
            }
        )

