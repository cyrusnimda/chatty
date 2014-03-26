# -*- coding: utf-8 -*-
import datetime
from random import randrange


class BaseApi():
    def __init__(self, user, token):
        self.user = user
        self.token = token
        
class TemporalUser():
    def __init__(self, telephoneNumber):
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
