from pydantic import BaseModel

class UserSchema(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str