import requests
import os
import json
from requests.auth import HTTPBasicAuth
from fastapi.security import HTTPBasicCredentials


def get_token(credentials: HTTPBasicCredentials):
    auth_svc_url = os.environ.get("AUTH_SVC", "") + "get-token/"
    res = requests.post(
        auth_svc_url, auth=HTTPBasicAuth(credentials.username, credentials.password)
    )

    if res.status_code != 200:
        return None, res.text

    return res.json(), None
