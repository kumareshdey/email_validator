from logging import config
from selenium import webdriver
from contextlib import contextmanager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


@contextmanager
def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (useful for headless mode)
    # chrome_options.add_argument("--no-sandbox")  # Bypass OS security model (useful for Docker)
    # chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    driver = webdriver.Chrome(options=chrome_options)
    try:
        yield driver
    finally:
        driver.quit()


def retry(max_retry_count, interval_sec):
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = kwargs.get('log')
            retry_count = 0
            while retry_count < max_retry_count:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retry_count += 1
                    log.error(f'{func.__name__} failed on attempt {retry_count}: {str(e)}')
                    if retry_count < max_retry_count:
                        log.info(f'Retrying {func.__name__} in {interval_sec} seconds...')
                        time.sleep(interval_sec)
            log.warning(f'{func.__name__} reached maximum retry count of {max_retry_count}.')
            return None
        return wrapper
    return decorator