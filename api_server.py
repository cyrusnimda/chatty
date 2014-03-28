# -*- coding: utf-8 -*-

#!flask/bin/python
from flask import Flask, jsonify
from flask import make_response

from bson.objectid import ObjectId
from flask import request
from flask import abort
from models import *

from flask.ext.pymongo import PyMongo

app = Flask("apitest")
app.config['MONGO_chatty_DBNAME'] = 'apitest'
mongo = PyMongo(None, config_prefix='MONGO_chatty')

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


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
    if not 'telephone' in request.json:
        return jsonify( { 'status': "NOK", 'msg': "Needed data: telephone" } ), 302
    temporal_user = TemporalUser(request.json['telephone'])
    if temporal_user.validate():
        temporal_user.save()
    else:
        return jsonify( { 'status': "NOK", 'msg': "Bad Data" } ), 302
    return jsonify( { 'status': "OK", 'msg': "temporalUser created seccessfully" } ), 201


	exists = mongo.db.temporal_users.find({ "telephoneNumber": request.json['telephone'], "smsCode": request.json['sms_code'] } ).count()
	if exists==0:
		return jsonify( { 'status': "NOK", 'msg': "SMS code does not match" } ), 201
	else:
		return jsonify( { 'status': "OK", 'msg': "user created seccessfully" } ), 201
if __name__ == '__main__':
    app.run(debug = True)
    

