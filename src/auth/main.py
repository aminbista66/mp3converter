from fastapi import FastAPI, Depends
from .config import load_env
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from . import crud, models, schemas
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

models.Base.metadata.create_all(bind=engine)

app = FastAPI(on_startup=[load_env])
security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    db: Session = Depends(get_db),
):
    user = crud.get_user_by_email(db, credentials.username)
    print(user)
    return {"message": "Message"}


@app.post("/create", response_model=schemas.UserSchema)
def create_user(user: schemas.UserSchema, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=403, detail="User with this email already exists"
        )
    return crud.create_user(db, user)
