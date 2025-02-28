from playwright.async_api import async_playwright

class ScrapeNaukriService():
    def __init__(self, **kwargs):
        self.start_url = self.__generate_url(kwargs)
        print(self.start_url)
        
    def __generate_url(self, kwargs):
        skills_designations_companies = kwargs["skills_designations_companies"]
        location = kwargs["location"]
        experience = kwargs["experience"]
        page = skills_designations_companies.replace(" ", "-").replace(",", "-") + "-jobs"
        if kwargs["page_number"] > 1:
            page += f"-{kwargs["page_number"]}"

        key_skills_designations_companies = skills_designations_companies.replace(" ", "%20").replace(",", "%2C")
        start_url = f"https://www.naukri.com/{page}?k={key_skills_designations_companies}"
        if location:
            start_url += "-in-" + location.split()[0]
            key_location = location.replace(" ", "%20").replace(",", "%2C")
            start_url += f"&l={key_location}"
        if experience:
            start_url += f"&experience={experience}"
        if location or experience:
            start_url += f"&nignbevent_src=jobsearchDeskGNB"
        
        return start_url

    async def scrape(self):
        async with async_playwright() as p:
            chrome_device = p.devices['Desktop Chrome']
            browser = await p.webkit.launch(headless=True)  # Launch in headless mode
            context = await browser.new_context(**chrome_device)
            page = await context.new_page()
            await page.goto(self.start_url)  
            TIMEOUT = 6000
            await page.wait_for_load_state("networkidle", timeout=TIMEOUT)
            jobs = []
            for job in await page.locator("css=div.styles_jlc__main__VdwtF > div.srp-jobtuple-wrapper").all():
                job_link = await job.locator("css=a.title").get_attribute("href")
                job_page = await context.new_page()
                await job_page.goto(job_link)
                await job_page.wait_for_load_state("networkidle", timeout=TIMEOUT)
                job_title = await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[1]/header/h1").get_attribute("title")
                company_name = await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[1]/div/a").text_content()
                years_of_experience = await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[1]/div[1]/span").text_content()
                salary = await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[1]/div[2]/span").text_content()
                location = await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[2]/div[2]/span").text_content()
                
                job_description = await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[2]").text_content()
                education = await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[2]/div[2]/div[3]/div[2]").text_content()

                skills_container =  job_page.locator("css=div.styles_key-skill__GIPn_")
                all_skills = await skills_container.locator("a").all_text_contents()
                skill_elements = await skills_container.locator("a").all()

                key_skills = []
                for skill in skill_elements:
                    if await skill.locator("i.ni-icon-jd-save").count() > 0:
                        key_skills.append(await skill.locator("span").text_content())

                if not key_skills:
                    key_skills = all_skills

                jobs.append({
                    "job_link": job_link,
                    "company_name": company_name,
                    "job_title": job_title,
                    "years_of_experience": years_of_experience,
                    "salary": salary,
                    "location": location,
                    "job_description": job_description,
                    "education": education,
                    "all_skills": all_skills,
                    "key_skills": key_skills
                })
                

            await browser.close()
            return jobs

            

import asyncio

jobs = asyncio.run(ScrapeNaukriService(
    skills_designations_companies="software dev", 
    experience=1,
    location=None,
    page_number=1
).scrape())

print(jobs)
'''
job_title
years of experience
comapnay name
job link
location
salary
job description
key skills
education
'''