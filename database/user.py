import traceback
#
from datetime import datetime
from fastapi import HTTPException, status
#
from constants.database import MongoCollections
#
from app import mongo_instance
from utilities.datetime_utilities import DatetimeUtilities
from abstractions.base_repository import BaseRepository
from models.auth import User

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.db = mongo_instance.cluster_db
        self.collection = self.db[MongoCollections.USER]
        self.collection_name = MongoCollections.USER

    def insert(self, email_id: str, hashed_password: str, username: str, ) -> User:
        start_timestamp = datetime.now()

        new_user = {
            "email_id": email_id,
            "hashed_password": hashed_password,
            "username": username,
            "disabled": False
        }
        try:
            self.logger.debug("Attempting to insert user record in database")
            user_id = str(self.collection.insert_one(new_user).inserted_id)
            end_timestamp = datetime.now()
            self.logger.info(f"Successfully retrieved document from {self.collection_name}.")
            self.logger.info(f"The query execution took {DatetimeUtilities.get_delta_in_milliseconds(start_timestamp, end_timestamp)} ms")


        except Exception:
            error = f"Error while inserting new record in {self.collection_name}"
            self.logger.error(error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error
            )
        self.logger.debug("Successfully inserted user")
        user = {
            "user_id": user_id,
            "email_id": email_id,
            "username": username,
            "disabled": False
        }
        return user

    def retrieve_record_by_email(self, email_id: str,):
        self.logger.info(f"Attempting to query {self.collection_name}")

        start_timestamp = datetime.now()

        try:
            query = {
                "email_id": email_id,
            }

            user = self.collection.find_one(query)
            end_timestamp = datetime.now()
            self.logger.debug(user)
            self.logger.info(f"Successfully retrieving document from {self.collection_name}.")

            self.logger.info(f"The query execution took {DatetimeUtilities.get_delta_in_milliseconds(start_timestamp, end_timestamp)} ms")


            if user:
                return user
            return None
        except Exception as exception:
            self.logger.error(f"Error while retrieving document from {self.collection_name} collection. Exception: {exception}\nTraceback:\n{traceback.print_exc()}")

            raise HTTPException(f"Error while retrieving document from {self.collection_name} collection.")
        
    def retrieve_record_by_username(self, username: str,):
        self.logger.info(f"Attempting to query {self.collection_name}")
        start_timestamp = datetime.now()

        try:
            query = {
                "username": username,
            }

            user = self.collection.find_one(query)
            end_timestamp = datetime.now()
            self.logger.debug(user)
            self.logger.info(f"Successfully retrieving document from {self.collection_name}.")

            self.logger.info(f"The query execution took {DatetimeUtilities.get_delta_in_milliseconds(start_timestamp, end_timestamp)} ms")

            if user:
                return user
            return None
        except Exception as exception:
            self.logger.error(f"Error while retrieving document from {self.collection_name} collection. Exception: {exception}\nTraceback:\n{traceback.print_exc()}")
            raise HTTPException(f"Error while retrieving document from {self.collection_name} collection.")