import requests
import os
from requests.auth import HTTPBasicAuth
from fastapi.security import HTTPBasicCredentials

def get_token(credentials: HTTPBasicCredentials):
    url = os.environ.get("AUTH_SVC", "") + "get-token/"
    res = requests.post(
        url, auth=HTTPBasicAuth(credentials.username, credentials.password)
    )

    if res.status_code != 200:
        return None, res.text

    return res.json(), None


def verify_token(token: str):
    url = os.environ.get("AUTH_SVC", "") + "verify-token/"
    res = requests.post(
        url, json={"access_token": token}
    )
    if res.status_code != 200:
        return False, res.text
    
    return True, None

def get_email(token: str):
    url = os.environ.get("AUTH_SVC", "") + "user-email/"
    res = requests.get(
        url, headers={"Authorization": token}
    )
    if res.status_code != 200:
        return None, res.text

    return res.json()["email"], None