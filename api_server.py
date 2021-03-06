# -*- coding: utf-8 -*-
#!flask/bin/python
from flask import Flask, jsonify
from flask import make_response

from bson.objectid import ObjectId
from flask import request
from flask import abort
from models import *
from mongoengine import connect
import uuid
from time import mktime
from datetime import datetime as newDateTime
try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict
import hashlib
import os


connect('apitest')

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask("apitest")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)
    
@app.errorhandler(403)
def required(error, msg):
    return make_response(jsonify( { 'error': str(msg) + 'Required' } ), 403)



def OkResponse(msg):
	return jsonify( { 'status': "OK", 'msg': msg } ), 200
	

def NOkResponse(msg):
	return jsonify( { 'status': "NOK", 'msg': msg } ), 300

class ErrorResponse(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['status'] = 'NOK'
        rv['msg'] = self.message
        return rv

def getSignature(params, secret_token):
    del params['signature']
    paramsOrdered = OrderedDict(sorted(params.items(), key=lambda t: t[0]))
    string = ""
    for key, param in paramsOrdered.iteritems(): 
        string += param
    string += str(secret_token)
    print string
    return hashlib.sha1(string).hexdigest()
        
def check_token(request, upload=False):
    try:
        if not upload:
            user = User.objects.get(id=request.json['user'])
            userSignature = request.json['signature']
            ownSignature = getSignature(request.json, user.secret_token)
        else:
            user = User.objects.get(id=request.form['user'])
            userSignature = request.form['signature']
            string = str(request.form['user']) + str(user.secret_token)
            print string
            ownSignature = hashlib.sha1(string).hexdigest()
        
        if ownSignature != userSignature:
            print "user=",userSignature,"own=",ownSignature
            raise ErrorResponse('Secret token does not match')
        else:
            return user

    except KeyError as e:
        raise ErrorResponse("Field required: " + e.message)
    except ValidationError as e:
        raise ErrorResponse("Dont be evil: " + e.message)
    except DoesNotExist as e:
        raise ErrorResponse("This user does not exits")

@app.errorhandler(ErrorResponse)
def handle_required_field(error):
    response = jsonify(error.to_dict())
    response.status_code = 410
    return response


@app.route('/v1.0/', methods = ['GET'])
def welcolme():
    return jsonify( { 'status': "OK", 'msg': "Welcome to chatty api" } )


@app.route('/v1.0/temporal_code', methods = ['POST'])
def create_temporal_user():
    temporal_code = TemporalCode()
    try:
        temporal_code.telephone_number = request.json['telephone_number']
        temporal_code.generateSmsCode()
    except KeyError as e:
        return NOkResponse("Field required: " + e.message)

    try:
        temporal_code.save()
    except ValidationError as e:
        return NOkResponse("Field bad data: " + e.message)

    return OkResponse('Temporal code created.')


@app.route('/v1.0/user', methods = ['POST'])
def create_user():
    try:
        temporal_code = TemporalCode()
        isLegelCode = temporal_code.checkSmsCode(request.json['telephone_number'],request.json['sms_code'])
        if isLegelCode:
        	new_user = User()
        	new_user.telephone_number = request.json['telephone_number']
        	new_user.secret_token = uuid.uuid4().hex
        	new_user.config = UserConfig()
        	new_user.save()
        else:
        	print request.json['sms_code']
        	raise ErrorResponse('The code is not valid')

    except KeyError as e:
    	raise ErrorResponse("Field required: " + e.message)

    return OkResponse("User created successfully, 'user_id': " + new_user.getId() + " 'secret_token':" + new_user.secret_token )
    

@app.route('/v1.0/user', methods = ['PUT'])
def updateUser():
	user = check_token(request)
	try:
		user.name = request.json['name']
		user.gender = request.json['gender']
		user.birthdate =  newDateTime.fromtimestamp(int(request.json['birthdate']))
		user.city = request.json['city']
		user.updated_at = datetime.datetime.now()
		user.save()
	except KeyError as e:
		raise ErrorResponse("Field required: " + e.message)
	return OkResponse("User updated successfully")


@app.route('/v1.0/user/config', methods = ['PUT'])
def updateUserConfig():
    user = check_token(request)
    try:
        user_config = UserConfig()
        user_config.who_can_see_your_age = request.json['who_can_see_your_age']
        user_config.who_can_see_your_city = request.json['who_can_see_your_city']
        user_config.who_can_see_your_rooms = request.json['who_can_see_your_rooms']
        user_config.who_can_see_your_friends = request.json['who_can_see_your_friends']
        if request.json['admit_friend_requests'] == "True":
            user_config.admit_friend_requests = True
        else:
            user_config.admit_friend_requests = False
        user.config = user_config
        user.save()
    except KeyError as e:
        raise ErrorResponse("Field required: " + e.message)
    return OkResponse("User updated successfully")

@app.route('/v1.0/user/friends', methods = ['POST'])
def addFriend():
    user = check_token(request)
    try:
        friend = User.objects.get(id=request.json['friend'])
        if user == friend:
            raise ErrorResponse("The friend cant be you")
        if friend in user.friends:
            raise ErrorResponse("The friend is already in your friend list")
           
        user.friends.append(friend)
        user.save()
    except KeyError as e:
        raise ErrorResponse("Field required: " + e.message)
    except DoesNotExist as e:
        raise ErrorResponse("This friend does not exits")

    return OkResponse("Friend added successfully")

@app.route('/v1.0/user/friends', methods = ['DELETE'])
def deleteFriend():
    user = check_token(request)
    try:
        friend = User.objects.get(id=request.json['friend'])
        if user == friend:
            raise ErrorResponse("The friend cant be you")
        try:
            user.friends.remove(friend)
        except ValueError as e:
            raise ErrorResponse("This friend is not in the user friend list")

        user.save()
    except KeyError as e:
        raise ErrorResponse("Field required: " + e.message)
    except DoesNotExist as e:
        raise ErrorResponse("This friend does not exits")

    return OkResponse("Friend removed successfully")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def secure_filename(filename):
    return filename

@app.route('/v1.0/user/picture', methods = ['POST'])
def setUserPicture():
    user = check_token(request, True)
    file = request.files['file']
    if file and allowed_file(file.filename):
        picture = file
        user.picture.replace(picture)
        user.save()
        #filename = secure_filename(file.filename)
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return OkResponse("Picture upload successfully")

@app.route('/v1.0/user/ignoredUsers', methods = ['POST'])
def blockUser():
    pass

@app.route('/v1.0/user/rooms', methods = ['GET'])
def getUserRooms():
	pass
	

@app.route('/v1.0/room', methods = ['POST'])
def create_room():
    user = check_token(request)
    try:
        room = Room()
        room.name = request.json['name']
        room.room_type = request.json['room_type']
        room.owner = user
        room.admins.append(user)
        room.users.append(user)
        room.config = RoomConfig()
        room.save()
    except KeyError as e:
        raise ErrorResponse("Field required: " + e.message)
    except NotUniqueError as e:
        raise ErrorResponse("This room already exits")

    return OkResponse("Room created successfully")

@app.route('/v1.0/user', methods = ['GET'])
def getUser():
    check_required(request, "user_id")
    check_token(request)
    user = User().find(id=request.json['user_id'])
    if user == False:
        abort(404)
    return jsonify(user.showDataTo(request.json['user'])), 201


if __name__ == '__main__':
    app.run(debug = True)
    


