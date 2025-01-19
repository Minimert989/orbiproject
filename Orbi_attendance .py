from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def wait_until_midnight():
    """
    Calculate the time difference to midnight and wait accordingly.
    """
    now = datetime.now()
    midnight = datetime.combine(now + timedelta(days=1), datetime.min.time())  # Set to next day's 12:00 AM
    time_to_midnight = (midnight - now).total_seconds()
    logging.info(f"Waiting {time_to_midnight:.2f} seconds until midnight...")
    time.sleep(time_to_midnight)

def main():
    # Configure Chrome WebDriver options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run browser in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    try:
        # Prompt for login credentials
        username = input("Enter your Orbi username/email: ")
        password = input("Enter your Orbi password: ")

        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://login.orbi.kr/login")

        # Log in
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for login to complete

        logging.info("Login successful!")

        # Navigate to attendance page
        driver.get("https://orbi.kr/amusement/attendance")

        # Input "q" into the attendance form
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "greets-wrap")))
        input_box = driver.find_element(By.CSS_SELECTOR, ".greets-wrap .input-wrap")
        input_box.send_keys("q")
        logging.info('Typed "q" into the input box.')

        # Wait until midnight
        wait_until_midnight()

        # Click the submit button at exactly midnight
        submit_button = driver.find_element(By.CSS_SELECTOR, ".greets-wrap button.submit")
        submit_button.click()
        logging.info("Attendance submitted successfully at exactly 12:00 AM!")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()