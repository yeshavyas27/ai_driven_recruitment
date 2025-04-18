from fastapi import HTTPException, status

from database.user import UserRepository
from utilities.auth_utilities import get_password_hash


class RegisterUserService:
    def __init__(self):
        pass
    
    def do(self, user_data):

        email_id = user_data.email
        password = user_data.password
        username = user_data.username
        role = user_data.role

        if UserRepository().retrieve_record_by_email(email_id=email_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please Login. User is already resgistered.")
        
        if UserRepository().retrieve_record_by_username(username=username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please pick a different username.")
        
        # hash the password
        hashed_password = get_password_hash(password=password)
        # add the record to the DB
        user = UserRepository().insert(email_id=email_id, hashed_password=hashed_password, username=username, role=role)

        return user

