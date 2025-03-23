from mistralai import Mistral
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv
import os


# using playwright
async def scrape(url):
    async with async_playwright() as p:
        chrome_device = p.devices['Desktop Chrome']
        browser = await p.webkit.launch(headless=True)  # Launch in headless mode
        context = await browser.new_context(**chrome_device)
        page = await context.new_page()
        await page.goto(url)  
        await page.wait_for_load_state("networkidle")
        page_data = await page.locator("body").text_content()
        return page_data





url = ["https://www.naukri.com/job-listings-software-dev-engineer-ii-amazon-india-software-dev-centre-pvt-ltd-bengaluru-0-to-7-years-130325502075?src=directSearch&sid=17419443863402700&xp=1&px=1",
       "https://boards.greenhouse.io/embed/job_app?token=6114125",
       "https://internshala.com/internship/detail/work-from-home-part-time-data-science-internship-at-emoolar-technology-private-limited1741951418"
]
page_data = asyncio.run(
    scrape(url[2])
)
# print(page_data)


load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model = model,
    messages = [
        {
            "role": "user",
            "content": f'''
                    Parse the scraped data of a job listing from a website into the follwing format:
                    "company_name": "",
                    "job_title": "",
                    "years_of_experience": "",
                    "salary": "",
                    "location": "",
                    "job_description": "",
                    "education": "",
                    "all_skills": "",
                    "key_skills": ""
                    Data/ job listing: {page_data}
            
            
            '''
        },],
        response_format = {
          "type": "json_object", }

)

print(chat_response.choices[0].message.content)
# add the job link to the json