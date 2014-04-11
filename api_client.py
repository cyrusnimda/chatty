# -*- coding: utf-8 -*-
from models import *
import requests, json
from time import mktime
from collections import OrderedDict
import hashlib

class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


class BaseApi():
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.version = "v1.0"
        self.params = {}

    def sendToAPI(self, url, method, params):
        url = "%s/%s/%s" %(self.base_url, self.version, url)
        print url

        data = json.dumps(params)
        headers = {'content-type': 'application/json'}
        if method == "POST":
            r = requests.post(url, data, headers=headers)
        elif method == "PUT":
            r = requests.put(url, data, headers=headers)
        elif method == "GET":
            r = requests.get(url, data, headers=headers)

        print r.json

    def create(self, url, params):
        self.sendToAPI(self.url, "POST", params)

    def update(self, url, params):
        self.sendToAPI(self.url, "PUT", params)

    def getSignature(self, params, secret_token):
        paramsOrdered = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
        secret_token = ""
        for key, param in paramsOrdered.iteritems(): 
            secret_token += param
        secret_token += secret_token
        return hashlib.sha1(secret_token).hexdigest()


class TemporalCode(BaseApi):
    telephone_number = 636314996
    url = "temporal_code"

    def create(self):
        self.params["telephone_number"] = self.telephone_number
        BaseApi.create(self, self.url, self.params)

class UserApi(BaseApi):
    id = "5347c4017950c334997277da"
    secret_token = "71de95e2a2fb4894bd737c8ba0323b85"
    url = "user"
    name = "Josulin"
    telephone_number = 636314996
    sms_code = 5141
    gender = "male"
    city = "Bilbao"
    birthdate = datetime.date(1983, 4, 21)

    def create(self):
        self.params["telephone_number"] = self.telephone_number
        self.params["sms_code"] = self.sms_code
        BaseApi.create(self, self.url, self.params)

    def update(self):
        self.params["user"] = self.id
        self.params["name"] = self.name
        self.params["gender"] = self.gender
        self.params["city"] = self.city
        self.params["birthdate"] = json.dumps(self.birthdate, cls=DateEncoder)
        signature = self.getSignature(self.params, self.secret_token)
        print signature
        self.params['signature'] = signature
        BaseApi.update(self, self.url, self.params)

#tc = TemporalCode()
#tc.create()

#user = UserApi()
#user.create()

user = UserApi()
user.update()