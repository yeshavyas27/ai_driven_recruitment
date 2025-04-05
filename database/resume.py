from datetime import datetime
from fastapi import HTTPException, status
#
from constants.database import MongoCollections
#
from app import mongo_instance
from utilities.datetime_utilities import DatetimeUtilities
from abstractions.base_repository import BaseRepository

class ResumeRepository(BaseRepository):
    def __init__(self):
        super().__init__()
        self.db = mongo_instance.cluster_db
        self.collection = self.db[MongoCollections.USER_RESUME_DETAILS]
        self.collection_name = MongoCollections.USER_RESUME_DETAILS

    def insert(self, resume_data, user_id, s3_key) -> str:
        start_timestamp = datetime.now()

        new_resume = {
            "resume_data": resume_data,
            "user_id": user_id,
            "s3_key": s3_key,
        }
        try:
            self.logger.debug("Attempting to insert new resume record in database")
            resume_id = str(self.collection.insert_one(new_resume).inserted_id)
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
        self.logger.debug("Successfully inserted resume data")
        
        return resume_id
    
    def fetch_all(self):
        start_timestamp = datetime.now()
        all_resumes = []
        try:
            candidate_resumes = self.collection.find({})
            for record in candidate_resumes:
                record["_id"] = str(record["_id"])
                all_resumes.append(record)

            end_timestamp = datetime.now()
            self.logger.info(f"Successfully retrieved documents from {self.collection_name}.")
            self.logger.info(f"The query execution took {DatetimeUtilities.get_delta_in_milliseconds(start_timestamp, end_timestamp)} ms")


        except Exception:
            error = f"Error while retrieving records from {self.collection_name}"
            self.logger.error(error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error
            )
            
        return all_resumes

