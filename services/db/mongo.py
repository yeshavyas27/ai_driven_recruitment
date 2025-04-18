import os

from pymongo import MongoClient

from constants.database import MongoDatabases


class MongoInstance:
    def __init__(self):

        hostname = os.getenv("MONGO_HOST")
        if not hostname:
            raise RuntimeError("Mongo host is not set.")

        user =  os.getenv("MONGO_USER")
        if not user:
            raise RuntimeError("Mongo user is not set.")
        

        password =  os.getenv("MONGO_PASSWORD")
        if not password:
            raise RuntimeError("Mongo password is not set.")
        self.cluster = MongoClient(hostname.format(user=user, password=password))
        
        self.cluster_db = self.cluster[MongoDatabases.AI_Driven_Recruitment_DB]