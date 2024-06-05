import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from setup import retry

@retry(max_retry_count=4, interval_sec=3)
def process_gmail_email(driver: webdriver.Chrome, email, log):
    log.info(f"Searching for {email} on gmail.")
    try:
        driver.get("https://accounts.google.com/signin/recovery/lookup")
        # time.sleep(1000)
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='email']")))
        email_input.clear()
        email_input.send_keys(email)
        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "next")))
        next_button.click()
        try:
            element = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Try using a different browser')]"))
            )

        except:
            pass
        page_source = driver.page_source
        visible_text = driver.find_element(By.TAG_NAME, 'body').text
        if "Try using a different browser" in page_source or \
                "Try using a different browser" in visible_text:
            return 'Correct'
        elif "To keep your Google Account secure, try signing in on a browser that has JavaScript turned on" in page_source or \
            "To keep your Google Account secure, try signing in on a browser that has JavaScript turned on"  in visible_text:
            raise Exception()
        return "Incorrect"

    except Exception as e:
        raise Exception()

