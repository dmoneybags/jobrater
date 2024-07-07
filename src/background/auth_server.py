'''
Exectution flow

signup.html
\/
\/
auth.js
\/
\/
auth_server.py
'''

import bcrypt
import database_functions
import datetime
import json
from flask import Flask, request, jsonify
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
import os

app = Flask(__name__)
API_KEY = os.environ["google_api_key"]
SECRET_KEY = os.environ["secret_key"]

@app.route('/auth/google', methods=['POST'])
def auth_google():
    token = request.args.get('token', default="NO TOKEN LOADED", type=str)
    try:
        # Verify the token using Google's API
        idinfo = id_token.verify_oauth2_token(token, requests.Request())

        email = idinfo['email']

        # Create a JWT token for the user
        jwt_token = jwt.encode({'email': email}, API_KEY, algorithm='HS256')
        return jsonify({'token': jwt_token})
    except ValueError:
        # Invalid token
        return jsonify({'error': 'Invalid token'}), 401
def token_required(f):
    #Thought, what to do with current user
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Extract token from header

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = database_functions.DatabaseFunctions.read_user_by_email()
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
'''
Login function, called when a user has to login due to a token expiring
ARGS: 
'''
@app.route('/login', methods=['POST'])
def login():
    email = request.args.get('email', default="NO EMAIL LOADED", type=str)
    password = request.args.get('password', default="NO PASSWORD LOADED", type=str)

    user = database_functions.DatabaseFunctions.read_user_by_email(email)

    if not user or not bcrypt.check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid email or password!'}), 401

    token = jwt.encode({
        'email': user['email'],
        'exp': datetime.datetime.time() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({'token': token})
@app.route('/register', methods=['POST'])
def register():
    user_str = request.args.get('user', default="NO COMPANY LOADED", type=str)
    user = json.loads(user_str)
    print(user)
    if database_functions.DatabaseFunctions.read_user_by_email(user['email']):
        return jsonify({'message': 'User already exists!'}), 401
    database_functions.DatabaseFunctions.add_user(user)

    token = jwt.encode({
        'email': user['email'],
        'exp': datetime.datetime() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({'token': token})

if __name__ == '__main__':
    app.run(debug=True, port=5007)