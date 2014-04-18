# -*- coding: utf-8 -*-
from models import *
import requests, json
from time import mktime
try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict
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
        elif method == "DELETE":
            r = requests.delete(url, data=data, headers=headers)

        print r.json

    def create(self, url, params):
        self.sendToAPI(url, "POST", params)

    def remove(self, url, params):
        self.sendToAPI(url, "DELETE", params)

    def update(self, url, params):
        self.sendToAPI(url, "PUT", params)

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
    id = "5346e259a853780cedaea07a"
    secret_token = "6a48bf6f24b595b1-2107458689d490ba"
    url = "user"
    name = "Josulin"
    telephone_number = 636314552
    sms_code = 1237
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
        self.params['signature'] = signature
        BaseApi.update(self, self.url, self.params)

    def updateConfig(self):
        self.params["user"] = self.id
        self.params["who_can_see_your_age"] = "nobody"
        self.params["who_can_see_your_city"] = "nobody"
        self.params["who_can_see_your_rooms"] = "nobody"
        self.params["who_can_see_your_friends"] = "nobody"
        self.params["admit_friend_requests"] = "False"
        signature = self.getSignature(self.params, self.secret_token)
        self.params['signature'] = signature
        BaseApi.update(self, "user/config", self.params)

    def addFriend(self, friend):
        self.params["user"] = self.id
        self.params["friend"] = friend
        signature = self.getSignature(self.params, self.secret_token)
        self.params['signature'] = signature
        BaseApi.create(self, "user/friends", self.params)

    def removeFriend(self, friend):
        self.params["user"] = self.id
        self.params["friend"] = friend
        signature = self.getSignature(self.params, self.secret_token)
        self.params['signature'] = signature
        BaseApi.remove(self, "user/friends", self.params)

#tc = TemporalCode()
#tc.create()

#user = UserApi()
#user.create()

#user = UserApi()
#user.update()

#user = UserApi()
#user.updateConfig()

#user = UserApi()
#user.addFriend("53502c38a8537808b8098cad")

user = UserApi()
user.removeFriend("53502c38a8537808b8098cad")