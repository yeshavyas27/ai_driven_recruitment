from mistralai import Mistral
import time
from typing import Dict, Any
import os
import json
class ParseJob:
    def __init__(self):

        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.model = "mistral-large-latest"
        self.client = Mistral(api_key=self.mistral_api_key)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'parsed_job_format.json')

        with open(file_path, 'r') as file:
            self.parsed_job_dict_format = file.read()

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
            "metrics": {
                "inference_time_seconds": inference_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
        }
        return response
