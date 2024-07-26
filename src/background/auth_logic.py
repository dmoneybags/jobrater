import os
import datetime
from flask import Flask, request, jsonify, abort, Response
from database_functions import DatabaseFunctions
import json
import jwt
from functools import wraps
from typing import Callable, Tuple, Dict
from user import User
from user_table import UserTable

SECRET_KEY: str = os.environ["secret_key"]

'''
token_required

function wrapper that requires the function it wraps to have a token in the auth headers

evaluates that the token exists and is valid

args:
    f: Vallable
returns:
    http error if theres no token, allows the function to run as normal if there is
'''
def token_required(f: Callable) -> Callable:
    #Thought, what to do with current user
    @wraps(f)
    def decorated(*args, **kwargs)  -> Tuple[Response, int]:
        if 'Authorization' in request.headers:
            token: str = request.headers['Authorization']
            print("Token found of ")
            print(token)
            if not token:
                print("token not found in headers")
                return jsonify({'message': 'Token is missing!'}), 401
        else:
            print("Authorization not found in headers")
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            user : User | None = decode_user_from_token(token)
            print("Loaded user of ")
            print(user)
            if user is None:
                #CONVERSATION:
                #An old cached token could cause this and server didn't really error. if for some reason read user by email errored
                #it would return 500 but I think 401 is correct error
                print("Couldn't decode user, returning 401")
                return jsonify({'message': 'User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated
'''
decode_user_from_token

retrieves the user from the token and returns it

args:
    token: str jwt token
returns:
    user from token or none if token is invalid
'''
def decode_user_from_token(token : str) -> User | None:
    print("DECODING TOKEN OF: ")
    print(token)
    try:
        # Decode the JWT
        payload : Dict[str, any] = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(payload)
        # Extract user information
        user_email : str = payload.get("email")
        
        return UserTable.read_user_by_email(user_email)
    #CONVERSATION:
    #Do higher level functions need to know why token is bad? seems that no matter what the reason is you're going to
    #reauth anyways. I'm not aware of any errors that would cause us not to send response to client to clear auth cache and
    #re-register/sign in
    except jwt.ExpiredSignatureError:
        # Handle expired token
        print("Token has expired")
        return None
    
    except jwt.InvalidTokenError:
        # Handle invalid token
        print("Invalid token")
        return None
'''
get_token

gets a token for a user object with an amount of time to make the token last for

args:
    user: user object to create token for
    num_hours: num hours for token to persist
returns:
    jwt token
'''
def get_token(user : User, num_hours : int=1) -> str:
    exp_time : datetime.datetime = datetime.datetime.utcnow() + datetime.timedelta(hours=num_hours)
    return jwt.encode({
        'email': user.email,
        'exp': int(exp_time.timestamp())
    }, SECRET_KEY, algorithm="HS256")