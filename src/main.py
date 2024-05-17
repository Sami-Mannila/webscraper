"""
A web scraper to extract real estate property listings
from a fictional real estate website.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_property_listings(url):
    """
    Fetch property listings from the given URL.

    Args:
        url (str): The URL of the real estate listings page.

    Returns:
        list: A list of dictionaries containing property details.
    """
    response = requests.get(url)

    if response.status_code != 200:
        print(f'Failed to retrieve the page. Status code: {response.status_code}')
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('div', class_='property-listing')

    properties = []

    for listing in listings:
        title = listing.find('h2', class_='title').text.strip()
        price = listing.find('span', class_='price').text.strip()
        address = listing.find('div', class_='address').text.strip()
        description = listing.find('p', class_='description').text.strip()

        properties.append({
            'Title': title,
            'Price': price,
            'Address': address,
            'Description': description
        })

    return properties

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
    url = 'https://example-realestate.com/properties'
    properties = fetch_property_listings(url)
    if properties:
        save_to_csv(properties, 'properties.csv')

if __name__ == '__main__':
    main()
