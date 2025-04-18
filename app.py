from dotenv import load_dotenv

load_dotenv()

    
from services.db.mongo import MongoInstance

mongo_instance = MongoInstance()

from utilities.logging_utilities import LoggingUtilities

logging_utilities = LoggingUtilities()

import os

from mistralai import Mistral

mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

from fastapi import FastAPI

app = FastAPI()

from routers import auth, candidate, recruiter

app.include_router(auth.router)
app.include_router(candidate.router)
app.include_router(recruiter.router)
