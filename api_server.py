# -*- coding: utf-8 -*-

#!flask/bin/python
from flask import Flask, jsonify
from flask import make_response

from bson.objectid import ObjectId
from flask import request
from flask import abort
from models import *
from mongoengine import connect

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

@app.route('/v1.0/', methods = ['GET'])
def welcolme():
    user_karma = 50;
    if not user_have_enoght_karma(20, user_karma):
        return make_response(jsonify({ 'status': "NOK", 'msg': "Don't have enought karma" }),500)
    return jsonify( { 'status': "OK", 'msg': "Welcome to chatty api" } )

@app.route('/v1.0/user', methods = ['POST'])
def create_user():
    if not request.json or not 'nick' in request.json:
        abort(400)
    user = {
        'nick': request.json['nick'],
        'description': request.json.get('cuidad', "Bilbao")
    }
    mongo.db.users.insert(user)
    return jsonify( { 'status': "OK", 'msg': "User created successfully" } ), 201

@app.route('/v1.0/temporal_user', methods = ['POST'])
def create_temporal_user():
    temporal_user = TemporalUser(request)
    if temporal_user.validate():
        temporal_user.generateSmsCode()
        temporal_user.save()
        return jsonify( { 'status': "OK", 'msg': "temporalUser created seccessfully" } ), 201
    else:
        return jsonify( { 'status': "NOK", 'msg': "Bad Data" } ), 302
    
@app.route('/v1.0/activate_acount', methods = ['POST'])
def activate_acount():
	temporal_user = TemporalUser(request)
	if not 'smsCode' in request.json:
		return jsonify( { 'status': "NOK", 'msg': "smsCode is required" } ), 302
	else:
		temporal_user.setSmsCode(request.json['smsCode'])
		
	if temporal_user.exists():
		user = User(request)
		user.generateSecretToken()
		user.insert()
		return jsonify( { 'status': "OK", 'msg': "user created seccessfully", 'id' : user.getId(), 'secret_token' : user.getSecretToken() } ), 201
	else:
		return jsonify( { 'status': "NOK", 'msg': "SMS code does not match" } ), 302

@app.route('/v1.0/user/rooms', methods = ['GET'])
def getUserRooms():
	pass
	
	
class RequiredField(Exception):
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
	
@app.errorhandler(RequiredField)
def handle_required_field(error):
    response = jsonify(error.to_dict())
    response.status_code = 410
    return response
	
def check_required(request, field_required):
	if not field_required in request.json:
		raise RequiredField('Field ' + field_required + ' is required')
		
def check_token(request):
	if not "user" in request.json:
		raise RequiredField('Field user is required')
	if not "token" in request.json:
		raise RequiredField('Field token is required')
	
	user =User()
	user.find(id=request.json['user'])
	if user.getSecretToken() != request.json['token']:
		raise RequiredField('Secret token does not match')
	
@app.route('/v1.0/user', methods = ['GET'])
def getUser():
	check_required(request, "user_id")
	check_token(request)
	user = User().find(id=request.json['user_id'])
	if user == False:
		abort(404)
	return jsonify(user.showDataTo(request.json['user'])), 201
	
@app.route('/v1.0/user', methods = ['PUT'])
def updateUser():
	check_token(request)
	user = User().find(id=request.json['user'])
	params = request.json.copy()
	params.pop('user', 0)
	params.pop('token', 0)
	for param in params:
		if not hasattr(user, param):
			raise RequiredField(param +' is not a legal parameter. Dont be evil')
		else:
			user.setAttri(param, request.json[param])
	print user.updated_fields
	print user.karma
	return jsonify(user.showDataTo(request.json['user'])), 201

@app.route('/v1.0/room', methods = ['POST'])
def create_room():
	#check_token(request)
	room = Room(name="telegram")
	room.save()
	return jsonify( { 'status': "OK", 'msg': "Room created seccessfully" } ), 201
	
if __name__ == '__main__':
    app.run(debug = True)
    


