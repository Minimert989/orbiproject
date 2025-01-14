from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
import logging
import getpass

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be located and return it.
    """
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    except TimeoutException:
        logging.error(f"Element with {by} = {value} not found within {timeout} seconds.")
        return None

def handle_alert(driver, timeout=5):
    """
    Handles an alert if it appears within the specified timeout period.
    """
    try:
        alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
        logging.info(f"Alert detected: {alert.text}")
        alert.accept()
        logging.info("Alert accepted.")
        return True
    except TimeoutException:
        logging.info("No alert appeared.")
        return False

def extract_posts(driver):
    """
    Extract all posts from the user's post list. Stops pagination if no valid posts are found.
    """
    posts = []
    page = 1

    while True:
        logging.info(f"Processing page {page}...")
        driver.get(f"https://orbi.kr/my/post?page={page}")

        try:
            if not wait_for_element(driver, By.CLASS_NAME, "post-list"):
                logging.error(f"Post list not found on page {page}.")
                break

            post_elements = driver.find_elements(By.CSS_SELECTOR, "ul.post-list > li")
            if not post_elements:
                logging.info("No more posts found. Ending pagination.")
                break

            valid_posts_found = False
            for post in post_elements:
                try:
                    title_element = post.find_element(By.CSS_SELECTOR, "p.title")
                    title = title_element.text.strip() if title_element.text.strip() else None
                    href = post.find_element(By.TAG_NAME, "a").get_attribute("href").split("/")[-1] \
                        if post.find_element(By.TAG_NAME, "a").get_attribute("href") else None

                    if title and href:
                        posts.append({"title": title, "href": href})
                        valid_posts_found = True
                except Exception as e:
                    logging.warning(f"Failed to extract post details: {e}")

            if not valid_posts_found:
                logging.info("No valid posts found on this page. Ending pagination.")
                break

            page += 1

        except UnexpectedAlertPresentException:
            alert = driver.switch_to.alert
            logging.warning(f"Unexpected alert dismissed: {alert.text}")
            alert.dismiss()
            break
        except Exception as e:
            logging.error(f"Error processing page {page}: {e}")
            break

    return posts

def delete_post(driver, post_number):
    """
    Navigate to a post's modify page and delete the post.
    Handle confirmation alerts if they appear.
    """
    try:
        logging.info(f"Attempting to delete post: {post_number}")
        driver.get(f"https://orbi.kr/modify/{post_number}")
        if not wait_for_element(driver, By.CLASS_NAME, "button.delete"):
            logging.error(f"Delete button not found for post {post_number}.")
            return

        delete_button = driver.find_element(By.CLASS_NAME, "button.delete")
        delete_button.click()

        if handle_alert(driver):
            logging.info(f"Post {post_number} deletion confirmed.")
        else:
            logging.warning("No confirmation alert appeared. Deletion may not have been confirmed.")

    except Exception as e:
        logging.error(f"Failed to delete post {post_number}: {e}")

def main():
    # Set Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    try:
        # Input credentials
        username = input("Enter your Orbi username/email: ")
        password = getpass.getpass("Enter your Orbi password: ")

        # Initialize WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://login.orbi.kr/login")

        # Log in to the site
        wait_for_element(driver, By.NAME, "username").send_keys(username)
        password_field = wait_for_element(driver, By.NAME, "password")
        password_field.send_keys(password)
        password_field.submit()

        if not wait_for_element(driver, By.CLASS_NAME, "post-list"):
            logging.error("Login failed or post list not found.")
            return

        logging.info("Login successful!")

        # Extract posts
        posts = extract_posts(driver)
        if not posts:
            logging.info("No posts found.")
            return

        logging.info("\nExtracted Posts:")
        for idx, post in enumerate(posts, start=1):
            logging.info(f"{idx}. Title: {post['title']}, HREF: {post['href']}")

        # Ask the user which posts to delete
        to_delete = input("Enter the numbers of the posts to delete (comma-separated): ")
        try:
            to_delete = [int(num.strip()) for num in to_delete.split(",") if num.strip().isdigit()]
        except ValueError:
            logging.error("Invalid input. Please enter numbers only.")
            return

        for num in sorted(to_delete):
            if 1 <= num <= len(posts):
                post = posts[num - 1]
                delete_post(driver, post["href"])
            else:
                logging.warning(f"Invalid post number: {num}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()