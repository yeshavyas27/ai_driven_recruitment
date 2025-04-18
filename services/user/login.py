from fastapi import HTTPException, status

from database.user import UserRepository
from utilities.auth_utilities import verify_password


class LoginService:
    def __init__(self):
        pass

    def do(self, user_data):


        user = UserRepository().retrieve_record_by_username(user_data.username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(plain_password=user_data.password, hashed_password=user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user

