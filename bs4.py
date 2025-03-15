from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import pandas as pd

# Credentials (Enter manually for security)
GLASSDOOR_EMAIL = "tempmail@vafyxh.com"  # Change to your email
GLASSDOOR_PASSWORD = "Test123!"  # Change to your password

# URLs
LOGIN_URL = "https://www.glassdoor.co.in/profile/login_input.htm"
REVIEWS_URL = "https://www.glassdoor.co.in/Reviews/Blackcoffer-Reviews-E2260916.htm?filter.iso3Language=eng"

# Initialize undetected Chrome driver
options = uc.ChromeOptions()
options.headless = False  # Set to True to run in the background
driver = uc.Chrome(options=options)

try:
    # Step 1: Navigate to Glassdoor Login Page
    driver.get(LOGIN_URL)
    time.sleep(2)  # Wait for page to load

    # Step 2: Enter Email
    email_field = driver.find_element(By.ID, "inlineUserEmail")
    email_field.send_keys(GLASSDOOR_EMAIL)
    email_field.send_keys(Keys.RETURN)
    time.sleep(2)

    # Step 3: Enter Password
    password_field = driver.find_element(By.ID, "inlineUserPassword")
    password_field.send_keys(GLASSDOOR_PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

    # Step 4: Navigate to Reviews Page After Login
    driver.get(REVIEWS_URL)
    time.sleep(2)  # Allow page to load

    # Step 5: Wait for Reviews
    wait = WebDriverWait(driver, 15)

    # Function to extract text safely
    def get_text(review, by, selector, default="N/A"):
        try:
            element = review.find_element(by, selector)
            return element.text.strip() or default
        except Exception:
            return default

    data = []
    
    # Loop through pages
    page_num = 1
    while True:
        print(f"Scraping page {page_num}...")
        
        reviews = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "review-details_reviewContainer__vkVM6")))

        for index, review in enumerate(reviews, start=len(data) + 1):
            try:
                # Extract review details
                date = get_text(review, By.XPATH, "//*[@id='empReview_94226343']/div[1]/div[2]/span", "N/A")
                review_title = get_text(review, By.XPATH, ".//h3[@data-test='review-details-title']/span")
                position = get_text(review, By.CLASS_NAME, "review-avatar_avatarLabel__P15ey")
                overall_rating = get_text(review, By.XPATH, "//*[@id='empReview_94132158']/div[1]/div[1]/div/div[2]/span", "N/A")
                pros = get_text(review, By.XPATH, ".//span[@data-test='review-text-PROS']")
                cons = get_text(review, By.XPATH, ".//span[@data-test='review-text-CONS']")
                
                # Extract Employee Status and Location
                tags = review.find_elements(By.CLASS_NAME, "tag_TagContainer___7Coz")
                emp_status = tags[0].text if tags else "N/A"
                location = tags[1].text if len(tags) > 1 else "N/A"

                data.append([
                    index, "Blackcoffer", date, review_title, position, location, emp_status, overall_rating, pros, cons, REVIEWS_URL
                ])
                print(f"Extracted review {index}: {review_title}")

            except Exception as e:
                print(f"Error extracting review {index}: {e}")

        # Pagination Fix: Check for the "Next" button
        try:
            next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next']")

            # **Check if the button is disabled (last page reached)**
            if "disabled" in next_button.get_attribute("class"):
                print("No more pages to extract. Stopping.")
                break

            # If it's enabled, click and continue
            next_button.click()
            time.sleep(3)  # Wait for the next page to load
            page_num += 1

        except Exception:
            print("Next button not found. Scraping complete.")
            break

    # Save Data to Excel
    output_file = "Glassdoor_Reviews_Fixed.xlsx"
    columns = [
        "S.N.", "Company Name", "Date", "Review Title", "Position", "Location", "Employee Status",
        "Overall Rating", "Pros", "Cons", "URL"
    ]
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(output_file, index=False)

    print(f"Data extraction complete! Check '{output_file}'.")
    print(f"Total reviews extracted: {len(data)}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
