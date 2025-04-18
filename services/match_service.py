from abstractions.base_service import BaseService


class MacthService(BaseService):
    def __init__(self):
        super().__init__()

    def do(self, resume_data, match_data):
        # call ai model service to get match score between resume and job data
        # return the match score

        pass