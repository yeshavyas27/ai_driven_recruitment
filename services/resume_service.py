import boto3
from pdfminer.high_level import extract_text
from io import BytesIO
from uuid import uuid4
from fastapi import HTTPException, status
import os
from abstractions.base_service import BaseService
from services.ai_model_services.resume_parse import ParseResume

class ResumeService(BaseService):
    def __init__(self, file_contents):
        super().__init__()
        self.file_contents = file_contents

    async def upload_resume_to_s3(self):
        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(os.getenv("AWS_S3_BUCKET"))
        #chnage the file name to include the username
        file_name = f'{uuid4()}.pdf'
        await self.__s3_upload(key=file_name)
        return file_name


    def parse_and_save_resume(self):
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
        # TODO: save the resume parsed data to DB
        
        return parsed_resume
    
    async def __s3_upload(self, key: str):
        self.logger.info(f'Uploading {key} to s3')
        self.bucket.put_object(Key=key, Body=self.file_contents, ContentType='application/pdf', ContentDisposition='inline')

        
    
    
