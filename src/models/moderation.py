from peewee import *
from random import choices
from string import ascii_letters, digits
import discord
from database import db
from datetime import datetime
from zoneinfo import ZoneInfo

class ActionType:
    note = 0
    warn = 1
    mute = 2
    kick = 3
    ban = 4

def get_id(type: ActionType):
    ending: str = ""
    match type:
        case ActionType.note: ending = "-n"
        case ActionType.warn: ending = "-w"
        case ActionType.mute: ending = "-m"
        case ActionType.kick: ending = "-k"
        case ActionType.ban: ending = "-b"
    
    r = "".join(choices(ascii_letters + digits, k=5))
    return r + ending

class ModerationNotes(Model):
    id: str = CharField(max_length=7, # the note id, always ending in '-n'
                        unique=True,
                        null=False,
                        index=True)
    note: str = CharField(max_length=1024, # the note itself
                          null=False)
    on: int = IntegerField(null=False) # the id of the user that the note is on
    by: int = IntegerField(null=False) # the id of the user who created the note
    at: datetime = DateTimeField(null=False) # the time that the note was added

    class Meta:
        database = db
    
    @staticmethod
    async def add(note: str, on: discord.Member, by: discord.Member):
        id = get_id(ActionType.note)
        now = datetime.now(ZoneInfo("Europe/London"))

        try:
            return ModerationNotes.create(id=id, note=note, on=on.id, by=by.id, at=now)
        except IntegrityError:
            return None
    
    @staticmethod
    async def remove(id: str):
        try:
            note = ModerationNotes.get(ModerationNotes.id == id)
            note.delete_instance()
            return True
        except DoesNotExist:
            return False