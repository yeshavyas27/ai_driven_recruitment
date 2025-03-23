from playwright.async_api import async_playwright

from abstractions.base_service import BaseService
from services.ai_model_services.job_parse import ParseJob
from services.scrape_service import ScrapeService


class JobService(BaseService):
    def __init__(self):
        super().__init__()

    async def parse_job(self, url):
        page_data = await ScrapeService().scrape(url)
        self.logger.debug(f"The page data scraped is {page_data}")
        # TODO: extract sensible text from the extracted text and pass that to the model
        job_data = ParseJob().parse_job_data(page_data=page_data)
        return job_data


