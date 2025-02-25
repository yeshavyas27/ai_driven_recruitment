import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.shell import inspect_response

from scrapy.utils.project import get_project_settings
import js2xml
import lxml.etree
from parsel import Selector
class NaukriSpider(scrapy.Spider):
    name = "naukri"

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        
        # Additional settings to make the crawler more browser-like
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        },
        
        # Add a download delay to seem more human-like
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        
        # Respect robots.txt by default
        'ROBOTSTXT_OBEY': True,
    }

    def __init__(self, **kwargs):
        super(NaukriSpider, self).__init__(**kwargs)
        skills_designations_companies = kwargs["skills_designations_companies"]
        location = kwargs["location"]
        experience = kwargs["experience"]
        page = skills_designations_companies.replace(" ", "-").replace(",", "-") + "-jobs"

        key_skills_designations_companies = skills_designations_companies.replace(" ", "%20").replace(",", "%2C")
        self.start_urls = [f"https://www.naukri.com/{page}?k={key_skills_designations_companies}"]
        if location:
            self.start_urls[0] += "-in-" + location.split()[0]
            key_location = location.replace(" ", "%20").replace(",", "%2C")
            self.start_urls[0] += f"&l={key_location}"
        if experience:
            self.start_urls[0] += f"&experience={experience}"
        if location or experience:
            self.start_urls[0] += f"&nignbevent_src=jobsearchDeskGNB"
        print(self.start_urls)
        
    def parse(self, response):
        print(response.text)
        javascript = response.css("script::text").get()
        xml = lxml.etree.tostring(js2xml.parse(javascript), encoding="unicode")
        selector = Selector(text=xml)
        selector.css('var[name="data"]').get()
        # inspect_response(response, self)
        # for job in response.css("div.styles_jlc__main__VdwtF").get():
        #     print(job)
        #     print("------------------------------------------------")
        #     # grab srp-jobtuple-wrapper class which contains for each job
        #     # in that pick class row1 -> h2 -> a tag title is job name and href link for the jon
        #     # .attrib["src"] - to catch title and href 
        #     # go to the href link -> grab the job description data
        #     # loop for all

        



def spider_naukri(
        skills_designations_companies: str ="software dev", 
        experience: int = None,
        location: str = None
    ):


    process = CrawlerProcess(get_project_settings())

    # 'followall' is the name of one of the spiders of the project.
    process.crawl(NaukriSpider, skills_designations_companies=skills_designations_companies, experience=experience, location=location)
    process.start()  # the script will block here until the crawling is finished

spider_naukri()