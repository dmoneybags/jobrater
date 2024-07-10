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
import datetime
import json
from flask import Flask, request, jsonify, abort
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps
import os


app = Flask(__name__)
bcrypt = Bcrypt(app)
API_KEY = os.environ["google_api_key"]
SECRET_KEY = os.environ["secret_key"]

#write this
def decode_user_from_token(token):
    print("DECODING TOKEN OF: " + token)
    try:
        # Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(payload)
        # Extract user information
        user_email = payload.get("email")
        user_json_str = DatabaseFunctions.read_user_by_email(user_email)
        if not user_json_str:
            print("User not in db")
            return None
        user_info = json.loads(user_json_str)
        
        return user_info
    except jwt.ExpiredSignatureError:
        # Handle expired token
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        # Handle invalid token
        print("Invalid token")
        return None
def get_token(user, num_hours=1):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=num_hours)
    return jwt.encode({
        'email': user['email'],
        'exp': int(exp_time.timestamp())
    }, SECRET_KEY, algorithm="HS256")

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
            user = decode_user_from_token(token)
            current_user = DatabaseFunctions.read_user_by_email(user["email"])
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
@app.route('/get_salt_by_email', methods=["GET"])
def get_salt_by_email():
    try:
        email = request.args.get('email', default="NO EMAIL LOADED", type=str)
    except:
        print("Request of: " + request + " is invalid")
        #Invalid request
        return abort(403)
    result_str = DatabaseFunctions.read_user_by_email(email)
    if not result_str:
        abort(404)
    result = json.loads(result_str)
    print(result)
    return jsonify({'salt': result['salt']})
@app.route('/login', methods=['POST'])
def login():
    email = request.args.get('email', default="NO EMAIL LOADED", type=str)
    password_hash = request.args.get('password', default="NO PASSWORD LOADED", type=str)

    user_str = DatabaseFunctions.read_user_by_email(email)
    user = json.loads(user_str)
    print("ATTEMPTING TO LOGIN USER: " + json.dumps(user))
    #PASSWORDS ARE SALTED AND HASHED! do not be scared...
    print("HASH SENT BY CLIENT: " + password_hash)
    print("HASH FOUND IN DB: " + user['password'])
    if not user or not user['password'] == password_hash:
        print("Passwords don't match")
        return jsonify({'message': 'Invalid email or password!'}), 401
    
    token = get_token(user)

    user = DatabaseFunctions.read_user_by_email(user["email"])
    response = jsonify({'token': token, 'user': json.loads(user)})
    print("LOGGED IN USER RETURNING RESPONSE: ")
    print(response)
    return response
@app.route('/register', methods=['POST'])
def register():
    user_str = request.args.get('user', default="NO USER LOADED", type=str)
    salt = request.args.get('salt', default="NO SALT LOADED", type=str)
    user = json.loads(user_str)
    print(user)
    if DatabaseFunctions.read_user_by_email(user['email']):
        return jsonify({'message': 'User already exists!'}), 401
    response = DatabaseFunctions.add_user(user, salt)

    token = get_token(user)

    return jsonify({'token': token, 'userId': response[0]})
if __name__ == '__main__':
    app.run(debug=True, port=5007)