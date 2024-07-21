import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'background')))

# Now import the user module
from user import User
import bcrypt
import json
from uuid import UUID, uuid1
from typing import Dict

test_user_json = {
    "userId": str(uuid1()),
    "email": "dandemoney@gmail.com",
    "password": "Xdfgh1012",
    "firstName": "Daniel",
    "lastName": "DeMoney",
    "salt": "!#%!%!%!#%!"
}
test_google_user_json = {
    "userId": str(uuid1()),
    "email": "dandemoney@gmail.com",
    "firstName": "Daniel",
    "lastName": "DeMoney",
    "googleId": "135ni4ntn3o2t"
}

def test_json_loading(test_json: Dict) -> None:
    print("Testing Traditional user")
    user : User = User.create_with_json(test_json)
    assert(str(user.user_id) == test_json["userId"])
    assert(user.email == test_json["email"])
    assert(user.password == test_json["password"])
    assert(user.first_name == test_json["firstName"])
    assert(user.last_name == test_json["lastName"])
    assert(user.salt == test_json["salt"])
    print("Test passed")
def test_google_json_loading(test_json: Dict) -> None:
    print("Testing Google user")
    user : User = User.create_with_json(test_json)
    assert(str(user.user_id) == test_json["userId"])
    assert(user.email == test_json["email"])
    assert(user.google_id == test_json["googleId"])
    assert(user.first_name == test_json["firstName"])
    assert(user.last_name == test_json["lastName"])
    print("Test passed")
if __name__ == "__main__":
    test_json_loading(test_user_json)
    test_google_json_loading(test_google_user_json)