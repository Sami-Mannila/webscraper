"""
A web scraper to extract multiple real estate property listings
from a real estate website and save them to a CSV file.
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

def fetch_listing_urls(url):
    """
    Fetch listing URLs from the given URL using Selenium.

    Args:
        url (str): The URL of the listings page.

    Returns:
        list: A list of URLs for each property listing.
    """
    # Set up the WebDriver
    driver = webdriver.Chrome()  # or webdriver.Firefox() if you are using Firefox
    driver.get(url)
    
    # Wait for the listings to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'ot-card-v2__info-container'))
    )
    
    # Scroll to the bottom to ensure all listings are loaded
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Get the page source and parse it with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Identify the HTML elements containing the links to the individual property listings
    listing_tags = soup.find_all('a', class_='ot-card-v2 link link--muted')
    listing_urls = [tag['href'] for tag in listing_tags]
    
    driver.quit()
    
    print(f'Found {len(listing_urls)} listing URLs')
    return listing_urls

def fetch_property_details(url):
    """
    Fetch property details from the given URL.

    Args:
        url (str): The URL of the property listing page.

    Returns:
        dict: A dictionary containing property details.
    """
    print(f'Scraping URL: {url}')
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Failed to retrieve the page. Status code: {response.status_code}')
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract title
    title_tag = soup.find('h1', class_='heading heading--no-styling listing-header__headline listing-header__headline--secondary customer-color margined margined--v15')
    title = title_tag.text.strip() if title_tag else 'N/A'
    
    # Print the HTML around the price for debugging
    price_container = soup.select_one('div.card-v2-text-container__group.card-v2-text-container__group--boxed')
    if price_container:
        print(f'Price container HTML:\n{price_container.prettify()}')
    
    # Extract price
    price_tag = price_container.select_one('div.card-v2-text-container__column.card-v2-text-container__column--desktop-wide > h2.card-v2-text-container__title.heading.heading--title-3.ng-star-inserted') if price_container else None
    price = price_tag.text.strip() if price_tag else 'N/A'
    
    # Extract size
    size_tag = soup.select_one('div.card-v2-text-container__column:not(.card-v2-text-container__column--desktop-wide) > h2.card-v2-text-container__title.heading.heading--title-3.ng-star-inserted')
    size = size_tag.text.strip() if size_tag else 'N/A'
    
    # Extract location
    location_tag = soup.select_one('dd.info-table__value')
    location = ' '.join([part.text for part in location_tag.find_all('span', class_='link__text')]) if location_tag else 'N/A'
    
    # Extract description
    description_tag = soup.find('div', class_='listing-overview')
    description = ' '.join([p.text.strip() for p in description_tag.find_all('p')]) if description_tag else 'N/A'

    property_details = {
        'Title': title,
        'Price': price,
        'Size': size,
        'Location': location,
        'Description': description
    }

    return property_details

def save_to_csv(data, filename):
    """
    Save the data to a CSV file.

    Args:
        data (list): A list of dictionaries containing property details.
        filename (str): The name of the CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

def main():
    """
    Main function to scrape the real estate website and save data to CSV.
    """
    listings_url = 'https://asunnot.oikotie.fi/myytavat-asunnot?pagination=1&locations=%5B%5B5695451,4,%22Kalasatama,%20Helsinki%22%5D%5D&cardType=100&roomCount%5B%5D=2'  # URL of the filtered listings page
    listing_urls = fetch_listing_urls(listings_url)
    
    all_properties = []
    for url in listing_urls:
        property_details = fetch_property_details(url)
        if property_details:
            all_properties.append(property_details)
    
    if all_properties:
        save_to_csv(all_properties, 'properties.csv')
    else:
        print('No properties found.')

if __name__ == '__main__':
    main()
