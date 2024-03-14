from fastapi import FastAPI, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from .auth_svc import access
from fastapi.exceptions import HTTPException
from .config import load_env

app = FastAPI(on_startup=[load_env])
security = HTTPBasic()


@app.post("/login")
def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    token, err = access.get_token(credentials)
    if err:
        return HTTPException(detail=err, status_code=403)
    
    return token