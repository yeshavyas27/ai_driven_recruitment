import time
import json
import re
from app import mistral_client
from constants.match_criteria import MatchCriteria
from fastapi import HTTPException, status

class MatchJobResume:
    def __init__(self):

        self.model = "open-mistral-7b"
        self.client = mistral_client


    def match(self, resume_data, job_data, match_criteria):
        
        resume_str = f'''
                        SKILLS: {', '.join(resume_data['skills'] + 
                                        [skill for exp in resume_data['experience'] for skill in exp.get('skills_related', [])] +
                                        [skill for project in resume_data.get('accomplishments and projects', []) for skill in project.get('skills_related', [])])}

                        EXPERIENCE: {' '.join([
                            f"{exp.get('role', 'N/A')} at {exp.get('organization', 'N/A')} ({exp.get('timeline', {}).get('start', 'N/A')}-{exp.get('timeline', {}).get('end', 'N/A')}): " + 
                            '. '.join(exp.get('details', [])) + ' ' +
                            'Skills used: ' + ', '.join(exp.get('skills_related', [])) 
                            for exp in resume_data['experience']
                        ])}

                        EDUCATION: {', '.join([
                            course for edu in resume_data.get('education', []) 
                            for course in edu.get('coursework', [])
                        ])}

                        PROJECTS AND ACCOMPLISHMENTS: {' '.join([
                            f"{proj.get('name', 'N/A')}: " + '. '.join(proj.get('details', [])) + ' ' +
                            'Skills demonstrated: ' + ', '.join(proj.get('skills_related', [])) 
                            for proj in resume_data.get('accomplishments and projects', [])
                        ])}
                    '''
        
        job_str = f'''
                        JOB_TITLE: {job_data['job_title']}

                        REQUIREMENTS:
                        - Minimum Experience: {job_data['years_of_experience']} years
                        - Education: {job_data['education']}
                        - Key/ Must have Skills: {', '.join(job_data['must_have_skills'])}
                        - Optional / Good to have skills: {', '.join(job_data['good_to_have_skills'])}
                        - Responsibilities: {job_data['job_description']}
                    '''

        print(f"Resume str is {resume_str}")
        print(f"Job str is {job_str}")
        # Start timer for inference time tracking
        start_time = time.time()
        
        # Prepare input message
        prompt = f'''
                    You are an expert technical recruiter AI. Your only task is to analyze job descriptions and candidate profiles to calculate a numerical match score from 0-100. 

                    Given the following information:
                    - Job Description (containing required skills, experience, and qualifications)
                    - Candidate Profile (containing the candidate's skills, experience, and background)
                    - Strictness Level (1=Lenient, 2=Moderate, 3=Strict)

                    Evaluate how well the candidate matches the job requirements based on the strictness level:
                    - Level 1 (Lenient): Consider potential, transferable skills, and learning ability
                    - Level 2 (Moderate): Balance between required skills and growth potential
                    - Level 3 (Strict): Rigid matching of technical requirements with limited flexibility

                    Reason and calculate the score, and always give the final score as: 'Final Score: <match_score>'

                    Strictness Level: {match_criteria}.

                    Candidate Profile:
                    {resume_str}.

                    Job Description:
                    {job_str}.
                    [/INST]
                '''


        # Make API call
        chat_response = self.client.chat.complete(
        model = self.model,
        messages = [
            {
                "role": "user",
                "content": prompt
            },],)

        # Calculate inference time
        inference_time = time.time() - start_time
        model_output = chat_response.choices[0].message.content
        print(f"Model output is {model_output}")
        pattern = r'Final Score:\s*(\d+)'
        try:
            match_score = re.search(pattern, model_output)
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Error while calculating match score"
        )

        if match_score:
            match_score = match_score.group(1)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Error while calculating match score"
        )

        # Get token counts
        input_tokens = chat_response.usage.prompt_tokens
        output_tokens = chat_response.usage.completion_tokens
        total_tokens = chat_response.usage.total_tokens
        # response = {
        #     "match_score": match_score,
        #     # "metrics": {
        #     #     "inference_time_seconds": inference_time,
        #     #     "input_tokens": input_tokens,
        #     #     "output_tokens": output_tokens,
        #     #     "total_tokens": total_tokens
        #     # }
        # }
        return match_score

