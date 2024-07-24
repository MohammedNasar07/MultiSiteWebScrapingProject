# Web scraping script for multiple websites

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import csv
import requests
from io import BytesIO
from PIL import Image
from requests.exceptions import RequestException
from time import sleep


def scrape_coursera(browser, user_input):
    # Navigate to Coursera
    browser.get("https://www.coursera.org")
    browser.maximize_window()

    # Wait for the search input element to be clickable
    wait = WebDriverWait(browser, 10)
    search_input = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "react-autosuggest__input"))
    )

    # Locate the search button
    search_button = browser.find_element(
        By.XPATH,
        "//button[@class='nostyle search-button' and @aria-label='Submit Search']",
    )

    # Enter the search query and click the search button
    search_input.send_keys(user_input)
    search_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[@class='nostyle search-button' and @aria-label='Submit Search']",
            )
        )
    )
    browser.execute_script("arguments[0].click();", search_button)
    sleep(2)

    # Initialize lists to store course details
    course_details = []
    image_urls = []
    descriptions = []
    ratings = []
    durations = []

    # Loop through multiple pages of search results (up to 10 pages)
    for page in range(1):
        # Wait for the course titles, partner names, and images to load
        wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//h3[@class='cds-119 cds-CommonCard-title css-e7lgfl cds-121']",
                )
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "(//p[@class='cds-119 cds-ProductCard-partnerNames css-dmxkm1 cds-121'][1])",
                )
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//div[@class='cds-CommonCard-previewImage'][1])")
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//div[@class='cds-CommonCard-ratings'])")
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='cds-CommonCard-metadata']")
            )
        )

        # Find all the course titles, partner names, and images on the page
        course_titles = browser.find_elements(
            By.XPATH, "(//h3[@class='cds-119 cds-CommonCard-title css-e7lgfl cds-121'])"
        )
        partner_names = browser.find_elements(
            By.XPATH,
            "(//p[@class='cds-119 cds-ProductCard-partnerNames css-dmxkm1 cds-121'][1])",
        )
        image_elements = browser.find_elements(
            By.XPATH, "(//div[@class='cds-CommonCard-previewImage'][1])"
        )
        descriptions_elements = browser.find_elements(
            By.XPATH, "(//div[@class='cds-ProductCard-body'][1])"
        )
        ratings_elements = browser.find_elements(
            By.XPATH, "(//div[@class='cds-CommonCard-ratings'])"
        )
        durations_elements = browser.find_elements(
            By.XPATH, "(//div[@class='cds-CommonCard-metadata'])"
        )

        # Extract course details
        for i in range(len(course_titles)):
            course_title = course_titles[i].text
            partner_name = partner_names[i].text

            # Extract course description
            course_description = descriptions_elements[i].text
            descriptions.append(course_description)

            # Extract image URL
            image_url = (
                image_elements[i].find_element(By.TAG_NAME, "img").get_attribute("src")
            )
            image_urls.append(image_url)

            # Extract rating and duration
            rating = ratings_elements[i].text
            duration = durations_elements[i].text

            course_details.append([course_title, partner_name, rating, duration])

        # Click the 'Next' button to go to the next page of search results if it's available
        next_button = browser.find_element(
            By.XPATH,
            '//button[@class="cds-149 cds-iconButton-small cds-iconButton-secondary css-dbqm7e"]',
        )
        if "disabled" in next_button.get_attribute("class"):
            break  # No more pages available, exit the loop
        else:
            next_button.click()

    return course_details, descriptions, image_urls


def scrape_udemy(browser, user_input):
    # Navigate to Udemy
    browser.get("https://www.udemy.com")
    browser.maximize_window()

    # Wait for the search input element to be clickable
    wait = WebDriverWait(browser, 10)
    search_input = wait.until(EC.presence_of_element_located((By.NAME, "q")))

    # Locate the search button
    search_button = browser.find_element(By.XPATH, "//button[@type='submit']")

    # Enter the search query and click the search button
    search_input.send_keys(user_input)
    search_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    )
    browser.execute_script("arguments[0].click();", search_button)
    sleep(2)

    # Initialize lists to store course details
    course_details = []
    image_urls = []
    descriptions = []
    ratings = []
    durations = []

    # Loop through multiple pages of search results (up to 10 pages)
    for page in range(1):
        # Wait for the course titles, partner names, and images to load
        wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//h3[@class='udlite-focus-visible-target udlite-heading-md course-card--course-title--2f7tE']",
                )
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//div[@class='udlite-text-xs course-card--row--29Y0w'])")
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//img[@class='course-card--course-image--3QhbM'])")
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//span[@class='star-rating--rating-number--3lVe8'])")
            )
        )
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "(//span[@class='course-card--course-duration--27iCz'])")
            )
        )

        # Find all the course titles, partner names, and images on the page
        course_titles = browser.find_elements(
            By.XPATH,
            "(//h3[@class='udlite-focus-visible-target udlite-heading-md course-card--course-title--2f7tE'])",
        )
        partner_names = browser.find_elements(
            By.XPATH, "(//div[@class='udlite-text-xs course-card--row--29Y0w'])"
        )
        image_elements = browser.find_elements(
            By.XPATH, "(//img[@class='course-card--course-image--3QhbM'])"
        )
        descriptions_elements = browser.find_elements(
            By.XPATH,
            "(//p[@class='udlite-text-sm course-card--course-headline--yIrRk'])",
        )
        ratings_elements = browser.find_elements(
            By.XPATH, "(//span[@class='star-rating--rating-number--3lVe8'])"
        )
        durations_elements = browser.find_elements(
            By.XPATH, "(//span[@class='course-card--course-duration--27iCz'])"
        )

        # Extract course details
        for i in range(len(course_titles)):
            course_title = course_titles[i].text
            partner_name = partner_names[i].text

            # Extract course description
            course_description = descriptions_elements[i].text
            descriptions.append(course_description)

            # Extract image URL
            image_url = image_elements[i].get_attribute("src")
            image_urls.append(image_url)

            # Extract rating and duration
            rating = ratings_elements[i].text
            duration = durations_elements[i].text

            course_details.append([course_title, partner_name, rating, duration])

        # Click the 'Next' button to go to the next page of search results if it's available
        next_button = browser.find_element(
            By.XPATH, "//button[contains(@class, 'pagination--next--8cCMM')]"
        )
        if "disabled" in next_button.get_attribute("class"):
            break  # No more pages available, exit the loop
        else:
            next_button.click()

    return course_details, descriptions, image_urls


if __name__ == "__main__":
    user_input = input("Enter the course name: ")

    # Create a WebDriver instance
    browser = webdriver.Chrome()

    # Scrape data from Coursera
    coursera_details, coursera_descriptions, coursera_image_urls = scrape_coursera(
        browser, user_input
    )

    # Scrape data from Udemy
    udemy_details, udemy_descriptions, udemy_image_urls = scrape_udemy(
        browser, user_input
    )

    # Combine the results
    course_details = coursera_details + udemy_details
    descriptions = coursera_descriptions + udemy_descriptions
    image_urls = coursera_image_urls + udemy_image_urls

    # Save the results to a CSV file
    with open("course_details.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Course Title",
                "Partner Name",
                "Rating",
                "Duration",
                "Description",
                "Image URL",
            ]
        )
        for i in range(len(course_details)):
            writer.writerow(course_details[i] + [descriptions[i], image_urls[i]])

    print("Course details have been saved to course_details.csv")

    # Close the browser
    browser.quit()
