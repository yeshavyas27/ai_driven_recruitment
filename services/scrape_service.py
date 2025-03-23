from abstractions.base_service import BaseService

import asyncio
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright
import random




class ScrapeService(BaseService):
    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor()
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"]

    async def scrape(self, url):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._scrape_sync, url)
    
    def _scrape_sync(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, 
                                        args=[
                                            '--disable-blink-features=AutomationControlled',
                                            '--disable-features=IsolateOrigins,site-per-process',
                                            '--disable-site-isolation-trials',
                                        ])
            user_agent = random.choice(self.user_agent_list)
            context = browser.new_context(  user_agent=user_agent, 
                                            viewport={'width': 1920, 'height': 1080},
                                            device_scale_factor=1,
                                            is_mobile=False,
                                            has_touch=False,
                                            locale="en-US",
                                            timezone_id="IST",)
            page = context.new_page()
            page.goto(url)
            content = page.locator("body").text_content()
            browser.close()
            return content