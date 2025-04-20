from fastapi import HTTPException, status

from abstractions.base_service import BaseService
from services.ai_model_services.job_parse import ParseJob
from services.scrape_service import ScrapeService


class JobService(BaseService):
    def __init__(self):
        super().__init__()

    async def parse_job(self, url, approach="agentql"):
        if approach == "agentql":
            job_data = ParseJob().parse_job_data_agentql(job_link=url)
            self.logger.info(f"The job data is {job_data}")

            if not job_data["company_name"]:
                self.logger.error(f"Job data not found using scraping for url: {url}")
                raise HTTPException(detail="Unable to parse job data." ,status_code=status.HTTP_406_NOT_ACCEPTABLE)


            return job_data


