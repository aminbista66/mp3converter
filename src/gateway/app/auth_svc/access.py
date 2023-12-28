import requests
from app.config import constants
import json


def login(request):
    credentials = {
        "username": request.data.get("username", None),
        "password": request.data.get("password", None),
    }

    response = requests.post(constants.LOGIN_URI, data=credentials)
    if response.status_code == 200:
        return json.loads(response.json())["access"], None
    else:
        return None, (response.json(), response.status_code)

def validate(request):
    token = request.headers.get('Authorization')
    if token:
        if not token.startswith('Bearer '):
            return None, "Invalid token"
        else:
            token = token[len('Bearer '):] # get all from the len('Bearer ')
            response = requests.post(constants.VALIDATE_URI, data={"token": token})
            if response.status_code == 200:
                return token, None
            else:
                return None, response.text
    else:
        return None, "Token missing"