from dotenv import load_dotenv, find_dotenv
import os

def load_env(env_filename: str = '.env'):
    load_dotenv(find_dotenv(env_filename))
    return

SECRET_KEY = os.environ.get("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30