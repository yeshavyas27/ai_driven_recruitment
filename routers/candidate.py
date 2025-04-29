from typing import Annotated

from fastapi import (APIRouter, Body, Depends, File, HTTPException, Query,
                     UploadFile, status)

from constants.match_criteria import MatchCriteria
from database.resume import ResumeRepository
from database.user import UserRepository
from dependancies.auth import get_current_active_user
from models.auth import User
from models.resume import Resume
from services.ai_model_services.match import MatchJobResume
from services.job_service import JobService
from services.resume_service import ResumeService
from utilities.aws_s3_utilities import get_s3_key_from_url, s3_url_format

router = APIRouter(prefix="/candidate", tags=["Candidate"])


@router.post('/parse_resume')
async def parse_resume(
    file: Annotated[UploadFile, File()],
    user: Annotated[User, Depends(get_current_active_user)],
    ):
    
    # save resume to s3 and return the parsed resume data
    # TODO: if resume already exists and new given then delete old one, and save new one

    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file found!!'
        )

    contents = await file.read()
    #upload resume service to s3, add s3 link to user db and user's resume db (background task)
    resume_service = ResumeService(file_contents=contents)

    resume_data = ResumeRepository().fetch_by_user_id(user_id=user.user_id)
    if resume_data:
        if resume_data["s3_key"]:
            is_success = resume_service.delete_resume_in_s3(file_name=resume_data["s3_key"])
            if not is_success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Unable to delete old resume from s3'
                )
        
    file_name = await resume_service.upload_resume_to_s3()
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unable to upload resume to s3'
        )
    
    parsed_resume = resume_service.parse()

    return{
        "parsed_resume": parsed_resume,
        "s3_link":  s3_url_format(s3_key=file_name)
    }

@router.post('/save_profile')
async def save_parsed_resume(
    parsed_resume: Annotated[Resume, Body()],
    user: Annotated[User, Depends(get_current_active_user)],
    s3_link: Annotated[str, Body()] =  None,
    ):
    # save the canidate profile, add this data to mongodb
    resume_id = ResumeService().save(parsed_resume.model_dump(), user.user_id, get_s3_key_from_url(s3_link))
    
    UserRepository().update_user_with_resume(
        resume_id=resume_id,
        username=user.username,
        s3_key=get_s3_key_from_url(s3_link)
    )

    return {"message": "Profile saved successfully"}

@router.get('/get_profile')
async def get_profile(
    user: Annotated[User, Depends(get_current_active_user)],
    ):
    resume_data = ResumeRepository().fetch_by_user_id(user_id=user.user_id)
    # get the candidate profile, get this data from mongodb
    # based on the user_id find the in the resume collection and return the data 

    return {
        "parsed_resume": resume_data["resume_data"],
        "s3_link": s3_url_format(s3_key=resume_data["s3_key"]) if resume_data["s3_key"] else None,
    }
    

@router.put('/update_profile')
async def update_profile(
    parsed_resume: Annotated[Resume, Body()],
    user: Annotated[User, Depends(get_current_active_user)],
    s3_link: Annotated[str, Body()] =  None,
    ):
    # update the candidate profile, update this data to mongodb
    print("resume_data", parsed_resume.model_dump())
    ResumeRepository().update_resume_data_by_user_id(
        user_id=user.user_id,       
        resume_data=parsed_resume.model_dump(),
        s3_key=get_s3_key_from_url(s3_link) if s3_link else None
    )

    return {
        "message": "Profile updated successfully", 
    }

@router.get('/match_with_job')
async def match_with_job(
    job_link: Annotated[str, Query()],
    user: Annotated[User, Depends(get_current_active_user)],
    match_criteria: Annotated[MatchCriteria, Query(description="Matching criteria: strict - 3, moderate - 2, or flexible - 1")] = MatchCriteria.MODERATE
    ):  
    # get the candidate profile, get this data from mongodb
    # match the candidate profile with the job link and return the match score
    resume_data = ResumeRepository().fetch_by_user_id(user_id=user.user_id)
    if not resume_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No profile details found!! Please upload your resume first/ fill in profile data.'
        )
    # parse the job link
    job_data = await JobService().parse_job(url=job_link)
    # calculate matches of job with resume in the DB        
    match_score = MatchJobResume(job_data=job_data,match_criteria=match_criteria).match(
        resume_data=resume_data['resume_data'], 
        
    )
    return match_score
    

# test/demo endpoint to test the match score between resume and job data, saves no data
@router.post('/demo_match')
async def demo_match(
    file: Annotated[UploadFile, File()],
    job_link: Annotated[str, Body()],
    match_criteria: Annotated[MatchCriteria, Query(description="Matching criteria: strict - 3, moderate - 2, or flexible - 1")] = MatchCriteria.MODERATE
    ):
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file found!!'
        )

    contents = await file.read()
    resume_service = ResumeService(file_contents=contents)
    resume_data = resume_service.parse()

    # #parse job link and get job data
    job_data = await JobService().parse_job(url=job_link)
    # TODO: calculate match score between resume data and job data
    match_score = MatchJobResume(job_data=job_data,match_criteria=match_criteria).match(
        resume_data=resume_data['resume_data'], 
    )
    
    await file.close()
    response  ={
        "match_score": match_score,
        "parsed_resume": resume_data, 
        "parsed_job": job_data
    }
    
    return response

