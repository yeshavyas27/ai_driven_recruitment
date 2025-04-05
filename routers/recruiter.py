# bulk upload resume pdfs, google spreadsheet support
# upload job link and get resume reccommendations
from typing import Annotated
from operator import itemgetter
import time
from fastapi import APIRouter, Depends, Query, HTTPException, status
from dependancies.auth import get_current_active_user
from services.job_service import JobService
from models.auth import User
from constants.match_criteria import MatchCriteria
from constants.auth import UserRoles
from database.resume import ResumeRepository
from services.ai_model_services.match import MatchJobResume
from utilities.s3_url_format import s3_url_format

router = APIRouter(prefix="/recruiter", tags=["Recruiter"])

#api endpoint for getting matches based on given job link, option to integrate spreadsheet of candidates and their resumes

@router.get("/find_matches")
async def find_matches(
    job_link: str,
    user: Annotated[User, Depends(get_current_active_user)],
    match_criteria: Annotated[MatchCriteria, Query(description="Matching criteria: strict - 3, moderate - 2, or flexible - 1")] = MatchCriteria.MODERATE,

):
    #validate if user has the recruiter role
    if not user.role == UserRoles.RECRUITER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only recruiters can access this API")
    #validate appropriate match criteria 
    # parse the job link
    job_data = await JobService().parse_job(url=job_link)
    # fetch all resumes
    candidate_resumes = ResumeRepository().fetch_all()
    # calculate matches of job with resume in the DB
    all_matches = []
    print(f"The match criteria is {match_criteria}. Its type is {type(match_criteria)}")
    # TODO: send job data in the constructor and match criteria, as it will create same job str everytime
    for resume in candidate_resumes:
        match_score = MatchJobResume().match(
            resume_data=resume['resume_data'],
            job_data=job_data,
            match_criteria=match_criteria
        )
        candidate_s3_resume_link = s3_url_format(s3_key=resume['s3_key'])

        all_matches.append(
            {
                "match_score": int(match_score),
                "resume_link": candidate_s3_resume_link
            }       
        )
        #added sleep due to mistral free tier limit of 1 request per second
        time.sleep(2)

    sorted_matches = sorted(all_matches, key=itemgetter('match_score'), reverse=True)

    return sorted_matches
    
