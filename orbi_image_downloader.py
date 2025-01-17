from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import logging
import os
import requests
import time

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

def download_image(url, save_path):
    """
    Download an image from the given URL and save it to the specified path.
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            logging.info(f"Image downloaded: {save_path}")
        else:
            logging.error(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error downloading image: {e}")

def process_articles(driver, visited_urls, run_time):
    """
    Process articles with images, download them, and repeat until the specified runtime elapses.
    """
    base_url = "https://orbi.kr/list"
    image_download_dir = "downloaded_images"
    os.makedirs(image_download_dir, exist_ok=True)
    start_time = time.time()

    while time.time() - start_time < run_time:
        driver.get(base_url)

        # Wait for the post list to load
        if not wait_for_element(driver, By.CLASS_NAME, "post-list"):
            logging.info("No post list found. Exiting.")
            break

        try:
            # Refresh the list of articles (excluding notices)
            articles = driver.find_elements(By.CSS_SELECTOR, "ul.post-list > li:not(.notice)")
        except Exception as e:
            logging.error(f"Error locating articles: {e}")
            continue

        for article in articles:
            try:
                # Get the article link from <p class="title"> inside the <li>
                title_element = article.find_element(By.CSS_SELECTOR, "p.title a")
                link = title_element.get_attribute("href")

                # Skip already visited links
                if not link or link in visited_urls:
                    continue

                visited_urls.add(link)  # Mark link as visited

                # Visit the article
                driver.get(link)

                # Wait for the content-wrap element to load
                content_wrap = wait_for_element(driver, By.CLASS_NAME, "content-wrap")
                if not content_wrap:
                    logging.info(f"No 'content-wrap' found in article: {link}")
                    continue

                # Find all images in the content-wrap
                try:
                    images = content_wrap.find_elements(By.TAG_NAME, "img")
                    for idx, img in enumerate(images):
                        img_url = img.get_attribute("src")
                        if img_url:
                            save_path = os.path.join(image_download_dir, f"{link.split('/')[-1]}_img{idx}.jpg")
                            download_image(img_url, save_path)
                except Exception as e:
                    logging.error(f"Error finding or downloading images in article: {e}")
                    continue

                logging.info(f"Processed article: {link}")

            except StaleElementReferenceException:
                logging.warning("Stale element detected while processing articles. Reloading...")
                break
            except Exception as e:
                logging.error(f"Error processing article: {e}")
                continue

        logging.info("Reloading page and checking for new articles...")
        time.sleep(2)  # Short delay before reloading

    logging.info("Time elapsed. Stopping script.")

def main():
    # Configure Chrome WebDriver options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Get user-specified runtime in minutes
        try:
            run_time_minutes = int(input("Enter the runtime in minutes: "))
            if run_time_minutes <= 0:
                raise ValueError("Runtime must be greater than 0.")
        except ValueError as e:
            logging.error(f"Invalid input: {e}")
            return

        run_time_seconds = run_time_minutes * 60
        visited_urls = set()

        logging.info(f"Script will run for {run_time_minutes} minutes.")
        process_articles(driver, visited_urls, run_time_seconds)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()