from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.auth import User
from constants.auth import AuthConstants

from jwt.exceptions import InvalidTokenError
from database.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, AuthConstants.SECRET_KEY, algorithms=[AuthConstants.ALGORITHM])
        username = payload.get("username")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user =  UserRepository().retrieve_record_by_username(username=username)
    if user is None:
        raise credentials_exception
    
    user = User(username=user["username"], email=user["email_id"], disabled=user["disabled"], user_id=str(user["_id"]))
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
