# File: imin_scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_imin_titles(imin_number):
    base_url = "https://orbi.kr/search"
    page = 1
    titles = []

    while True:
        # Construct URL with query parameters
        params = {
            "type": "imin",
            "q": imin_number,
            "page": page  # Add the page parameter for pagination
        }
        print(f"Fetching page {page} for {imin_number}...")

        # Make a GET request to the page
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}. HTTP Status Code: {response.status_code}")
            break

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the 'post-list' class container
        post_list = soup.find("ul", class_="post-list")
        if not post_list:
            print("No more 'post-list' found. Stopping.")
            break

        # Find all list items in the post list
        list_items = post_list.find_all("li")

        # Skip the first three list items with the 'notice' class
        valid_posts = [
            li for li in list_items
            if "notice" not in li.get("class", [])  # Exclude 'notice' class
        ][3:]  # Skip the first three valid posts

        # Extract titles from the <p> tags with class "title"
        page_titles = [
            post.find("p", class_="title").text.strip()
            for post in valid_posts
            if post.find("p", class_="title")  # Ensure <p class="title"> exists
        ]

        # Stop if no valid titles are found
        if not page_titles:
            print("No titles found on this page. Stopping.")
            break

        # Filter out any empty titles and append valid ones to the list
        titles.extend([title for title in page_titles if title])
        page += 1  # Move to the next page

    # Write titles to a text file with one title per line and no blank lines
    log_filename = f"{imin_number}_log.txt"
    with open(log_filename, "w", encoding="utf-8") as file:
        file.write("\n".join(titles))  # Join titles with a newline separator
    
    print(f"Scraping complete. Titles written to {log_filename}")

if __name__ == "__main__":
    # Get the imin number from the user
    imin_number = input("Enter the imin number: ")
    scrape_imin_titles(imin_number)