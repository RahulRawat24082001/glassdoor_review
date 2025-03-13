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
REVIEWS_URL = "https://www.glassdoor.co.in/Reviews/Blackcoffer-Reviews-E2260916.htm"

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
    reviews = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "review-details_reviewContainer__vkVM6")))
    print(f"Found {len(reviews)} reviews.")

    # Function to extract text safely
    def get_text(review, by, selector, default="N/A"):
        try:
            element = review.find_element(by, selector)
            return element.text.strip() or default
        except Exception:
            return default

    # Function to extract sub-ratings (adjust after inspection)
    def get_sub_rating(review, category, default="N/A"):
        try:
            # Placeholder: Look for sub-ratings in expanded content
            rating_elements = review.find_elements(By.CLASS_NAME, "subRatings__SubRating")  # Hypothetical class
            for elem in rating_elements:
                if category.lower() in elem.text.lower():
                    return elem.find_element(By.CLASS_NAME, "ratingNumber").text.strip() or default
            return default
        except Exception:
            return default

    data = []
    for index, review in enumerate(reviews, start=1):
        try:
            # Click "Show more" to reveal full details
            show_more = review.find_elements(By.CLASS_NAME, "expand-button_ExpandButton__Wevvg")
            if show_more:
                show_more[0].click()
                time.sleep(1)

            # Extract review details
            date = get_text(review, By.TAG_NAME, "time", "N/A").split("T")[0] if "T" in get_text(review, By.TAG_NAME, "time", "N/A") else get_text(review, By.TAG_NAME, "time", "N/A")
            review_title = get_text(review, By.XPATH, ".//h3[@data-test='review-details-title']/span")
            position = get_text(review, By.CLASS_NAME, "review-avatar_avatarLabel__P15ey")
            tags = review.find_elements(By.CLASS_NAME, "tag_TagContainer___7Coz")
            emp_status = tags[0].text if tags else "N/A"
            location = tags[1].text if len(tags) > 1 else "N/A"
            overall_rating = get_text(review, By.CLASS_NAME, "ratingNumber", "N/A")  # Adjust if needed
            pros = get_text(review, By.XPATH, ".//span[@data-test='review-text-PROS']")
            cons = get_text(review, By.XPATH, ".//span[@data-test='review-text-CONS']")
            recommend = "Yes" if "Recommend" in get_text(review, By.CLASS_NAME, "rating-icon_ratingContainer__9UoJ6") else "No"

            # Extract sub-ratings
            work_life_balance = get_sub_rating(review, "Work/Life")
            culture_values = get_sub_rating(review, "Culture")
            diversity_inclusion = get_sub_rating(review, "Diversity")
            career_opportunities = get_sub_rating(review, "Career")
            compensation_benefits = get_sub_rating(review, "Compensation")
            senior_management = get_sub_rating(review, "Senior")

            # Append data
            data.append([
                index, "Blackcoffer", date, review_title, position, location, emp_status, overall_rating,
                work_life_balance, culture_values, diversity_inclusion, career_opportunities,
                compensation_benefits, senior_management, pros, cons, recommend, REVIEWS_URL
            ])
            print(f"Extracted review {index} successfully: {review_title}")

        except Exception as e:
            print(f"Error extracting review {index}: {e}")

    # Debug: Print data before saving
    print("\nExtracted Data Preview:")
    for row in data[:2]:  # Show first 2 rows
        print(row)

    # Step 6: Save Data to Excel with a unique filename
    output_file = "Glassdoor_Reviews_new.xlsx"  # Changed to avoid conflicts
    columns = [
        "S.N.", "Company name", "Date", "Review", "Position", "Location", "Employee status",
        "Overall rating", "Work/Life balance", "Culture and values", "Diversity and inclusion",
        "Career opportunities", "Compensation and benefits", "Senior management", "Pros", "Cons",
        "Recommend", "URL"
    ]

    df = pd.DataFrame(data, columns=columns)
    df.to_excel(output_file, index=False)

    print(f"✅ Data extraction complete! Check '{output_file}'.")
    print(f"Total reviews extracted: {len(data)}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()