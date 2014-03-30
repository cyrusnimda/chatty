# -*- coding: utf-8 -*-
import datetime
from random import randrange
from pymongo import MongoClient
import uuid
from bson.objectid import ObjectId

class BaseCRUD():
    def __init__(self):
        mongoClient = MongoClient()
        self.mongo = mongoClient.apitest
        self.updated_fields = []
        self.id = None
        
    def getId(self):
        return self.id

    def save(self):
        print "save" 

class BaseApi(BaseCRUD):
    def __init__(self):
        BaseCRUD.__init__(self)
        self.errors = []


class Room(BaseApi):
    def __init__(self, request):
        BaseApi.__init__(self, request)
        self.collection = "rooms"
        self.name = None
        self.createtd_at = None
        self.bloqued_users = []
        self.silenced_users = []
        self.public = None
        self.owner = None
        self.admins = []
        self.users = []
        self.picture = None
        self.karma = None
        self.config = None


class User(BaseApi):
    def __init__(self):
        BaseApi.__init__(self)
        self.collection = "users"
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.name = None
        self.birth_date = None
        self.city = None
        self.picture = None
        self.igonored_users = []
        self.friends = []
        self.config = None
        self.karma = 30
        self.secret_token = None
        
        
    def toJSON(self):
        pass 

    def insert(self):
        initUser = {'secret_token': self.secret_token, 'created_at': self.created_at, 'karma': self.karma, 'updated_at': self.updated_at}
        self.id = str(self.mongo[self.collection].insert(initUser))
    
    def generateSecretToken(self):
        fieldName = "secret_token"
        if not fieldName in self.updated_fields:
            self.updated_fields.append(fieldName)
        self.secret_token = uuid.uuid4().hex
        return True
    
    def getSecretToken(self):
        return self.secret_token

    def fillData(self, cursor):
        print cursor
        self.karma = cursor["karma"]
        self.secret_token = cursor['secret_token']
        
    def showDataTo(self, user):
        data = {}
        data["karma"] = self.karma
        return data

    def find(self, id=None):
        if id!= None:
            try:
                find = { "_id": ObjectId(id) }
            except:
                return False
            cursor = self.mongo[self.collection].find(find)
            if cursor.count()!=1:
                return False
            else:
                self.fillData(cursor[0])
        return self


class TemporalUser(BaseApi):
    def __init__(self, request):
        BaseApi.__init__(self, request)
        self.telephoneNumber = None
        self.smsCode = None
        self.created_at = datetime.datetime.now()
        self.checkRequestData()
        self.collection = "temporal_users"
        
    def setSmsCode(self, smsCode):
        self.smsCode = smsCode

    def checkRequestData(self):
        if not 'telephone' in self.request.json:
            self.validateRequest = False
            self.errrors.append("Telephone is requiered.")
        else:
            self.telephoneNumber = self.request.json['telephone']
        return True
        
    def generateSmsCode(self):
        code = ""
        for i in range(4):
            rand = randrange(10)
            code = code +str(rand)
        self.smsCode = code
        return  True
        
    def checkUserAndToken(self):
        return True
        
    def toJSON(self):
        return {'telephoneNumber':self.telephoneNumber, 'smsCode': self.smsCode, 'created_at': self.created_at}

    def save(self):
        self.mongo[self.collection].insert(self.toJSON())
        
    def exists(self):
        find = { "telephoneNumber": self.telephoneNumber, "smsCode": self.smsCode }
        count = self.mongo[self.collection].find( find).count()
        return count>0
