from dotenv import load_dotenv
load_dotenv()

    
from services.db.mongo import MongoInstance
mongo_instance = MongoInstance()

from utilities.logging_utilities import LoggingUtilities
logging_utilities = LoggingUtilities()

import asyncio
import platform

# At the start of your main.py or app.py file:
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI

    
from routers import auth
from routers import candidate

app = FastAPI()
app.include_router(auth.router)
app.include_router(candidate.router)
