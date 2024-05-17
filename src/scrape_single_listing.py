"""
A web scraper to extract a single real estate property listing
from a real estate website and save it to a CSV file.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_property_details(url):
    """
    Fetch property details from the given URL.

    Args:
        url (str): The URL of the property listing page.

    Returns:
        dict: A dictionary containing property details.
    """
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Failed to retrieve the page. Status code: {response.status_code}')
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract title
    title = soup.find('h1', class_='heading heading--no-styling listing-header__headline listing-header__headline--secondary customer-color margined margined--v15').text.strip() if soup.find('h1', class_='heading heading--no-styling listing-header__headline listing-header__headline--secondary customer-color margined margined--v15') else 'N/A'
    
    # Extract price using the detailed CSS selector path
    price = soup.select_one('body > main > section > div.content.content--primary-background.center-on-wallpaper.padded.padded--v30-h0.padded--desktop-v50-h15.padded--xdesktop-v50-h0.padded--topless > div > div > div.listing-columns__left > div.listing-details-container > div:nth-child(2) > dl > div:nth-child(1) > dd').text.strip() if soup.select_one('body > main > section > div.content.content--primary-background.center-on-wallpaper.padded.padded--v30-h0.padded--desktop-v50-h15.padded--xdesktop-v50-h0.padded--topless > div > div > div.listing-columns__left > div.listing-details-container > div:nth-child(2) > dl > div:nth-child(1) > dd') else 'N/A'
    
    # Extract location
    location_tag = soup.select_one('body > main > section > div.content.content--primary-background.center-on-wallpaper.padded.padded--v30-h0.padded--desktop-v50-h15.padded--xdesktop-v50-h0.padded--topless > div > div > div.listing-columns__left > div.listing-details-container > div:nth-child(2) > dl > div:nth-child(2) > dd')
    location = ' '.join([part.text for part in location_tag.find_all('span', class_='link__text')]) if location_tag else 'N/A'
    
    # Extract description
    description_tag = soup.find('div', class_='listing-overview')
    description = ' '.join([p.text.strip() for p in description_tag.find_all('p')]) if description_tag else 'N/A'

    property_details = {
        'Title': title,
        'Price': price,
        'Location': location,
        'Description': description
    }

    return property_details

def save_to_csv(data, filename):
    """
    Save the data to a CSV file.

    Args:
        data (dict): A dictionary containing property details.
        filename (str): The name of the CSV file.
    """
    df = pd.DataFrame([data])
    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

def main():
    """
    Main function to scrape the real estate website and save data to CSV.
    """
    url = 'https://asunnot.oikotie.fi/myytavat-asunnot/hollola/17674777'
    property_details = fetch_property_details(url)
    if property_details:
        save_to_csv(property_details, 'property_details.csv')

if __name__ == '__main__':
    main()
