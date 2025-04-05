from dotenv import load_dotenv
load_dotenv()

    
from services.db.mongo import MongoInstance
mongo_instance = MongoInstance()

from utilities.logging_utilities import LoggingUtilities
logging_utilities = LoggingUtilities()

from mistralai import Mistral
import os
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

from fastapi import FastAPI
app = FastAPI()

from routers import auth
from routers import candidate
from routers import recruiter

app.include_router(auth.router)
app.include_router(candidate.router)
app.include_router(recruiter.router)
