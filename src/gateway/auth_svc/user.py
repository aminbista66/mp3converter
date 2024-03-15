import requests
import os

def get_email(token: str):
    url = os.environ.get("AUTH_SVC", "") + "user-email/"
    res = requests.get(
        url, headers={"Authorization": "Bearer {}".format(token)}
    )
    if res.status_code != 200:
        return None, res.text

    return res.json()["email"], None