# Real Estate Property Listings Scraper
Author: Sami Mannila

This project contains scripts to scrape property listings and details from a real estate website. The data is saved into CSV files for further analysis or processing.

## Contents

- `element.html`: Sample HTML file for reference.
- `property_details.csv`: Example CSV file with property details.
- `README.md`: This README file.
- `properties.csv`: Another example CSV file with property details.
- `venv`: Virtual environment for the project.
- `.git`: Git version control directory.
- `src`: Directory containing the scraping scripts.

## Requirements

- Python 3.x
- Selenium
- BeautifulSoup4
- Requests
- pandas
- A web driver for your browser (ChromeDriver for Chrome or GeckoDriver for Firefox)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd webscraper
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download and install the web driver for your browser**:
   - [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)
   - [GeckoDriver](https://github.com/mozilla/geckodriver/releases)

## Usage

### Scripts

- `scrape_single_listing.py`: Script to scrape details of a single property listing.
- `scrape_multiple_listings.py`: Script to scrape details of multiple property listings.

### Running the Scripts

1. **Navigate to the `src` directory**:
   ```bash
   cd src
   ```

2. **Run the script for scraping multiple listings**:
   ```bash
   python scrape_multiple_listings.py
   ```

3. **Follow prompts**:
   - You will be prompted to use the default URL or provide a custom URL for the listings page.
   - The script will fetch all listing URLs, scrape details for each property, and save the data to `properties.csv`.

## Example

1. Run the script:
   ```bash
   python scrape_multiple_listings.py
   ```
2. Choose to use the default URL or provide a custom URL.
3. The script will scrape property details and save them to `properties.csv`.

## Notes

- Ensure that the web driver version matches your browser version.
- Adjust the waiting times in the script if you encounter issues with loading times.
- The scripts currently handle a specific real estate website structure; modifications may be needed for different websites.

## License

This project is licensed under the MIT License.

