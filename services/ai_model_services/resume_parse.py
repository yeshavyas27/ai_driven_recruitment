from mistralai import Mistral
import time
from typing import Dict, Any
import os
import json

class ParseResume:
    def __init__(self):

        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.model = "mistral-small-latest"
        self.client = Mistral(api_key=self.mistral_api_key)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'parsed_resume_format.json')

        with open(file_path, 'r') as file:
            self.parsed_resume_dict_format = file.read()

    def parse_api_call(self, resume_data):
       

        # Start timer for inference time tracking
        start_time = time.time()
        
        # Prepare input message
        input_message = f"Extract structured information in the format given from the data. Format: {self.parsed_resume_dict_format} Data:{resume_data}"

        # Make API call
        chat_response = self.client.chat.complete(
            model=self.model,
            messages=[
                {
                    "role": "user", 
                    "content": input_message
                }
            ],
            response_format={
                "type": "json_object"
            }
        )

        # Calculate inference time
        inference_time = time.time() - start_time

        # Extract response content
        response_content = chat_response.choices[0].message.content
        # Get token counts
        input_tokens = chat_response.usage.prompt_tokens
        output_tokens = chat_response.usage.completion_tokens
        total_tokens = chat_response.usage.total_tokens
        parsed_resume = json.loads(response_content)
        response = {
            **parsed_resume,
            "metrics": {
                "inference_time_seconds": inference_time,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens
            }
        }
        return response
        

    def parse(self, resume_data):
        return self.parse_api_call(resume_data)

