"""
Neckermann Nordic Turkey Hotel Scraper
Extracts all Turkey hotels with prices from neckermann-nordic.dk
Uses browser automation to get dynamically loaded content
"""

import requests
import json
import csv
import re
from datetime import datetime
from bs4 import BeautifulSoup


class TurkeyHotelScraper:
    def __init__(self, base_url="https://neckermann-nordic.dk"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        self.hotels = []

    def fetch_search_page(self, params=None):
        """Fetch the search page for Turkey hotels."""
        if params is None:
            # Default search for Turkey, 7 nights, 2 adults, from Copenhagen
            params = {
                'CHARTER': 'True',
                'CURRENCY': '4',
                'FILTER': '1',
                'FREIGHT': '1',
                'PARTITION_PRICE': '32',
                'PRICE_PAGE': '1',
                'RECONPAGE': '10',
                'SEARCH_MODE': 'b2c',
                'SORT_TYPE': '0',
                'NIGHTMIN': '7',
                'NIGHTMAX': '7',
                'TOURTYPE': '-1',
                'ADULT': '2',
                'TOWNFROM': '1941',  # Copenhagen
                'STATE': '9',  # Turkey
                'REGULAR': 'True',
                'ISCHARTER': '1',
                'SEARCH_TYPE': 'PACKET_TOUR',
                'CHECKIN_BEG': '20260626',
                'CHECKIN_END': '20260626',
                'DIRECTION': '1',
                'CLASSID': '0'
            }
        
        url = f"{self.base_url}/search/tours"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching search page: {e}")
            return None

    def extract_hotels_from_html(self, html):
        """Extract hotel data from the HTML page."""
        soup = BeautifulSoup(html, 'html.parser')
        hotels = []
        
        # Find all article elements (hotel cards)
        for article in soup.find_all('article'):
            text = article.get_text(separator=' ', strip=True)
            
            # Skip if not a hotel card
            if 'Hotel' not in text and 'Apart' not in text and 'Resort' not in text:
                continue
            
            # Extract hotel name
            name_match = re.search(r'^([A-Za-z\s\(\)]+(?:Apart|Hotel|Resort|Suite)[A-Za-z\s\(\)]*)', text)
            if not name_match:
                continue
            name = name_match.group(1).strip()
            
            # Clean up duplicate names
            name = re.sub(r'^(\w+(?:\s+\w+)*)\1$', r'\1', name)
            
            # Extract location
            location_match = re.search(r'(Alanya|Side|Kumkoy|Belek|Antalya|Kemer)', text)
            location = location_match.group(1) if location_match else ''
            
            # Extract price (discounted price)
            price_match = re.search(r'fra\s*([\d\.]+),-', text)
            price = price_match.group(1) if price_match else ''
            
            # Extract original price
            orig_price_match = re.search(r'([\d\.]+),-\s*Se\s+tilbud', text)
            orig_price = orig_price_match.group(1) if orig_price_match else ''
            
            # Extract board type (RO, BB, HB, AI, UAI)
            board_match = re.search(r'\b(RO|BB|HB|AI|UAI)\b', text)
            board_type = board_match.group(1) if board_match else ''
            
            # Extract room type
            room_match = re.search(r'(?:RO|BB|HB|AI|UAI)\s+([A-Za-z\s]+(?:Room|Studio|Suite|Apart|Bedroom))', text)
            room_type = room_match.group(1).strip() if room_match else ''
            
            # Extract temperature
            temp_match = re.search(r'(\d+(?:\.\d+)?)\s*°C', text)
            temperature = temp_match.group(1) if temp_match else ''
            
            # Check if few spots left
            few_spots = 'Der er få pladser tilbage' in text or 'few spots' in text.lower()
            
            # Extract hotel slug from link
            link = article.find('a', href=re.compile(r'/tours/turkey/'))
            slug = ''
            if link and link.get('href'):
                slug_match = re.search(r'/tours/turkey/([^?]+)', link['href'])
                if slug_match:
                    slug = slug_match.group(1)
            
            if name and price:
                hotels.append({
                    'name': name,
                    'slug': slug,
                    'location': location,
                    'price': price,
                    'original_price': orig_price,
                    'board_type': board_type,
                    'room_type': room_type,
                    'temperature': temperature,
                    'few_spots_left': few_spots,
                    'url': f"{self.base_url}/tours/turkey/{slug}" if slug else '',
                    'scraped_at': datetime.now().isoformat()
                })
        
        return hotels

    def scrape_turkey_hotels(self):
        """Scrape all Turkey hotels with prices."""
        print("Fetching Turkey search results...")
        html = self.fetch_search_page()
        if not html:
            print("Failed to fetch search page")
            return []
        
        print("Extracting hotel data...")
        self.hotels = self.extract_hotels_from_html(html)
        
        print(f"Found {len(self.hotels)} Turkey hotels")
        return self.hotels

    def save_to_json(self, filename="data/turkey_hotels.json"):
        """Save scraped data to JSON file."""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        data = {
            'hotels': self.hotels,
            'scraped_at': datetime.now().isoformat(),
            'total': len(self.hotels)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")

    def save_to_csv(self, filename="data/turkey_hotels.csv"):
        """Save hotel data to CSV file."""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.hotels:
            print("No hotel data to save")
            return
        
        keys = self.hotels[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.hotels)
        print(f"CSV saved to {filename}")

    def print_summary(self):
        """Print a summary of scraped data."""
        print("\n" + "="*60)
        print("TURKEY HOTELS - SCRAPING SUMMARY")
        print("="*60)
        print(f"Total hotels found: {len(self.hotels)}")
        print(f"Scraped at: {datetime.now().isoformat()}")
        
        if self.hotels:
            print("\n--- Hotels ---")
            for hotel in self.hotels:
                print(f"\n{hotel['name']}")
                print(f"  Location: {hotel['location']}")
                print(f"  Price: {hotel['price']},- DKK (was {hotel['original_price']},-)")
                print(f"  Room: {hotel['room_type']} ({hotel['board_type']})")
                print(f"  Temperature: {hotel['temperature']}°C")
                if hotel['few_spots_left']:
                    print(f"  ⚠️ Few spots left!")
                print(f"  URL: {hotel['url']}")


def main():
    """Main execution function."""
    scraper = TurkeyHotelScraper()
    
    # Scrape Turkey hotels
    scraper.scrape_turkey_hotels()
    
    # Save data
    scraper.save_to_json()
    scraper.save_to_csv()
    
    # Print summary
    scraper.print_summary()


if __name__ == "__main__":
    main()
