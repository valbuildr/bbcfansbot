from peewee import *
from database import db

class LivePage(Model):
    thread_id: int = IntegerField(null=False, index=True, unique=True) # the thread's id
    title: str = CharField(max_length=1024, null=False) # title of page
    started_by: int = IntegerField(null=False) # user id of who started the page
    participating_members: str = CharField(null=False)
    active: bool = BooleanField(null=True, default=True)

    @staticmethod
    async def fetch(thread_id: int):
        try:
            return LivePage.get(LivePage.thread_id == thread_id)
        except DoesNotExist:
            return None
    
    class Meta:
        database = db