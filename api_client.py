# -*- coding: utf-8 -*-
from models import *

import requests, json

class BaseApi():
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.version = "v1.0"

    def sendToAPI(self, url, method, params):
        url = "%s/%s/%s" %(self.base_url, self.version, url)
        print url

        data = json.dumps(params)
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data, headers=headers)
        print r.json


class UserApi(BaseApi):
    url = "temporal_code"
    name = ""

    def send(self):
        method = "POST"
        params = {"name": self.name}
        self.sendToAPI(self.url, method, params)


user = UserApi()
user.name = "Josulin"
user.send()