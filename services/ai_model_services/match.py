import re
import time

from fastapi import HTTPException, status

from app import mistral_client


class MatchJobResume:
    def __init__(self, job_data, match_criteria):

        self.model = "mistral-small-2503"
        self.client = mistral_client
        self.job_str = f'''
                        JOB_TITLE: {job_data['job_title']}

                        REQUIREMENTS:
                        - Minimum Experience: {job_data['years_of_experience']} years
                        - Education: {job_data['education']}
                        - Key/ Must have Skills: {', '.join(job_data['must_have_skills'])}
                        - Optional / Good to have skills: {', '.join(job_data['good_to_have_skills'])}
                        - Responsibilities: {job_data['job_description']}
                    '''
        self.match_criteria = match_criteria


    def match(self, resume_data):
        
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
                        YEARS OF EXPERIENCE: {resume_data.get('total_years_of_experience')}
                    '''
        

        print(f"Resume str is {resume_str}")
        print(f"Job str is {self.job_str}")
        # Start timer for inference time tracking
        start_time = time.time()
        
        # Prepare input message
        prompt = f'''
                    ## Resume-Job Matching System
                    You are an expert AI recruiter that calculates resume-job match scores (0-100) using this strict formula:

                    ### Base Criteria (80 points max)
                    1. Skills Match (40 points)
                    - 2 points per required skill explicitly mentioned in resume  
                    - Transferable skills count only at Strictness 1-2  
                    - Example: 8/10 skills = 32 points

                    2. Experience Context (40 points)
                    - 20 points for matching years of experience (prorate partial matches)  
                    - 20 points for responsibility overlap (keyword match + contextual analysis)  
                    - Example: 4/5 years + 75% responsibility match = 35 points

                    ### Bonus Points (20 points max)
                    - Job Title Similarity: +10 if current/most recent title matches  
                    - Skill Majority Bonus: +10 if >70% required skills are present  
                    - Experience Depth Bonus: +10 if candidate exceeds required years  

                    ### Strictness Modifiers
                    - Level 1: Add 15% to final score for adjacent experience/skills  
                    - Level 2: No adjustments - use raw score  
                    - Level 3: Deduct 20% for any missing required skills  

                    ### Final Score Rules
                    1. Above 80 **only if**:  
                    - All bonus conditions met  
                    - Years of experience requirement satisfied  
                    - >85% skill match  
                    2. Show calculation steps  
                    3. Always conclude with: Final Score: [number]  

                    Reason and calculate the score, and always give the final score as: ' Final Score: <match_score> '

                    Strictness Level: {self.match_criteria}.

                    Candidate Profile:
                    {resume_str}.

                    Job Description:
                    {self.job_str}.
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
        pattern = r'(?i)final score\s*\*?\*?\s*:\s*(\d+)'
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

