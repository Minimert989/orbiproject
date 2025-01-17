import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, UnexpectedAlertPresentException, WebDriverException

LOG_FILE = "orbi_lottery_log.txt"

def log_result(message):
    """Writes logs to a file with a timestamp."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        f.write(timestamp + message + "\n")

def login_to_orbi(username, password):
    """Logs in to Orbi and returns the WebDriver instance."""
    login_url = "https://login.orbi.kr/login"
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.popups": 2,  # Block pop-ups
        "profile.default_content_setting_values.notifications": 2  # Block notifications
    })
    options.add_argument("--disable-popup-blocking")  # Ensures pop-ups don’t interfere
    driver = webdriver.Chrome(options=options)
    driver.get(login_url)
    
    try:
        time.sleep(3)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(3)
        log_result("Login successful.")
        return driver
    except NoSuchElementException:
        log_result("Login failed: Elements not found.")
        driver.quit()
        return None

def handle_alert(driver):
    """Closes JavaScript alerts by clicking '확인' (OK) automatically."""
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text  # Get alert text before closing
        alert.accept()  # Clicks "확인" button
        log_result(f"Alert appeared and was closed: {alert_text}")
        return True
    except WebDriverException:
        return False  # No alert present

def click_lottery_balloon(driver, num_clicks):
    """Navigates to the lottery page and clicks the balloon image."""
    lottery_url = "https://orbi.kr/amusement/lottery"
    driver.get(lottery_url)
    
    time.sleep(3)

    for i in range(num_clicks):
        try:
            balloon = driver.find_element(By.CLASS_NAME, "balloon")
            balloon.click()
            time.sleep(1)

            # Automatically handle alert and click "확인"
            while handle_alert(driver):  # Keep closing alerts if multiple appear
                time.sleep(1)

            log_result(f"Click {i+1}/{num_clicks} successful.")
            print(f"Clicked {i+1}/{num_clicks} times.")
        except NoSuchElementException:
            log_result(f"Click {i+1}/{num_clicks}: Balloon not found. Retrying...")
            time.sleep(2)
            continue
        except ElementClickInterceptedException:
            log_result(f"Click {i+1}/{num_clicks}: Click was blocked. Retrying...")
            time.sleep(2)
            continue
        except UnexpectedAlertPresentException:
            log_result(f"Click {i+1}/{num_clicks}: Unexpected alert appeared, handling now...")
            handle_alert(driver)  # Ensure any unexpected alerts are closed
            continue

    print("Clicking process completed.")
    log_result("Clicking process completed.")

if __name__ == "__main__":
    username = input("Enter your Orbi username: ")
    password = input("Enter your Orbi password: ")
    num_clicks = int(input("How many times do you want to click the balloon? "))

    driver = login_to_orbi(username, password)
    if driver:
        click_lottery_balloon(driver, num_clicks)
        input("Press Enter to close the browser...")  # Keeps browser open
        driver.quit()