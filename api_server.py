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

connect('apitest')

app = Flask("apitest")

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)
    
@app.errorhandler(403)
def required(error, msg):
    return make_response(jsonify( { 'error': str(msg) + 'Required' } ), 403)


def user_have_enoght_karma(needed_karma, user_karma):
    return needed_karma < user_karma


def check_karma(needed_karma, user_karma):
    if needed_karma < user_karma:
        return make_response(jsonify({ 'status': "NOK", 'msg': "Don't have enought karma" }),500)


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


@app.route('/v1.0/user/rooms', methods = ['GET'])
def getUserRooms():
	pass
	
		
def check_token(request):
	try:
		user = User.objects.get(id=request.json['user'])

		print user.to_json()
		if user.secret_token != uuid.UUID(request.json['secret_token']):
			raise ErrorResponse('Secret token does not match')
		else:
			return user

	except KeyError as e:
		raise ErrorResponse("Field required: " + e.message)
	except ValidationError as e:
		raise ErrorResponse("Dont be evil: " + e.message)
	except DoesNotExist as e:
		raise ErrorResponse("This user does not exits")

@app.route('/v1.0/user', methods = ['GET'])
def getUser():
	check_required(request, "user_id")
	check_token(request)
	user = User().find(id=request.json['user_id'])
	if user == False:
		abort(404)
	return jsonify(user.showDataTo(request.json['user'])), 201
	


@app.route('/v1.0/room', methods = ['POST'])
def create_room():
	#check_token(request)
	room = Room(name="telegram")
	room.save()
	return jsonify( { 'status': "OK", 'msg': "Room created seccessfully" } ), 201
	
if __name__ == '__main__':
    app.run(debug = True)
    


