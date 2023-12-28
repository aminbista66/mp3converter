import os

LOGIN_URI = f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/auth/login/"
VALIDATE_URI = f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/auth/verify/"