from fastapi import FastAPI, Depends, Response
from .config import load_env
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from . import crud, models, schemas
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from .utils import create_access_token, verify_access_token
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta


models.Base.metadata.create_all(bind=engine)

app = FastAPI(on_startup=[load_env])
security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/get-token")
def get_token(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_email(db, credentials.username)
    if not user:
        raise HTTPException(status_code=403, detail="Invalid email or password")
    if str(user.password) != str(credentials.password):
        raise HTTPException(status_code=403, detail="Invalid email or password")

    token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": token} 

@app.post("/verify-token")
def verify_token(token: schemas.Token):
    data = verify_access_token(token.access_token)
    if not data:
        return HTTPException(status_code=403, detail="Token failed verification")
    return data


@app.post("/create-user", response_model=schemas.UserSchema)
def create_user(user: schemas.UserSchema, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=403, detail="User with this email already exists"
        )
    return crud.create_user(db, user)
