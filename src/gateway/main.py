from fastapi import FastAPI, Depends, UploadFile, Request, File
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from .auth_svc import access
from fastapi.exceptions import HTTPException
from .config import load_env
from .utils import upload
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(on_startup=[load_env])
security = HTTPBasic()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    token, err = access.get_token(credentials)
    if err:
        return HTTPException(detail=err, status_code=403)
    
    return token

@app.post("/convert")
def convert(req: Request, file: UploadFile | None = None):
    if not file:
        return {"message": "No file uploded"}

    token = req.headers["Authorization"]
    verified, err = access.verify_token(token.split(' ')[1])

    if err:
        raise HTTPException(detail=err, status_code=403)

    if not verified:
        raise HTTPException(detail="Invalid credentials", status_code=403)
    
    file_id, err = upload.upload_file(file)
    
    if err:
        raise HTTPException(detail=err, status_code=403)
    
    return {"file_id": file_id}