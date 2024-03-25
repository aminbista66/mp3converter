from fastapi import FastAPI, Depends, UploadFile, Request, File, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from .auth_svc import access
from fastapi.exceptions import HTTPException
from .config import load_env
from .utils import upload, download
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


app = FastAPI(on_startup=[load_env])
security = HTTPBasic()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    verified, err = access.verify_token(token.split(" ")[1])

    if err:
        raise HTTPException(detail=err, status_code=403)

    if not verified:
        raise HTTPException(detail="Invalid credentials", status_code=403)

    user, err = access.get_email(token)

    if err:
        raise HTTPException(detail=err, status_code=403)

    file_id, err = upload.upload_file(file, user)

    if err:
        raise HTTPException(detail=err, status_code=403)

    return {"file_id": file_id}


@app.get("/download/{mp3_id}")
def download_mp3(mp3_id: str):
    # Set response headers to stream the file
    headers = {"Content-Disposition": f"attachment; filename={mp3_id}.mp3"}
    return StreamingResponse(
        download.stream_file(mp3_id), media_type="audio/mpeg", headers=headers
    )


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return {"status": "ok"}