# bulk upload resume pdfs, google spreadsheet support
# upload job link and get resume reccommendations
import time
from operator import itemgetter
from typing import Annotated

from fastapi import (APIRouter, Depends, File, HTTPException, Query,
                     UploadFile, status)

from constants.auth import UserRoles
from constants.match_criteria import MatchCriteria
from database.resume import ResumeRepository
from dependancies.auth import get_current_active_user
from models.auth import User
from services.ai_model_services.match import MatchJobResume
from services.job_service import JobService
from services.resume_service import ResumeService
from utilities.aws_s3_utilities import s3_url_format

router = APIRouter(prefix="/recruiter", tags=["Recruiter"])

#api endpoint for getting matches based on given job link, optionally upload resume pdfs to match the job to
# to include existing resumes in the DB, add a query param to the endpoint

@router.post("/find_matches")
async def find_matches(
    job_link: str,
    user: Annotated[User, Depends(get_current_active_user)],
    match_criteria: Annotated[MatchCriteria, Query(description="Matching criteria: strict - 3, moderate - 2, or flexible - 1")] = MatchCriteria.MODERATE,
    resume_files: Annotated[list[UploadFile], File(description="Optionally upload resumes to match the job with")] = None,
    include_existing_resumes: bool = True,
):
    #validate if user has the recruiter role
    if not user.role == UserRoles.RECRUITER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only recruiters can access this API")
    #validate appropriate match criteria 
    # parse the job link
    job_data = await JobService().parse_job(url=job_link)
    # fetch all resumes
    candidate_resumes = []

    if resume_files:
        for file in resume_files:
            contents = await file.read()
            resume_service = ResumeService(file_contents=contents)
            # upload the resume to s3 and get the s3 key
            s3_key = await resume_service.upload_resume_to_s3()
            resume ={ "resume_data": resume_service.parse(), "s3_key": s3_key}
            candidate_resumes.append(resume)

    if include_existing_resumes:
        db_candidate_resumes = ResumeRepository().fetch_all()

    if resume_files and include_existing_resumes:
        all_resumes = [*candidate_resumes, *db_candidate_resumes]
    elif resume_files:
        all_resumes = candidate_resumes
    elif include_existing_resumes:  
        all_resumes = db_candidate_resumes
    else:
        all_resumes = []

    if not all_resumes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No resumes to match the job with")
    
    # calculate matches of job with resume in the DB
    all_matches = []
    print(f"The match criteria is {match_criteria}. Its type is {type(match_criteria)}")
    # TODO: send job data in the constructor and match criteria, as it will create same job str everytime
    match_job_resume_service = MatchJobResume(job_data=job_data, match_criteria=match_criteria)
    for resume in all_resumes:
        match_score = match_job_resume_service.match(
            resume_data=resume['resume_data'],
        )
        candidate_s3_resume_link = s3_url_format(s3_key=resume['s3_key'])

        all_matches.append(
            {
                "match_score": int(match_score),
                "resume_link": candidate_s3_resume_link if candidate_s3_resume_link else None,
                "user_profile": resume['resume_data'],
            }       
        )
        #added sleep due to mistral free tier limit of 1 request per second
        time.sleep(2)

    sorted_matches = sorted(all_matches, key=itemgetter('match_score'), reverse=True)

    return sorted_matches

# add job/ save the job
# shortlist cadidates for a job
# get all jobs for a recruiter
# get all candidates/matches for a job
    
