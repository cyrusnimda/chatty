# -*- coding: utf-8 -*-
import datetime
from random import randrange
import uuid
from bson.objectid import ObjectId
from mongoengine import *


class User(Document):
    name = StringField()


class TemporalCode(Document):
    telephone_number = IntField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    user = ReferenceField(User)
    sms_code = StringField()
    #self.generateSmsCode()

    def generateSmsCode(self):
        code = ""
        for i in range(4):
            rand = randrange(10)
            code += str(rand)
        self.sms_code = code
        return  True


class RoomConfig(EmbeddedDocument):
    users_are_puclic = BooleanField()
    
    
class Room(Document):
    name = StringField(required=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())
    type = StringField(max_length=50)
    bloqued_users = ListField(ReferenceField(User))
    muted_users = ListField(ReferenceField(User))
    owner = ReferenceField(User)
    admins = ListField(ReferenceField(User))
    users = ListField(ReferenceField(User))
    picture = ImageField()
    karma = IntField(default=20)
    config = EmbeddedDocumentField(RoomConfig)
    



# class BaseCRUD():
#     def __init__(self, user, token):
#         self.user = user
#         self.token = token
#
#     def save(self):
#         print "save"
#
# class BaseApi(BaseCRUD):
#     def __init__(self):
#         BaseCRUD.__init__(self)
#         self.errors = []
#
#
# class Rooma(BaseApi):
#     def __init__(self, request):
#         BaseApi.__init__(self, request)
#         self.collection = "rooms"
#         self.name = None
#         self.createtd_at = None
#         self.bloqued_users = []
#         self.silenced_users = []
#         self.public = None
#         self.owner = None
#         self.admins = []
#         self.users = []
#         self.picture = None
#         self.karma = None
#         self.config = None
#
#
# class Usera(BaseApi):
#     def __init__(self):
#         BaseApi.__init__(self)
#         self.collection = "users"
#         self.created_at = datetime.datetime.now()
#         self.updated_at = datetime.datetime.now()
#         self.name = None
#         self.birth_date = None
#         self.city = None
#         self.picture = None
#         self.igonored_users = []
#         self.friends = []
#         self.config = None
#         self.karma = 30
#         self.secret_token = None
#
#     def setAttri(self, attr, value):
#         self.updated_fields.append(attr)
#         setattr(self, attr, value)
#
#     def toJSON(self):
#         pass
#
#     def insert(self):
#         initUser = {'secret_token': self.secret_token, 'created_at': self.created_at, 'karma': self.karma, 'updated_at': self.updated_at}
#         self.id = str(self.mongo[self.collection].insert(initUser))
#
#     def generateSecretToken(self):
#         fieldName = "secret_token"
#         if not fieldName in self.updated_fields:
#             self.updated_fields.append(fieldName)
#         self.secret_token = uuid.uuid4().hex
#         return True
#
#     def getSecretToken(self):
#         return self.secret_token
#
#     def fillData(self, cursor):
#         self.karma = cursor["karma"]
#         self.secret_token = cursor['secret_token']
#
#
#     def showDataTo(self, user):
#         data = {}
#         data["karma"] = self.karma
#         return data
#
#     def find(self, id=None):
#         if id!= None:
#             try:
#                 find = { "_id": ObjectId(id) }
#             except:
#                 return False
#             cursor = self.mongo[self.collection].find(find)
#             if cursor.count()!=1:
#                 return False
#             else:
#                 self.fillData(cursor[0])
#         return self
