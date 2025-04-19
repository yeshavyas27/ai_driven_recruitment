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
                self.logger.warning(f"Job data not found using agentql for url: {url}")
                # Fallback to scraping if agentql fails
                page_data = await ScrapeService().scrape(url)
                job_data = ParseJob().parse_job_data(page_data=page_data)

            return job_data


