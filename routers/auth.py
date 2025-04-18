from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from constants.auth import AuthConstants
from dependancies.auth import get_current_active_user
from models.auth import Token, User, UserCreate
from services.user.login import LoginService
from services.user.register import RegisterUserService
from utilities.auth_utilities import create_access_token
from utilities.logging_utilities import LoggingUtilities

logger = LoggingUtilities().get_logger()

router = APIRouter(tags=["Auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> Token:
    logger.info("Register User request received")

    user = RegisterUserService().do(user_data=user_data)
    access_token_expires = timedelta(minutes=AuthConstants.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = LoginService().do(user_data=form_data)

    access_token_expires = timedelta(minutes=AuthConstants.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user["username"]}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")



@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


