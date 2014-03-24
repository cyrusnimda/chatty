# -*- coding: utf-8 -*-

#!flask/bin/python
from flask import Flask, jsonify
from hashlib import sha1
import hmac
from flask import make_response
from functools import wraps
app = Flask(__name__)

			
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)


class check_karma(object):
    def __init__(self, karma, user_karma):
        self.karma = karma
        print user_karma

    def __call__(self, f):
        @wraps(f)
        def wrapped_f(*args):
            #f(*args)
            if(20 < self.karma):
                return jsonify( { 'status': "NOK", 'msg': "Be good, be god" } )
            return f(*args)
        return wrapped_f

@app.route('/v1.0/', methods = ['GET'])
@check_karma(42)
def welcolme():
	user_karma = 50;
	return jsonify( { 'status': "OK", 'msg': "Welcome to chatty api" } )

if __name__ == '__main__':
    app.run(debug = True)
    

