import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
import time
import random
import os
import json

# Setup logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize driver with stealth capabilities
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")  # Uncomment after testing

try:
    driver = uc.Chrome(options=options)
    logging.info("WebDriver initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize WebDriver: {e}")
    raise

# Remove navigator.webdriver flag
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Job roles and locations
roles = [
    "data-analyst", "data-scientist", "machine-learning-engineer",
    "web-developer", "mobile-app-developer",
    "software-engineer", "devops-engineer",
    "full-stack-developer", "cloud-engineer"
]
locations = [
    "Gurgaon", "Bangalore", "Mumbai",
    "Hyderabad", "Pune", "Chennai",
    "Kolkata", "Noida", "Ahmedabad"
]

# Setup
os.makedirs("Data/screenshots", exist_ok=True)
os.makedirs("Data/clean", exist_ok=True)
all_jobs = []
max_jobs = 30000
max_pages_per_role_location = 7  # Set to 7 for testing
retries = 3
output_file = "Data/clean/indeed_selenium_fixed.json"

# Function to save jobs
def save_jobs(jobs, file_path, append=True):
    try:
        mode = 'a' if append and os.path.exists(file_path) else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            for job in jobs:
                f.write(json.dumps(job, ensure_ascii=False) + '\n')
        logging.info(f"Saved {len(jobs)} jobs to {file_path} (append={append})")
    except Exception as e:
        logging.error(f"Error saving jobs to JSON: {e}")

# Main scraping logic
for role in roles:
    logging.info(f"Starting scraping for role: {role}")
    for location in locations:
        if len(all_jobs) >= max_jobs:
            logging.info(f"Reached global job limit of {max_jobs}")
            break

        logging.info(f"Scraping {role} in {location}")
        for page in range(1, max_pages_per_role_location + 1):
            if len(all_jobs) >= max_jobs:
                break

            # Try both in.indeed.com and www.indeed.com
            urls = [
                f"https://in.indeed.com/jobs?q={role.replace('-', '+')}&l={location.replace(' ', '+')}&start={(page - 1) * 10}",
                f"https://www.indeed.com/jobs?q={role.replace('-', '+')}&l={location.replace(' ', '+')}&start={(page - 1) * 10}"
            ]

            for url_idx, search_url in enumerate(urls):
                job_cards = []  # Initialize job_cards to avoid NameError
                for attempt in range(retries):
                    try:
                        logging.info(f"Page {page} (Attempt {attempt + 1}, URL {url_idx + 1}): {search_url}")
                        driver.get(search_url)
                        time.sleep(random.uniform(5, 8))

                        # Log page title and URL for debugging
                        logging.info(f"Page title: {driver.title}")
                        logging.info(f"Current URL: {driver.current_url}")

                        # Save page source for debugging
                        source_file = f"Data/screenshots/page_source_{role}_{location}_page_{page}_attempt_{attempt + 1}.html"
                        with open(source_file, "w", encoding="utf-8") as f:
                            f.write(driver.page_source)
                        logging.info(f"Saved page source to {source_file}")

                        # Check for CAPTCHA or robot check
                        if "robot" in driver.current_url or "captcha" in driver.page_source.lower():
                            logging.error(f"Blocked by CAPTCHA or robot-check on page {page} for {role} in {location}")
                            driver.save_screenshot(f"Data/screenshots/block_{role}_{location}_page_{page}_attempt_{attempt + 1}.png")
                            break

                        # Scroll multiple times to load dynamic content
                        for _ in range(3):
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(random.uniform(1, 3))

                        # Wait for job cards
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.job_seen_beacon"))
                        )

                        job_cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
                        logging.info(f"Found {len(job_cards)} job cards on page {page}")

                        if not job_cards:
                            logging.warning(f"No job cards found on page {page}")
                            driver.save_screenshot(f"Data/screenshots/no_cards_{role}_{location}_page_{page}_attempt_{attempt + 1}.png")
                            if url_idx == len(urls) - 1:  # Last URL tried
                                break
                            continue

                        for job in job_cards:
                            try:
                                title = job.find_element(By.CSS_SELECTOR, "h2.jobTitle a span").text.strip() if job.find_elements(By.CSS_SELECTOR, "h2.jobTitle a span") else "N/A"
                                company = job.find_element(By.CSS_SELECTOR, "span[data-testid='company-name']").text.strip() if job.find_elements(By.CSS_SELECTOR, "span[data-testid='company-name']") else "N/A"
                                location_text = job.find_element(By.CSS_SELECTOR, "div[data-testid='text-location']").text.strip() if job.find_elements(By.CSS_SELECTOR, "div[data-testid='text-location']") else "N/A"
                                salary = job.find_element(By.CSS_SELECTOR, "div[data-testid='attribute_snippet_testid']").text.strip() if job.find_elements(By.CSS_SELECTOR, "div[data-testid='attribute_snippet_testid']") else "Not Disclosed"
                                skills = [skill.text.strip() for skill in job.find_elements(By.CSS_SELECTOR, "div.jobsearch-Skills-container")] if job.find_elements(By.CSS_SELECTOR, "div.jobsearch-Skills-container") else []

                                job_data = {
                                    "Role": role,
                                    "Location": location,
                                    "Title": title,
                                    "Company": company,
                                    "Location_Detail": location_text,
                                    "Salary": salary,
                                    "Skills": skills
                                }
                                all_jobs.append(job_data)
                                logging.info(f"Scraped job: {title} at {company}")

                                if len(all_jobs) >= max_jobs:
                                    logging.info(f"Reached max job limit of {max_jobs}")
                                    break

                            except Exception as e:
                                logging.warning(f"Error parsing job card: {e}")
                                continue

                        break  # Break retry loop on success

                    except TimeoutException:
                        logging.warning(f"Timeout on page {page}, attempt {attempt + 1}")
                        driver.save_screenshot(f"Data/screenshots/timeout_{role}_{location}_page_{page}_attempt_{attempt + 1}.png")
                        if attempt < retries - 1:
                            time.sleep(random.uniform(5, 10))
                            continue
                        break
                    except WebDriverException as e:
                        logging.error(f"WebDriver error on page {page}: {e}")
                        if attempt < retries - 1:
                            time.sleep(random.uniform(5, 10))
                            continue
                        break

                if len(all_jobs) >= max_jobs or len(job_cards) > 0:
                    break  # Move to next page if jobs were found or max limit reached

            if len(all_jobs) >= max_jobs:
                break

        # Save jobs incrementally after each location
        if all_jobs:
            save_jobs(all_jobs, output_file, append=True)
            all_jobs = []

    if len(all_jobs) >= max_jobs:
        break

# Close browser safely
try:
    driver.quit()
    logging.info("Browser closed successfully")
except Exception as e:
    logging.error(f"Error closing browser: {e}")
finally:
    driver = None  # Ensure driver is cleared

# Final save
if all_jobs:
    save_jobs(all_jobs, output_file, append=True)
    print(f"✅ Done. Scraped and saved {len(all_jobs)} jobs to {output_file}.")
else:
    print("⚠️ No jobs scraped. Check scraper.log and screenshots for details.")