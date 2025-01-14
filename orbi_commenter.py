from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def login_to_orbi_and_comment(username, password, article_number, comment_word, num_comments):
    # Set up WebDriver
    login_url = "https://login.orbi.kr/login"
    base_url = "https://orbi.kr/"
    article_url = f"{base_url}{article_number}"  # Construct the article URL

    # Start WebDriver
    driver = webdriver.Chrome()  # Ensure you have the ChromeDriver installed and accessible
    driver.get(login_url)

    try:
        # Log in to Orbi
        time.sleep(3)  # Allow time for the page to load
        driver.find_element(By.NAME, "username").send_keys(username)  # Locate username field by "name"
        driver.find_element(By.NAME, "password").send_keys(password)  # Locate password field by "name"
        driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)  # Submit the login form
        time.sleep(3)  # Wait for login to complete

        # Navigate to the article
        driver.get(article_url)
        time.sleep(3)

        # Post comments
        for i in range(num_comments):
            # Locate the comment input field
            comment_area = driver.find_element(By.NAME, "content")  # Locate by "name"
            comment_area.click()  # Activate the comment input field
            time.sleep(1)  # Allow the input area to activate

            # Enter the comment text
            comment_area.send_keys(comment_word)

            # Locate and click the post button
            post_button = driver.find_element(By.CLASS_NAME, "send")  # Locate the post button by "class"
            post_button.click()

            print(f"Comment {i + 1} posted.")
            time.sleep(2)  # Add delay to mimic human behavior

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    username = input("Enter your Orbi username/email: ")
    password = input("Enter your password: ")
    article_number = input("Enter the article number (last digits of the URL): ")
    comment_word = input("Enter the word to comment: ")
    num_comments = int(input("Enter the number of comments to post: "))

    login_to_orbi_and_comment(username, password, article_number, comment_word, num_comments)