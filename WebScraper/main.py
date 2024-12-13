from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests
import re
from bs4 import BeautifulSoup
from time import sleep


def login_to_linkedin(driver, username, password):

    print("Logging in LinkedIn...")
    driver.get('https://www.linkedin.com/login')

    username_field = driver.find_element(By.ID, 'username')
    password_field = driver.find_element(By.ID, 'password')

    username_field.send_keys(username)
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

    sleep(5)
    return driver


def scrape_job_data(driver):

    driver.get('https://www.linkedin.com/jobs/search/')
    sleep(5)

    jobs = []
    current_page = 1

    while True:
        print(f"Scraping Page {current_page}...")

        try:
            job_cards = driver.find_elements(By.XPATH, '//div[@data-job-id]')

            if not job_cards:
                print("No job cards found on this page.")
                break

            for card in job_cards:
                try:

                    title_element = card.find_element(By.XPATH, './/a[contains(@class, "job-card-container__link")]')
                    title = title_element.text.strip() if title_element else 'N/A'

                    subtitle_element = card.find_element(By.XPATH,
                                                         './/div[contains(@class, "artdeco-entity-lockup__subtitle")]')
                    if subtitle_element:
                        subtitle_text = subtitle_element.text.strip()
                        parts = subtitle_text.split('·')
                        company = parts[0].strip() if len(parts) > 0 else 'N/A'
                        location = parts[1].strip() if len(parts) > 1 else 'N/A'
                    else:
                        company, location = 'N/A', 'N/A'

                except Exception as e:
                    # Log the error and proceed with defaults
                    print(f"Error extracting job card: {e}")
                    title, company, location = 'N/A', 'N/A', 'N/A'

                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location
                })
        except Exception as e:
            print(f"Error extracting job cards: {e}")
            break

        try:
            pagination = driver.find_element(By.CLASS_NAME, "artdeco-pagination__pages")

            page_buttons = pagination.find_elements(By.TAG_NAME, "button")

            if current_page < len(page_buttons):
                next_page_button = page_buttons[current_page]
                driver.execute_script("arguments[0].scrollIntoView();", next_page_button)

                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(next_page_button)
                )

                next_page_button.click()
                sleep(5)
                current_page += 1

            else:
                print("No more pages available.")
                break

        except Exception as e:
            print(f"Error navigating pages: {e}")
            break

    return jobs

if __name__ == '__main__':

    chrome_driver_path = r'D:\chromedriver-win64\chromedriver-win64\chromedriver.exe'
    service = Service(chrome_driver_path)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:

        username = "m.yaneva002@gmail.com"
        password = "v06480675"
        driver = login_to_linkedin(driver, username, password)

        jobs = scrape_job_data(driver)
        job_index = 1
        for job in jobs:
            print(f"Job {job_index}:")
            print(f"Title: {job['title']},\n Company: {job['company']},\n Location: {job['location']}")
            job_index += 1

    finally:
        driver.quit()


