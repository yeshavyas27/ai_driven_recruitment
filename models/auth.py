from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    # user_id: str


class User(BaseModel):
    username: str
    email: str 
    disabled: bool | None = None
    user_id: str


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


