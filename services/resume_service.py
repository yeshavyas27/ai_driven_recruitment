import os
from io import BytesIO
from uuid import uuid4

import boto3
from fastapi import HTTPException, status
from pdfminer.high_level import extract_text

from abstractions.base_service import BaseService
from database.resume import ResumeRepository
from services.ai_model_services.resume_parse import ParseResume


class ResumeService(BaseService):
    def __init__(self, file_contents = None):
        super().__init__()
        self.file_contents = file_contents

    async def upload_resume_to_s3(self):
        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(os.getenv("AWS_S3_BUCKET"))
        #chnage the file name to include the username
        file_name = f'{uuid4()}.pdf'
        await self.__s3_upload(key=file_name)
        return file_name

    def delete_resume_in_s3(self, file_name):
        try:
            s3 = boto3.client('s3')
            s3.delete_object(Bucket=os.getenv("AWS_S3_BUCKET"), Key=file_name)
            self.logger.info(f'{file_name} deleted from s3 successfully')
            return True
        except Exception as e:
            self.logger.error(f"Error deleting file from S3: {e}")
            return False
    

    def parse_and_save_resume(self, user_id, s3_key):
        # Convert bytes to BytesIO for pdfminer
        pdf_file = BytesIO(self.file_contents)
        
        # Extract text from the PDF
        try:
            text = extract_text(pdf_file)
            # Remove newlines and backslashes
            text = text.replace("\n", "").replace("\\", "")

            self.logger.debug(f"Resume text extracted using pdfminer successfully")
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unable to extract text from the pdf file'
        )
        parsed_resume = ParseResume().parse(resume_data=text)
        resume_id = ResumeRepository().insert(
            resume_data=parsed_resume,
            user_id=user_id,
            s3_key=s3_key
        )

        return parsed_resume, resume_id
    
    def parse(self):
        pdf_file = BytesIO(self.file_contents)
        
        # Extract text from the PDF
        try:
            text = extract_text(pdf_file)
            # Remove newlines and backslashes
            text = text.replace("\n", "").replace("\\", "")

            self.logger.debug(f"Resume text extracted using pdfminer successfully")
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unable to extract text from the pdf file'
        )
        parsed_resume = ParseResume().parse(resume_data=text)

        return parsed_resume
    
    def save(self, parsed_resume, user_id, s3_key):
        # TODO: check if resume already exists in the db, if yes then update the resume data

        resume_id = ResumeRepository().insert(
            resume_data=parsed_resume,
            user_id=user_id,
            s3_key=s3_key
        )
        return resume_id

    
    async def __s3_upload(self, key: str):
        self.logger.info(f'Uploading {key} to s3')
        self.bucket.put_object(Key=key, Body=self.file_contents, ContentType='application/pdf', ContentDisposition='inline')

        
    
    
