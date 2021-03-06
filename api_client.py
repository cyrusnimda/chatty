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
import sys

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
        self.id = "5346e259a853780cedaea07a"
        self.secret_token = "b195b524-6fbf-486a-ba90-d48986450721"

    def sendToAPI(self, url, method, params, files = None):
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
        elif method == "UPLOAD":
            print params
            r = requests.post(url, data=params, files=files)
            #r = requests.post(url, data=data, headers=headers, files=files)


        print r.text

    def create(self, url, params):
        self.sendToAPI(url, "POST", params)

    def remove(self, url, params):
        self.sendToAPI(url, "DELETE", params)

    def update(self, url, params):
        self.sendToAPI(url, "PUT", params)

    def upload(self, url, params, file_path):
        f = open(file_path, 'rb')
        files = {'file': f }
        self.sendToAPI(url, "UPLOAD", params, files)

    def getSignature(self, params, secret_token):
        paramsOrdered = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
        string = ""
        for key, param in paramsOrdered.iteritems(): 
            string += str(param)
        string += str(secret_token)
        print string
        return hashlib.sha1(string).hexdigest()


class TemporalCode(BaseApi):
    telephone_number = 636314996
    url = "temporal_code"

    def create(self):
        self.params["telephone_number"] = self.telephone_number
        BaseApi.create(self, self.url, self.params)

class Room(BaseApi):
    url = "room"
    name = "default"
    room_type = "public"

    def create(self):
        self.params["user"] = self.id
        self.params["name"] = self.name
        self.params["room_type"] = self.room_type
        signature = self.getSignature(self.params, self.secret_token)
        self.params['signature'] = signature
        BaseApi.create(self, self.url, self.params)

class UserApi(BaseApi):
    
    url = "user"
    name = "Josulin"
    telephone_number = 636314996
    sms_code = 3290
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

    def upload_avatar(self, avatar):
        self.params["user"] = self.id
        signature = self.getSignature(self.params, self.secret_token)
        self.params['signature'] = signature
        BaseApi.upload(self, "user/picture", self.params, avatar)

#tc = TemporalCode()
#tc.create()

#user = UserApi()
#user.create()

#user = UserApi()
#user.update()

#user = UserApi()
#user.updateConfig()

#user = UserApi()
#user.addFriend("5350f47b2024471367dea8b0")

#user = UserApi()
#user.removeFriend("5350f47b2024471367dea8b0")

options_menu = ['create_room','create_user', 'upload_avatar']

def print_options():
    print "## please select one menu option"
    for item in options_menu:
        print "[x]", item
    exit(0)

def create_room():
    required_params = 2
    if len(sys.argv) != 2+required_params:
        print "ERROR, params required"
        print "example: python", sys.argv[0], sys.argv[1], "<name> <room_type>"
    else:
        room = Room()
        room.name = sys.argv[2]
        room.room_type = sys.argv[3]
        room.create()

def upload_avatar():
    required_params = 1
    if len(sys.argv) != 2+required_params:
        print "ERROR, params required"
        print "example: python", sys.argv[0], sys.argv[1], "<file>"
    else:
        user = UserApi()
        avatar = sys.argv[2]
        user.upload_avatar(avatar)

if __name__ == "__main__":
    if len(sys.argv)<2:
        print_options()

    selected_option = sys.argv[1]
    if not selected_option in options_menu:
        print_options()

    if selected_option == "create_room":
        create_room()

    if selected_option == "upload_avatar":
        upload_avatar()
