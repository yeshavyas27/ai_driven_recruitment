from playwright.async_api import async_playwright

class ScrapeNaukriService():
    def __init__(self, **kwargs):
        skills_designations_companies = kwargs["skills_designations_companies"]
        location = kwargs["location"]
        experience = kwargs["experience"]
        page = skills_designations_companies.replace(" ", "-").replace(",", "-") + "-jobs"

        key_skills_designations_companies = skills_designations_companies.replace(" ", "%20").replace(",", "%2C")
        self.start_url = f"https://www.naukri.com/{page}?k={key_skills_designations_companies}"
        if location:
            self.start_url += "-in-" + location.split()[0]
            key_location = location.replace(" ", "%20").replace(",", "%2C")
            self.start_url += f"&l={key_location}"
        if experience:
            self.start_url += f"&experience={experience}"
        if location or experience:
            self.start_url += f"&nignbevent_src=jobsearchDeskGNB"
        # TODO: add page query to url as well
        print(self.start_url)

    async def scrape(self):
        async with async_playwright() as p:
            chrome_device = p.devices['Desktop Chrome']
            browser = await p.webkit.launch(headless=True)  # Launch in headless mode
            context = await browser.new_context(**chrome_device)
            page = await context.new_page()
            await page.goto(self.start_url)  
            TIMEOUT = 5000
            await page.wait_for_load_state("networkidle", timeout=TIMEOUT)
            
            for job in await page.locator("css=div.styles_jlc__main__VdwtF > div.srp-jobtuple-wrapper").all():
                job_link = await job.locator("css=a.title").get_attribute("href")
                print(job_link)
                job_page = await context.new_page()
                await job_page.goto(job_link)
                await job_page.wait_for_load_state("networkidle", timeout=TIMEOUT)
                # get job title, company, location - section.styles_job-header-container___0wLZ
                print("Job header:")
                print(await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[1]/div[1]/div[1]/header/h1").text_content())
                # job description,skills, education - section.styles_job-desc-container__txpYf
                print("Job description:")
                print(await job_page.locator("xpath=/html/body/div/div/main/div[1]/div[1]/section[2]").text_content())
                

                # returns job link, company name, job description, job name, key skills, education required, number of years of experience required
                # just print single job description and stop for experiment purpose
                
                break
                print("------------------------------------------------------")

            await browser.close()

import asyncio

asyncio.run(ScrapeNaukriService(
    skills_designations_companies="software dev", 
    experience=None,
    location=None,
    page=None
).scrape())
