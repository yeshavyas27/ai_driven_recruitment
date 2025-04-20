import ast
import json
import os
import time
from typing import Any, Dict

from langchain_agentql.document_loaders import AgentQLLoader
from mistralai import Mistral

from app import mistral_client


class ParseJob:
    def __init__(self):

        self.model = "mistral-large-latest"
        self.client = mistral_client
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'parsed_job_format.json')

        with open(file_path, 'r') as file:
            self.parsed_job_dict_format = file.read()

    def parse_job_data_agentql(self, job_link):
        api_key = os.getenv("AGENTQL_API_KEY")
        loader = AgentQLLoader(
            url=job_link,
            query="""
                {
                job_data(all data related to the job listing){
                    company_name(the organisation which is hiring)
                    job_title(name of role or position)
                    years_of_experience(expected experience, it could be range as well like 0-2)
                    salary(stiped or compensation or pay for this job)
                    location(city, state, country or remote)
                    job_description(includes details about the responsiblities, job overview and other context related to job like skills and experience context)
                    education(expected education)[]
                    good_to_have_skills(all kinds technical skills required for the role, this may be implicit and present in job description)[]
                    must_have_skills(explicitly mentioned skills that the candidate must have)[]
                }
            }
            """,
            is_scroll_to_bottom_enabled=True,
            api_key=api_key
        )
        docs = loader.load()
        parsed_job = ast.literal_eval(docs[0].page_content)["job_data"]

        return parsed_job

    def parse_job_data(self, page_data):
        start_time = time.time()

        chat_response = self.client.chat.complete(
            model = self.model,
            messages = [
                {
                    "role": "user",
                    "content": f'''
                            Parse the data / job listing into the follwing format:
                            {self.parsed_job_dict_format}.
                            All the data to be extracted is present in the data below. Convert it from unstructured form to the format mentioned above. Extract key skills and all skills from the description as well.
                            Data/ job listing: {page_data}
                    
                    
                    '''
                },],
                response_format = {
                "type": "json_object", }

        )

        # Calculate inference time
        inference_time = time.time() - start_time

        # Extract response content
        response_content = chat_response.choices[0].message.content
        # Get token counts
        input_tokens = chat_response.usage.prompt_tokens
        output_tokens = chat_response.usage.completion_tokens
        total_tokens = chat_response.usage.total_tokens
        parsed_job = json.loads(response_content)
        response = {
            **parsed_job,
            # "metrics": {
            #     "inference_time_seconds": inference_time,
            #     "input_tokens": input_tokens,
            #     "output_tokens": output_tokens,
            #     "total_tokens": total_tokens
            # }
        }
        return response
