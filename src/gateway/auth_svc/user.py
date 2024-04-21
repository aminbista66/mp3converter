import os
import requests

def create(email: str, password: str):
    url = os.environ.get("AUTH_SVC", "") + "create-user/"
    response = requests.post(url, json={"email": email, "password": password})
    return response.json()