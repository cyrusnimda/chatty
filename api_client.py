# -*- coding: utf-8 -*-
from models import *

import requests, json

from time import mktime

class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


class BaseApi():
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.version = "v1.0"

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


class TemporalCode(BaseApi):
    telephone_number = 636314996
    url = "temporal_code"

    def create(self):
        method = "POST"
        params = {}
        params["telephone_number"] = self.telephone_number
        self.sendToAPI(self.url, "POST", params)

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
        params = {}
        params["telephone_number"] = self.telephone_number
        params["sms_code"] = self.sms_code
        self.sendToAPI(self.url, "POST", params)

    def update(self):
        params = {}
        params["user"] = self.id
        params["secret_token"] = self.secret_token
        params["name"] = self.name
        params["gender"] = self.gender
        params["city"] = self.city
        params["birthdate"] = json.dumps(self.birthdate, cls=DateEncoder)
        self.sendToAPI(self.url, "PUT", params)

#tc = TemporalCode()
#tc.create()

#user = UserApi()
#user.create()

user = UserApi()
user.update()