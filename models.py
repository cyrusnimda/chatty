# -*- coding: utf-8 -*-
import datetime
from random import randrange
import uuid
from bson.objectid import ObjectId
from mongoengine import *
import json


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class User(Document):
    name = StringField()
    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())
    karma = IntField(default=20)
    secret_token = UUIDField(required=True)
    telephone_number = IntField(required=True, unique=True)

    def getId(self):
        return str(self.id)
        #return JSONEncoder().encode(self.id)
    

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

    def checkSmsCode(self, telephone_number, sms_code):
        temporal_code = TemporalCode.objects(telephone_number=telephone_number, sms_code=sms_code)
        return temporal_code.count()>0


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
    