import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import re

async def scrape_properties():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://propertyonion.com/property_search")
        await page.wait_for_timeout(10000)  # wait for JS content to load

        content = await page.content()
        await browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        property_cards = soup.find_all('div', class_='p-card-content')

        data = []
        for card in property_cards:
            try:
                # Extract status
                status = card.find('div', class_='p-chip')
                status = status.text.strip() if status else 'N/A'

                # Extract date
                date_divs = card.select('div.flex.flex-wrap.text-right > div.px-2.pt-1')
                date = date_divs[-1].text.strip() if date_divs else 'N/A'

                # Extract address
                address_tag = card.find('div', class_='ellip')
                address_lines = address_tag.find_all('span') if address_tag else []
                address = ' '.join([line.text.strip() for line in address_lines]) if address_lines else 'N/A'

                # Extract Beds, Baths, Sqft using regex
                full_info = address_tag.get_text(separator=" ", strip=True) if address_tag else ''
                beds_match = re.search(r'(\d+)\s+Beds', full_info)
                baths_match = re.search(r'(\d+)\s+Baths', full_info)
                sqft_match = re.search(r'([\d,]+)\s+sqft', full_info)

                beds = beds_match.group(1) if beds_match else 'N/A'
                baths = baths_match.group(1) if baths_match else 'N/A'
                sqft = sqft_match.group(1).replace(',', '') if sqft_match else 'N/A'

                # Extract deal type (e.g., Wholesaler Deal)
                deal_tag = card.find('span', class_='ng-star-inserted')
                deal_type = deal_tag.text.strip() if deal_tag else 'N/A'

                if deal_type.lower() == 'for':
                    deal_type = 'N/A'  

                data.append({
                    'Status': status,
                    'Date': date,
                    'Deal Type': deal_type,
                    'Address': address,
                    'Beds': beds,
                    'Baths': baths,
                    'Sqft': sqft 
                })
            except Exception as e:
                print("Error parsing a card:", e)

        df = pd.DataFrame(data)
        df.to_csv('property_onion_listings.csv', index=False)
        print("✅ Data scraped and saved to 'property_onion_listings.csv'.")

# Wrap the async call in an event loop
def main():
    asyncio.run(scrape_properties())

if __name__ == "__main__":
    main()
