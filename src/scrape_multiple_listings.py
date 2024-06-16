"""
Script to scrape property listings and details from a real estate website.
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re

def fetch_listing_urls(base_url):
    """
    Fetch all listing URLs from the given base URL.
    
    Args:
        base_url (str): The base URL to fetch the listings from.

    Returns:
        list: A list of listing URLs.
    """
    all_listing_urls = []
    page_index = 1
    while True:
        url = f"{base_url}&pagination={page_index}"
        print(f"Fetching listings from: {url}")

        driver = webdriver.Chrome()  # or webdriver.Firefox() if you are using Firefox
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'ot-card-v2__info-container'))
        )

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

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        listing_tags = soup.find_all('a', class_='ot-card-v2 link link--muted')
        listing_urls = [tag['href'] for tag in listing_tags]

        driver.quit()

        print(f'Found {len(listing_urls)} listing URLs on page {page_index}')

        all_listing_urls.extend(listing_urls)
        if len(listing_urls) < 10:
            break

        page_index += 1

    return all_listing_urls

def parse_numeric_value(value, unit=None):
    """
    Parse numeric values from strings, handling units and formatting.
    
    Args:
        value (str): The string containing the numeric value.
        unit (str, optional): The unit to be removed from the string. Defaults to None.

    Returns:
        str: The parsed numeric value as a string.
    """
    if unit:
        value = value.split(unit)[0]
    value = re.sub(r"[^\d,\.]", "", value)
    value = value.replace(',', '.')
    return value

def fetch_property_details(url):
    """
    Fetch property details from a given URL.
    
    Args:
        url (str): The URL of the property listing.

    Returns:
        dict: A dictionary containing property details.
    """
    print(f'Scraping URL: {url}')
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Failed to retrieve the page. Status code: {response.status_code}')
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')

    title_tag = soup.find(
        'h1',
        class_='heading heading--no-styling listing-header__headline listing-header__headline--secondary customer-color margined margined--v15',
    )
    title = title_tag.text.strip() if title_tag else 'N/A'

    header_primary = soup.find(
        'h2',
        class_='heading heading--title-1 listing-header__headline listing-header__headline--primary customer-color',
    )
    price = 'N/A'
    size = 'N/A'
    if header_primary:
        header_texts = header_primary.find_all('span', class_='listing-header__text')
        if len(header_texts) >= 2:
            price = parse_numeric_value(header_texts[0].text.strip(), "€")
            size = parse_numeric_value(header_texts[1].text.strip(), "m²")

    address_tag = title_tag.find('span', class_='listing-header__text')
    address = address_tag.text.strip() if address_tag else 'N/A'

    description_tag = soup.find('span', class_='listing-header__text listing-header__text--cut-overflow')
    description = description_tag.text.strip() if description_tag else 'N/A'

    building_year = 'N/A'
    apartment_type = 'N/A'
    debt_free_price = 'N/A'
    maintenance_charge = 'N/A'
    living_area = 'N/A'
    rooms = 'N/A'
    floor = 'N/A'
    total_floors = 'N/A'
    district = 'N/A'
    city = 'N/A'

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
                    debt_free_price = parse_numeric_value(value, "€")
                elif key == 'Hoitovastike':
                    maintenance_charge = parse_numeric_value(value, "€ / kk")
                elif key == 'Asuinpinta-ala':
                    living_area = parse_numeric_value(value, "m²")
                elif key == 'Huoneita':
                    rooms = value
                elif key == 'Kerros':
                    floor_info = value.split('/')
                    if len(floor_info) == 2:
                        floor = parse_numeric_value(floor_info[0])
                        total_floors = parse_numeric_value(floor_info[1])
                    else:
                        floor = parse_numeric_value(value)
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
        'Total Floors': total_floors,
        'District': district,
        'City': city,
    }

    return property_details

def save_to_csv(data, filename):
    """
    Save the property details to a CSV file.
    
    Args:
        data (list): List of dictionaries containing property details.
        filename (str): The name of the file to save the data to.
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        headers = [
            'Title',
            'Price (€)',
            'Size (m²)',
            'Address',
            'Description',
            'Building Year',
            'Apartment Type',
            'Debt-free Price (€)',
            'Maintenance Charge (€ / month)',
            'Living Area (m²)',
            'Rooms',
            'Floor',
            'Total Floors',
            'District',
            'City',
        ]
        writer.writerow(headers)

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
                item['Total Floors'],
                item['District'],
                item['City'],
            ]
            writer.writerow(row)

    print(f'Data saved to {filename}')

def main():
    """
    Main function to execute the scraping process.
    """
    use_default = input('Do you want to use the default URL? (yes/no): ').strip().lower()
    if use_default == 'yes':
        base_url = 'https://asunnot.oikotie.fi/myytavat-asunnot?locations=%5B%5B5695451,4,%22Kalasatama,%20Helsinki%22%5D%5D&cardType=100&roomCount%5B%5D=2'
    else:
        base_url = input('Please enter the listings page URL: ')

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
