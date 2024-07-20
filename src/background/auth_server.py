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
from flask_bcrypt import Bcrypt
from database_functions import DatabaseFunctions 
import json
from flask import Flask, request, jsonify, abort, Response
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from auth_logic import get_token
from typing import Dict
from user_table import UserTable
from user import User
import uuid
from uuid import UUID
from user import UserInvalidData


app : Flask = Flask(__name__)
bcrypt = Bcrypt(app)
API_KEY : str = os.environ["GOOGLE_API_KEY"]
PORT : int = 5007
'''
auth_google

recieves a request to authorize a user using the google token returned from authing with google

args:
    Request
        google_token: token returned from authing with google
returns:
    response with our auth token
'''
@app.route('/auth/google', methods=['POST'])
def auth_google():
    google_token : str = request.args.get('google_token', default="NO TOKEN LOADED", type=str)
    try:
        # Verify the token using Google's API
        idinfo : Dict = id_token.verify_oauth2_token(google_token, requests.Request())

        email : str = idinfo['email']

        # Create a JWT token for the user
        jwt_token : str = jwt.encode({'email': email}, API_KEY, algorithm='HS256')
        return jsonify({'token': jwt_token})
    except ValueError:
        # Invalid token
        return jsonify({'error': 'Invalid token'}), 401

'''
get_salt_by_email

grabs a users salt for hashing the password client side so we dont send plain text password over network

args:
    request
        email: email of user to get salt for
returns:
    salt
'''
@app.route('/get_salt_by_email', methods=["GET"])
def get_salt_by_email():
    try:
        email : str = request.args.get('email', default="NO EMAIL LOADED", type=str)
    except:
        print("Request of: " + request + " is invalid")
        #Invalid request
        return abort(403)
    user : User | None = UserTable.read_user_by_email(email)
    if not user:
        abort(404)
    return jsonify({'salt': user.salt})
'''
login

endpoint for a user logging in, checks that user is in db and compares password hashes

args:
    request
        email: str email
        password_hash: password hashed with salt client side
returns:
    response of either an error or user info
'''
@app.route('/login', methods=['POST'])
def login():
    email : str = request.args.get('email', default="NO EMAIL LOADED", type=str)
    password_hash : str = request.args.get('password', default="NO PASSWORD LOADED", type=str)

    user : User = UserTable.read_user_by_email(email)
    print("ATTEMPTING TO LOGIN USER: " + json.dumps(user.to_json()))
    #PASSWORDS ARE SALTED AND HASHED! do not be scared...
    print("HASH SENT BY CLIENT: " + password_hash)
    print("HASH FOUND IN DB: " + user.password)
    if not user or not user.password == password_hash:
        print("Passwords don't match")
        return jsonify({'message': 'Invalid email or password!'}), 401
    
    token : str = get_token(user)

    response : Response = jsonify({'token': token, 'user': user.to_json()})
    print("LOGGED IN USER RETURNING RESPONSE: ")
    print(response)
    return response
'''
register

endpoint for a user registering in, checks that user is NOT db and registers

args:
    request
        user_str: json dumped to str of user
        salt: salt for the hash
returns:
    either http error 
'''
@app.route('/register', methods=['POST'])
def register():
    user_str : str = request.args.get('user', default="NO USER LOADED", type=str)
    salt : str = request.args.get('salt', default="NO SALT LOADED", type=str)
    user_json : Dict = json.loads(user_str)
    user_id : UUID = str(uuid.uuid1())
    user_json["userId"] = user_id
    try:
        user : User = User.create_with_json(user_json)
    except UserInvalidData:
        return "Bad User Data", 400
    user.salt = salt
    if UserTable.read_user_by_email(user.email):
        return jsonify({'message': 'User already exists!'}), 401
    UserTable.add_user(user)

    token : str = get_token(user)

    return jsonify({'token': token, 'userId': user_id})
if __name__ == '__main__':
    app.run(debug=True, port=PORT)