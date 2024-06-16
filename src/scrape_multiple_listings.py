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
import csv


def fetch_listing_urls(base_url):
    """
    Fetch listing URLs from all paginated pages using Selenium.

    Args:
        base_url (str): The base URL of the listings page without pagination index.

    Returns:
        list: A list of URLs for each property listing.
    """
    all_listing_urls = []
    page_index = 1
    while True:
        url = f"{base_url}&pagination={page_index}"
        print(f"Fetching listings from: {url}")

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
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
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

        print(f'Found {len(listing_urls)} listing URLs on page {page_index}')

        all_listing_urls.extend(listing_urls)
        if len(listing_urls) < 25:
            break

        page_index += 1

    return all_listing_urls


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
    title_tag = soup.find(
        'h1',
        class_='heading heading--no-styling listing-header__headline listing-header__headline--secondary customer-color margined margined--v15',
    )
    title = title_tag.text.strip() if title_tag else 'N/A'

    # Extract price and size
    header_primary = soup.find(
        'h2',
        class_='heading heading--title-1 listing-header__headline listing-header__headline--primary customer-color',
    )
    price = 'N/A'
    size = 'N/A'
    if header_primary:
        header_texts = header_primary.find_all('span', class_='listing-header__text')
        if len(header_texts) >= 2:
            price = header_texts[0].text.strip()
            size = header_texts[1].text.strip()

    # Extract address
    address_tag = title_tag.find('span', class_='listing-header__text')
    address = address_tag.text.strip() if address_tag else 'N/A'

    # Extract description
    description_tag = soup.find('span', class_='listing-header__text listing-header__text--cut-overflow')
    description = description_tag.text.strip() if description_tag else 'N/A'

    # Initialize variables for additional details
    building_year = 'N/A'
    apartment_type = 'N/A'
    debt_free_price = 'N/A'
    maintenance_charge = 'N/A'
    living_area = 'N/A'
    rooms = 'N/A'
    floor = 'N/A'
    district = 'N/A'
    city = 'N/A'

    # Extract additional details from the content section
    content_section = soup.find(
        'div',
        class_='content content--primary-background center-on-wallpaper padded padded--v10-h15 padded--desktop-v10-h15 padded--xdesktop-v10-h0 padded--topless',
    )
    if content_section:
        for dl in content_section.find_all('dl'):
            dt = dl.find('dt', class_='details-grid__item-title')
            dd = dl.find('dd', class_='details-grid__item-value')
            if dt and dd:
                key = dt.text.strip()
                value = dd.text.strip()
                if key == 'Rakennusvuosi':
                    building_year = value
                elif key == 'Rakennuksen tyyppi':
                    apartment_type = value
                elif key == 'Velaton hinta':
                    debt_free_price = value
                elif key == 'Hoitovastike':
                    maintenance_charge = value
                elif key == 'Asuinpinta-ala':
                    living_area = value
                elif key == 'Huoneita':
                    rooms = value
                elif key == 'Kerros':
                    floor = value
                elif key == 'Kaupunginosa':
                    district = value
                elif key == 'Kaupunki':
                    city = value
            else:
                print(f"Failed to find dt or dd in {dl}")
    else:
        print("Content section not found")

    property_details = {
        'Title': title,
        'Price': price,
        'Size': size,
        'Address': address,
        'Description': description,
        'Building Year': building_year,
        'Apartment Type': apartment_type,
        'Debt-free Price': debt_free_price,
        'Maintenance Charge': maintenance_charge,
        'Living Area': living_area,
        'Rooms': rooms,
        'Floor': floor,
        'District': district,
        'City': city,
    }

    return property_details


def save_to_csv(data, filename):
    """
    Save the data to a CSV file.

    Args:
        data (list): A list of dictionaries containing property details.
        filename (str): The name of the CSV file.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        # Write the headers
        headers = [
            'Title',
            'Price',
            'Size',
            'Address',
            'Description',
            'Building Year',
            'Apartment Type',
            'Debt-free Price',
            'Maintenance Charge',
            'Living Area',
            'Rooms',
            'Floor',
            'District',
            'City',
        ]
        writer.writerow(headers)

        # Write the data
        for item in data:
            row = [
                item['Title'],
                item['Price'],
                item['Size'],
                item['Address'],
                item['Description'],
                item['Building Year'],
                item['Apartment Type'],
                item['Debt-free Price'],
                item['Maintenance Charge'],
                item['Living Area'],
                item['Rooms'],
                item['Floor'],
                item['District'],
                item['City'],
            ]
            writer.writerow(row)

    print(f'Data saved to {filename}')


def main():
    """
    Main function to scrape the real estate website and save data to CSV.
    """
    base_url = 'https://asunnot.oikotie.fi/myytavat-asunnot?locations=%5B%5B5695451,4,%22Kalasatama,%20Helsinki%22%5D%5D&cardType=100&roomCount%5B%5D=2'  # Base URL of the filtered listings page
    listing_urls = fetch_listing_urls(base_url)

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
