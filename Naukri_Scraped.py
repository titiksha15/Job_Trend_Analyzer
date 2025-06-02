from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
import os
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to ChromeDriver
CHROMEDRIVER_PATH = "C:/Chromedriver/chromedriver-win64/chromedriver-win64/chromedriver.exe"

# Expanded list of job roles and locations
roles = [
    "data-analyst", "data-scientist", "machine-learning-engineer",
    "web-developer", "mobile-app-developer",
    "software-engineer", "devops-engineer", 
    "full-stack-developer", "cloud-engineer", 
    
]
locations = [
    "delhi", "bangalore", "mumbai", 
    "hyderabad", "pune", "chennai", 
    "kolkata", "gurgaon", "noida", 
    "ahmedabad"
]

# Create directory for saving data and screenshots
os.makedirs("Data/clean", exist_ok=True)
os.makedirs("Data/screenshots", exist_ok=True)

# Set up Chrome options to mimic a real browser
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--enable-unsafe-swiftshader")
# options.add_argument("--headless")  # Uncomment after testing
# proxy = "http://your-proxy:port"  # Uncomment and set for proxy support
# options.add_argument(f"--proxy-server={proxy}")

# Initialize the WebDriver
service = Service(CHROMEDRIVER_PATH)
try:
    driver = webdriver.Chrome(service=service, options=options)
    logging.info("WebDriver initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize WebDriver: {e}")
    raise

# Remove navigator.webdriver flag
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

all_jobs = []
max_jobs = 30000  # Target up to 30,000 jobs total
max_pages_per_role_location = 10  # Limit pages per role/location
jobs_per_page = 20  # Approximate jobs per page on Naukri
retries = 3
output_file = "Data/clean/naukri_selenium_fixed.csv"

# Function to save jobs incrementally
def save_jobs(jobs, filename, append=True):
    try:
        df = pd.DataFrame(jobs)
        mode = 'a' if append and os.path.exists(filename) else 'w'
        df.to_csv(filename, index=False, mode=mode, header=not append or mode == 'w')
        logging.info(f"Saved {len(jobs)} jobs to {filename} (append={append})")
    except Exception as e:
        logging.error(f"Error saving jobs to CSV: {e}")

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
            
            # Construct URL
            url = f"https://www.naukri.com/{role}-jobs-in-{location}?k={role}&l={location}"
            if page > 1:
                url += f"&start={(page - 1) * jobs_per_page}"
            
            for attempt in range(retries):
                try:
                    logging.info(f"Page {page} (Attempt {attempt + 1}): {url}")
                    driver.get(url)
                    time.sleep(random.uniform(3, 7))  # Increased delay for large scale

                    # Check for CAPTCHA
                    captcha = driver.find_elements(By.CLASS_NAME, "g-recaptcha")
                    if captcha:
                        logging.error(f"CAPTCHA detected on page {page} for {role} in {location}")
                        driver.save_screenshot(f"Data/screenshots/captcha_{role}_{location}_page_{page}_attempt_{attempt + 1}.png")
                        break

                    # Scroll to ensure dynamic content loads
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(random.uniform(1, 3))

                    # Wait for job cards
                    WebDriverWait(driver, 22).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
                    )

                    # Find job cards
                    job_cards = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")
                    if not job_cards:
                        logging.warning(f"No job cards found on page {page}")
                        driver.save_screenshot(f"Data/screenshots/no_cards_{role}_{location}_page_{page}_attempt_{attempt + 1}.png")
                        break

                    logging.info(f"Found {len(job_cards)} job cards on page {page}")
                    for job in job_cards:
                        try:
                            title = job.find_element(By.CLASS_NAME, "title").text.strip() if job.find_elements(By.CLASS_NAME, "title") else "N/A"
                            company = job.find_element(By.CLASS_NAME, "comp-name").text.strip() if job.find_elements(By.CLASS_NAME, "comp-name") else "N/A"
                            location_text = job.find_element(By.CLASS_NAME, "locWdth").text.strip() if job.find_elements(By.CLASS_NAME, "locWdth") else "N/A"
                            salary = job.find_element(By.CLASS_NAME, "sal").text.strip() if job.find_elements(By.CLASS_NAME, "sal") else "Not Disclosed"
                            skills = [skill.text.strip() for skill in job.find_elements(By.CLASS_NAME, "skill")] if job.find_elements(By.CLASS_NAME, "skill") else []
                            
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
                            
                            if len(all_jobs) >= max_jobs:
                                logging.info(f"Reached global job limit of {max_jobs}")
                                break
                        
                        except Exception as e:
                            logging.warning(f"Error parsing job card: {e}")
                            continue
                    
                    break  # Success, move to next page
                
                except TimeoutException:
                    logging.warning(f"Timeout on page {page}, attempt {attempt + 1}")
                    driver.save_screenshot(f"Data/screenshots/timeout_{role}_{location}_page_{page}_attempt_{attempt + 1}.png")
                    if attempt < retries - 1:
                        time.sleep(random.uniform(5, 10))
                        continue
                    else:
                        logging.error(f"Failed to load page {page} after {retries} attempts")
                        break
                except WebDriverException as e:
                    logging.error(f"WebDriver error on page {page}: {e}")
                    if attempt < retries - 1:
                        time.sleep(random.uniform(5, 10))
                        continue
                    else:
                        break
            
            if len(all_jobs) >= max_jobs:
                break

        # Save jobs incrementally after each location
        if all_jobs:
            save_jobs(all_jobs, output_file, append=True)
            all_jobs = []  # Clear memory

    if len(all_jobs) >= max_jobs:
        break

# Close the browser
driver.quit()

# Final save (if any jobs remain)
if all_jobs:
    save_jobs(all_jobs, output_file, append=True)

print("✅ Done.")
print(f"Scraped {len(all_jobs)} jobs (total saved to {output_file}).")