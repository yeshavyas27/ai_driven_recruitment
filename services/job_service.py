from playwright.async_api import async_playwright

from abstractions.base_service import BaseService
from services.ai_model_services.job_parse import ParseJob
from services.scrape_service import ScrapeService


class JobService(BaseService):
    def __init__(self):
        super().__init__()

    async def parse_job(self, url, approach="agentql"):
        if approach == "agentql":
            job_data = ParseJob().parse_job_data_agentql(job_link=url)
        
        else:
            page_data = await ScrapeService().scrape(url)
            # TODO: extract only sensible text from the extracted text and pass that to the model
            job_data = ParseJob().parse_job_data(page_data=page_data)

        return job_data


