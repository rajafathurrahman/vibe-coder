"""
Neckermann Nordic Web Scraper
Scrapes travel packages, hotels, and pricing from neckermann-nordic.dk
"""

import requests
import json
import csv
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup


class NeckermannScraper:
    def __init__(self, base_url="https://neckermann-nordic.dk"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7',
        })
        self.data = {
            'hotels': [],
            'destinations': [],
            'scraped_at': None
        }

    def fetch_page(self, url_path="/", retries=3, delay=2):
        """Fetch a page with retry logic."""
        url = f"{self.base_url}{url_path}"
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{retries} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
        return None

    def extract_nextjs_data(self, html):
        """Extract hotel data from Next.js flight scripts."""
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')
        hotels = []
        
        for script in scripts:
            if not script.string:
                continue
            
            text = script.string
            if 'initialData' not in text or 'hotel' not in text:
                continue
            
            # Extract the flight data string
            start_marker = 'self.__next_f.push([1,"'
            start_idx = text.find(start_marker)
            end_marker = '"])'
            end_idx = text.rfind(end_marker)
            
            if start_idx < 0 or end_idx <= start_idx:
                continue
            
            data_start = start_idx + len(start_marker)
            flight_data = text[data_start:end_idx]
            
            # Unescape the JSON string
            flight_data = flight_data.replace('\\"', '"').replace('\\\\', '\\')
            
            # Find initialData array
            idx = flight_data.find('"initialData":')
            if idx <= 0:
                continue
            
            start = idx + len('"initialData":')
            
            # Parse bracket by bracket to find array end
            bracket_count = 0
            in_string = False
            escape_next = False
            end = start
            
            for j in range(start, len(flight_data)):
                ch = flight_data[j]
                if escape_next:
                    escape_next = False
                    continue
                if ch == '\\':
                    escape_next = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if not in_string:
                    if ch == '[':
                        bracket_count += 1
                    elif ch == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = j + 1
                            break
            
            json_str = flight_data[start:end]
            try:
                data = json.loads(json_str)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'hotel' in item:
                            hotels.append(item)
            except json.JSONDecodeError:
                continue
        
        return hotels

    def extract_destinations(self, html):
        """Extract destination/region data from the page."""
        soup = BeautifulSoup(html, 'html.parser')
        destinations = []
        
        # Look for navigation links to destinations
        for link in soup.find_all('a', href=re.compile(r'/rejsemål|/destinationer')):
            destinations.append({
                'name': link.get_text(strip=True),
                'url': link.get('href'),
                'type': 'destination'
            })
        
        return destinations

    def scrape_homepage(self):
        """Scrape the homepage for featured hotels and destinations."""
        print("Fetching homepage...")
        html = self.fetch_page("/")
        if not html:
            print("Failed to fetch homepage")
            return
        
        print("Extracting hotel data...")
        hotels = self.extract_nextjs_data(html)
        self.data['hotels'].extend(hotels)
        
        print("Extracting destinations...")
        destinations = self.extract_destinations(html)
        self.data['destinations'].extend(destinations)
        
        self.data['scraped_at'] = datetime.now().isoformat()
        
        print(f"Found {len(hotels)} hotels and {len(destinations)} destinations")

    def scrape_hotel_page(self, slug):
        """Scrape a specific hotel page for detailed info."""
        # Extract hotel code from slug like "/tours/greece/ekavi-apartments"
        hotel_name = slug.split('/')[-1] if '/' in slug else slug
        url_path = f"/hotel/{hotel_name}"
        print(f"Fetching hotel page: {url_path}")
        html = self.fetch_page(url_path)
        if not html:
            return None
        
        # Extract detailed hotel info from the page
        soup = BeautifulSoup(html, 'html.parser')
        
        hotel_data = {
            'slug': slug,
            'url': f"{self.base_url}{url_path}",
            'title': soup.title.string if soup.title else None,
            'description': None,
            'images': [],
            'amenities': [],
            'rooms': [],
            'pricing': []
        }
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            hotel_data['description'] = meta_desc.get('content')
        
        # Extract images
        for img in soup.find_all('img', src=re.compile(r'hotel|room')):
            hotel_data['images'].append({
                'src': img.get('src'),
                'alt': img.get('alt', '')
            })
        
        # Extract amenities
        for amenity in soup.find_all(text=re.compile(r'WiFi|Pool|Restaurant|Bar|Gym|SPA')):
            hotel_data['amenities'].append(amenity.strip())
        
        return hotel_data

    def save_to_json(self, filename="data/hotels.json"):
        """Save scraped data to JSON file."""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {filename}")

    def save_to_csv(self, filename="data/hotels.csv"):
        """Save hotel data to CSV file."""
        import os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not self.data['hotels']:
            print("No hotel data to save")
            return
        
        # Flatten hotel data for CSV
        flat_hotels = []
        for hotel in self.data['hotels']:
            flat = {
                'hotel_id': hotel.get('hotel'),
                'name': hotel.get('name'),
                'slug': hotel.get('slug'),
                'region': hotel.get('regionLName'),
                'country': hotel.get('stateLName'),
                'star_rating': hotel.get('starGroupName'),
                'image_url': hotel.get('image', {}).get('Img') if hotel.get('image') else None,
                'scraped_at': self.data['scraped_at']
            }
            flat_hotels.append(flat)
        
        if flat_hotels:
            keys = flat_hotels[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(flat_hotels)
            print(f"CSV saved to {filename}")

    def print_summary(self):
        """Print a summary of scraped data."""
        print("\n" + "="*50)
        print("SCRAPING SUMMARY")
        print("="*50)
        print(f"Scraped at: {self.data['scraped_at']}")
        print(f"Total hotels: {len(self.data['hotels'])}")
        print(f"Total destinations: {len(self.data['destinations'])}")
        
        if self.data['hotels']:
            print("\n--- Hotels ---")
            for hotel in self.data['hotels']:
                print(f"- {hotel['name']} ({hotel.get('starGroupName', 'N/A')})")
                print(f"  Region: {hotel.get('regionLName', 'N/A')}, {hotel.get('stateLName', 'N/A')}")
                print(f"  URL: {self.base_url}{hotel.get('slug', '')}")
                print()


def main():
    """Main execution function."""
    scraper = NeckermannScraper()
    
    # Scrape homepage
    scraper.scrape_homepage()
    
    # Scrape detailed info for first hotel (optional)
    if scraper.data['hotels']:
        first_hotel = scraper.data['hotels'][0]
        slug = first_hotel.get('slug', '')
        if slug:
            # Extract slug from path like "/tours/greece/ekavi-apartments"
            detail = scraper.scrape_hotel_page(slug)
            if detail:
                print(f"\nDetailed info for {first_hotel['name']}:")
                print(f"  Description: {detail['description'][:100]}..." if detail['description'] else "  No description")
                print(f"  Images found: {len(detail['images'])}")
    
    # Save data
    scraper.save_to_json()
    scraper.save_to_csv()
    
    # Print summary
    scraper.print_summary()


if __name__ == "__main__":
    main()
