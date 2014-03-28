# -*- coding: utf-8 -*-
import datetime
from random import randrange
from pymongo import MongoClient

class BaseCRUD():
    def __init__(self):
        mongoClient = MongoClient()
        self.mongo = mongoClient.apitest

    def save(self):
        print "save" 

class BaseApi(BaseCRUD):
    def __init__(self, user, token):
        self.user = user
        self.token = token


class TemporalUser(BaseCRUD):
    def __init__(self, telephoneNumber):
        BaseCRUD.__init__(self)
        self.telephoneNumber = telephoneNumber
        self.smsCode = self.generateSmsCode()
        self.created_at = datetime.datetime.now()
        
    def generateSmsCode(self):
        code = ""
        for i in range(4):
            rand = randrange(10)
            code = code +str(rand)
        return  code
        
    def validate(self):
        return True
        
    def toJSON(self):
        return {'telephoneNumber':self.telephoneNumber, 'smsCode': self.smsCode, 'created_at': self.created_at}

    def save(self):
        self.mongo.temporal_user.insert(self.toJSON())
