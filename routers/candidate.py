from fastapi import APIRouter, Body, status, File, UploadFile, Depends, HTTPException
from typing import Annotated
from models.auth import User

from services.resume_service import ResumeService
from services.job_service import JobService
from dependancies.auth import get_current_active_user
from database.user import UserRepository
from services.ai_model_services.match import MatchJobResume

router = APIRouter(prefix="/candidate", tags=["Candidate"])

@router.post('/match')
async def create_file(
    file: Annotated[UploadFile, File()],
    job_link: Annotated[str, Body()],
    user: Annotated[User, Depends(get_current_active_user)],
    ):
    '''
    Uploads resume to s3 storage and parses resume file to get structured content of resume.
    Scrapes a website given job link and uses model to get structued content of job.
    Matches job data and resume data and returns match score.
    
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
    resume_data, resume_id = resume_service.parse_and_save_resume(
        user_id=user.user_id,
        s3_key=file_name
    )

    # #parse job link and get job data
    job_data = await JobService().parse_job(url=job_link)
    # TODO: calculate match score between resume data and job data
    match_score = MatchJobResume().match(
            resume_data=resume_data,
            job_data=job_data,
            match_criteria="moderate"
        )

    # TODO: make a function in Resume service to update the resume with s3 link
    UserRepository().update_user_with_resume(
        s3_key=file_name,
        resume_id=resume_id,
        username=user.username
    )

    
    await file.close()
    response  ={
        "match_score": match_score,
        "parsed_resume": resume_data, 
        "s3_file_key": file_name,
        "parsed_job": job_data
    }
    
    return response

