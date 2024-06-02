import peewee
from database import db

class CroissantsModel(peewee.Model):
    user_id: int = peewee.IntegerField(null=False)
    count: int = peewee.IntegerField(null=False)

    @staticmethod
    def check_user(user_id: int) -> dict["uid": int, "croissant_count": int]:
        try:
            u = CroissantsModel.get(CroissantsModel.user_id == user_id)
        except peewee.DoesNotExist:
            u = CroissantsModel.create(user_id=user_id, count=0)
        
        return {"uid": u.user_id, "croissant_count": u.count}
    
    @staticmethod
    def add_croissant(user_id: int) -> dict["uid": int, "croissant_count": int]:
        try:
            u = CroissantsModel.get(CroissantsModel.user_id == user_id)
        except peewee.DoesNotExist:
            u = CroissantsModel.create(user_id=user_id, count=0)
        
        u.count = u.count + 1
        u.save()

        return {"uid": u.user_id, "croissant_count": u.count}

    class Meta:
        database = db