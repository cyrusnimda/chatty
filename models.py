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

class UserConfig(EmbeddedDocument):
    CHOICES = ("all", "friends", "nobody")
    who_can_see_your_age = StringField(max_length=7, choices=CHOICES, default="all")
    who_can_see_your_city = StringField(max_length=7, choices=CHOICES, default="all")
    who_can_see_your_rooms = StringField(max_length=7, choices=CHOICES, default="friends")
    who_can_see_your_friends = StringField(max_length=7, choices=CHOICES, default="nobody")
    admit_friend_requests = BooleanField(default=True)

class Achivement(Document):
    title = StringField(max_length=25)

class User(Document):
    GENDER_CHOICES = ("male", "female")

    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())
    karma = IntField(default=20)
    secret_token = UUIDField(required=True, binary=False)
    telephone_number = IntField(required=True, unique=True)
    config = EmbeddedDocumentField(UserConfig)

    name = StringField(max_length=25)
    gender = StringField(max_length=6, choices=GENDER_CHOICES)
    birthdate = DateTimeField()
    city= StringField(max_length=15)

    picture = ImageField()
    password = StringField(max_length=15)
    
    ignored_users = ListField(ReferenceField("self"))
    friends = ListField(ReferenceField("self"))
    achivements = ListField(ReferenceField(Achivement))
    
    def getId(self):
        return str(self.id)
    

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
        temporal_code = TemporalCode.objects(telephone_number=telephone_number, sms_code=str(sms_code))
        return temporal_code.count()>0


class RoomConfig(EmbeddedDocument):
    GENDER_CHOICES = ("male", "female", "all")
    users_are_puclic = BooleanField(default=False)
    min_karma = IntField(default=0)
    gender = StringField(max_length=6, choices=GENDER_CHOICES, default="all")
    max_age = IntField(default=0)
    min_age = IntField(default=0)
    
    
class Room(Document):
    TYPE_CHOICES = ("public", "private", "anonimous")
    name = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())
    room_type = StringField(max_length=10, choices=TYPE_CHOICES, default="public")
    bloqued_users = ListField(ReferenceField(User))
    muted_users = ListField(ReferenceField(User))
    owner = ReferenceField(User)
    admins = ListField(ReferenceField(User))
    users = ListField(ReferenceField(User))
    picture = ImageField()
    karma = IntField(default=20)
    config = EmbeddedDocumentField(RoomConfig)
    