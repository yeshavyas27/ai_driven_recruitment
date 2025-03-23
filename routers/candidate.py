from fastapi import APIRouter, Path, Query, Body, status, File, UploadFile, Form, Response
from pydantic import BaseModel, AnyHttpUrl, Field
from typing import Annotated

from services.resume_service import ResumeService
from services.job_service import JobService

router = APIRouter(prefix="/candidate", tags=["Candidate"])

@router.post('/match')
async def create_file(
    file: Annotated[UploadFile, File()],
    job_link: Annotated[str, Body()],
    # TODO: auth_token: Annotated[str, Form()] | None = None,
    response_model=dict
    ):
    '''
    Uploads resume to s3 storage and parses resume file to get structured content of resume
    Scrapes a website given job link and uses model to get structued content of job
    Matches job data and resume data and returns match score
    
    '''
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file found!!'
        )

    contents = await file.read()
    #upload resume service to s3, add s3 link to user db and user's resume db (background task)
    resume_service = ResumeService(file_contents=contents)
    file_name = await resume_service.upload_resume_to_s3()
    #parse resume, add the data to resume collection
    data = resume_service.parse_and_save_resume()

    # #parse job link and get job data
    job_data = await JobService().parse_job(url=job_link)
    # TODO: calculate match score between resume data and job data
    # match_score = Match(resume_data, job_data)

    
    await file.close()
    response  ={
        "parsed_resume": data, 
        "s3_file_key": file_name,
        "parsed_job": job_data
    }
    
    return response

