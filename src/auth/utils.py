from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from .config import SECRET_KEY, ALGORITHM

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY)
    except JWTError as e:
        print(e)
        return None
    return data