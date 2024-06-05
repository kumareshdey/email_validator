import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from setup import retry

@retry(max_retry_count=4, interval_sec=3)
def process_outlook_email(driver: webdriver.Chrome, email, log):
    log.info(f"Searching for {email} on outlook")
    try:
        driver.get("https://account.live.com/ResetPassword.aspx")
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "iSigninName"))
        )
        email_input.clear()
        email_input.send_keys(email)
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "resetPwdHipAction"))
        )
        next_button.click()
        try:
            error_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "iSigninNameError"))
            )
            return "Incorrect"
        except:
            try:
                verified = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "iSelectProofTitle"))
                )
            except:
                try:
                    verified = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "iVerifyIdentityTitle"))
                    )
                except:
                    verified = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.ID, "recoveryPlusTitle"))
                    )
            
            return 'Correct'

    except Exception as e:
        raise Exception()