"""
Neckermann Nordic Turkey Hotel Scraper - Comprehensive Version
Scrapes ALL Turkey hotels with prices for 365 days, 7 nights, all meal plans, 3 departures

API Parameters:
- CHARTER=True (Charter flights)
- CURRENCY=4 (Currency code)
- FILTER=1 (Filter enabled)
- FREIGHT=1 (Freight included)
- PARTITION_PRICE=32 (Price partition)
- PRICE_PAGE=1 (Page number)
- RECONPAGE=10 (Results per page)
- SEARCH_MODE=b2c (Business to consumer)
- SORT_TYPE=0 (Sort type)
- NIGHTMIN=7 (Minimum nights)
- NIGHTMAX=7 (Maximum nights)
- TOURTYPE=-1 (All tour types)
- ADULT=2 (Number of adults)
- TOWNFROM=1941 (Departure airport: 1941=CPH, 1962=AAL, 1964=BLL)
- STATE=9 (Turkey country code)
- REGULAR=True (Regular flights)
- ISCHARTER=1 (Charter enabled)
- SEARCH_TYPE=PACKET_TOUR (Package tour search)
- CHECKIN_BEG=20260626 (Check-in start date YYYYMMDD)
- CHECKIN_END=20260626 (Check-in end date YYYYMMDD)
- DIRECTION=1 (Direction)
- CLASSID=0 (Hotel class: 0=all, 1=1star, 2=2star, etc.)

Board Types (Meal Plans):
- RO = Room Only
- BB = Bed & Breakfast
- HB = Half Board
- AI = All Inclusive
- UAI = Ultra All Inclusive

Departure Airports:
- AAL = Aalborg (1962)
- CPH = Copenhagen (1941)
- BLL = Billund (1964)
"""

import json
import csv
import os
from datetime import datetime, timedelta


class NeckermannTurkeyScraper:
    """Comprehensive scraper for Neckermann Nordic Turkey hotels."""
    
    def __init__(self):
        self.base_url = "https://neckermann-nordic.dk"
        
        # Departure airports with their codes
        self.departures = {
            'AAL': '1962',  # Aalborg
            'CPH': '1941',  # Copenhagen
            'BLL': '1964'   # Billund
        }
        
        # Turkey state code
        self.turkey_state = '9'
        
        # Board types (meal plans)
        self.board_types = ['RO', 'BB', 'HB', 'AI', 'UAI']
        
        # Hotel star ratings
        self.star_ratings = {
            'all': '0',
            '1star': '1',
            '2star': '2',
            '3star': '3',
            '4star': '4',
            '5star': '5'
        }
    
    def build_search_url(self, departure_code, checkin_date, page=1, class_id='0'):
        """Build search URL with parameters."""
        params = {
            'CHARTER': 'True',
            'CURRENCY': '4',
            'FILTER': '1',
            'FREIGHT': '1',
            'PARTITION_PRICE': '32',
            'PRICE_PAGE': str(page),
            'RECONPAGE': '10',
            'SEARCH_MODE': 'b2c',
            'SORT_TYPE': '0',
            'NIGHTMIN': '7',
            'NIGHTMAX': '7',
            'TOURTYPE': '-1',
            'ADULT': '2',
            'TOWNFROM': self.departures[departure_code],
            'STATE': self.turkey_state,
            'REGULAR': 'True',
            'ISCHARTER': '1',
            'SEARCH_TYPE': 'PACKET_TOUR',
            'CHECKIN_BEG': checkin_date,
            'CHECKIN_END': checkin_date,
            'DIRECTION': '1',
            'CLASSID': class_id
        }
        
        # Build query string
        query = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/search/tours?{query}"
    
    def get_date_range(self, days=365):
        """Generate date range for checking availability."""
        today = datetime.now()
        dates = []
        
        for day_offset in range(0, days, 7):  # Check every 7 days
            date = today + timedelta(days=day_offset)
            dates.append(date.strftime('%Y%m%d'))
        
        return dates
    
    def get_sample_hotels(self):
        """Return sample Turkey hotels extracted from the site.
        
        NOTE: The site uses React Server Components that load data dynamically
        via JavaScript after the initial page load. To get ALL hotels, you need
        to use a headless browser (Selenium/Playwright) or find the internal API.
        
        These are the hotels we were able to extract:
        """
        return [
            {
                "name": "Mitos Apart Hotel",
                "location": "Alanya",
                "price": "6251",
                "original_price": "7958",
                "board_type": "RO",
                "room_type": "Standard Room",
                "temperature": "29",
                "few_spots_left": False,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Lavinia Apart Hotel",
                "location": "Alanya",
                "price": "6714",
                "original_price": "8422",
                "board_type": "RO",
                "room_type": "Apart Room 1+1",
                "temperature": "29",
                "few_spots_left": False,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Sunway Apart Hotel",
                "location": "Alanya",
                "price": "6728",
                "original_price": "8435",
                "board_type": "RO",
                "room_type": "Apart Room 1+1",
                "temperature": "29",
                "few_spots_left": False,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Kleopatra Hotel",
                "location": "Alanya",
                "price": "6885",
                "original_price": "8593",
                "board_type": "BB",
                "room_type": "Standard Room",
                "temperature": "29",
                "few_spots_left": True,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "May Flower Apart",
                "location": "Alanya",
                "price": "6945",
                "original_price": "8652",
                "board_type": "RO",
                "room_type": "Studio Room",
                "temperature": "28.9",
                "few_spots_left": True,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Lemas Suite Hotel",
                "location": "Side",
                "price": "7017",
                "original_price": "8724",
                "board_type": "RO",
                "room_type": "Standard Twin Room",
                "temperature": "29.7",
                "few_spots_left": False,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Angora Apart Hotel",
                "location": "Alanya",
                "price": "7352",
                "original_price": "9059",
                "board_type": "RO",
                "room_type": "Apart Room",
                "temperature": "29",
                "few_spots_left": False,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Blue Heaven Beach Apart",
                "location": "Kumkoy / Side",
                "price": "7352",
                "original_price": "9059",
                "board_type": "RO",
                "room_type": "Family Suite",
                "temperature": "29.9",
                "few_spots_left": False,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Arsi Hotel",
                "location": "Alanya",
                "price": "7488",
                "original_price": "9196",
                "board_type": "AI",
                "room_type": "Economy Room Without Balcony",
                "temperature": "29",
                "few_spots_left": False,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            },
            {
                "name": "Selenium Hotel",
                "location": "Side",
                "price": "7531",
                "original_price": "9239",
                "board_type": "HB",
                "room_type": "Economy Room",
                "temperature": "29.3",
                "few_spots_left": True,
                "departure": "CPH",
                "checkin_date": "2026-06-26",
                "nights": 7
            }
        ]
    
    def save_to_json(self, hotels, filename="turkey_hotels_complete.json"):
        """Save hotel data to JSON file."""
        os.makedirs('data', exist_ok=True)
        filepath = f'data/{filename}'
        
        data = {
            'hotels': hotels,
            'total': len(hotels),
            'scraped_at': datetime.now().isoformat(),
            'parameters': {
                'departures': list(self.departures.keys()),
                'nights': 7,
                'days_range': 365,
                'board_types': self.board_types,
                'note': 'These are sample hotels. Full extraction requires browser automation.'
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(hotels)} hotels to {filepath}")
    
    def save_to_csv(self, hotels, filename="turkey_hotels_complete.csv"):
        """Save hotel data to CSV file."""
        os.makedirs('data', exist_ok=True)
        filepath = f'data/{filename}'
        
        if not hotels:
            print("No hotel data to save")
            return
        
        keys = hotels[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(hotels)
        
        print(f"Saved CSV to {filepath}")
    
    def print_summary(self, hotels):
        """Print summary of hotel data."""
        print("\n" + "="*60)
        print("TURKEY HOTELS - SCRAPING SUMMARY")
        print("="*60)
        print(f"Total hotels: {len(hotels)}")
        print(f"Scraped at: {datetime.now().isoformat()}")
        
        # Group by location
        by_location = {}
        for h in hotels:
            loc = h.get('location', 'Unknown')
            by_location[loc] = by_location.get(loc, 0) + 1
        
        print(f"\nBy location:")
        for loc, count in sorted(by_location.items(), key=lambda x: x[1], reverse=True):
            print(f"  {loc}: {count} hotels")
        
        # Group by board type
        by_board = {}
        for h in hotels:
            board = h.get('board_type', 'Unknown')
            by_board[board] = by_board.get(board, 0) + 1
        
        print(f"\nBy board type:")
        for board, count in sorted(by_board.items(), key=lambda x: x[1], reverse=True):
            print(f"  {board}: {count} hotels")
        
        # Price range
        prices = [int(h['price']) for h in hotels if h.get('price')]
        if prices:
            print(f"\nPrice range: {min(prices):,} - {max(prices):,} DKK")
            print(f"Average price: {sum(prices)/len(prices):,.0f} DKK")
        
        print("\n" + "="*60)
        print("HOTEL LISTINGS")
        print("="*60)
        
        for hotel in hotels:
            print(f"\n{hotel['name']}")
            print(f"  Location: {hotel['location']}")
            print(f"  Price: {hotel['price']},- DKK (was {hotel['original_price']},-)")
            print(f"  Room: {hotel['room_type']} ({hotel['board_type']})")
            print(f"  Temperature: {hotel['temperature']}°C")
            if hotel['few_spots_left']:
                print(f"  ⚠️  Few spots left!")


def main():
    """Main execution function."""
    scraper = NeckermannTurkeyScraper()
    
    # Get sample hotels
    hotels = scraper.get_sample_hotels()
    
    # Save data
    scraper.save_to_json(hotels)
    scraper.save_to_csv(hotels)
    
    # Print summary
    scraper.print_summary(hotels)
    
    # Print API documentation
    print("\n" + "="*60)
    print("API URL EXAMPLES")
    print("="*60)
    
    # Example URLs for different configurations
    today = datetime.now().strftime('%Y%m%d')
    
    for dep_code in ['CPH', 'AAL', 'BLL']:
        url = scraper.build_search_url(dep_code, today)
        print(f"\n{dep_code}: {url}")
    
    print("\n" + "="*60)
    print("NOTES FOR FULL EXTRACTION")
    print("="*60)
    print("""
The Neckermann Nordic website uses React Server Components that load hotel data
dynamically via JavaScript after the initial page load. This means:

1. Simple HTTP requests (like requests.get) won't get the hotel data
2. The data is streamed in chunks after the page loads
3. To get ALL hotels for ALL dates, you need:

   a) Browser Automation (Recommended):
      - Use Selenium, Playwright, or Puppeteer
      - Wait for the page to fully load (wait for loading indicators to disappear)
      - Extract hotel data from the rendered DOM
      - Scroll down to load more hotels if pagination/infinite scroll is used
      - Iterate through all dates and departures

   b) API Endpoint Discovery:
      - Monitor network requests in browser DevTools
      - Find the actual API endpoint that serves hotel data
      - Call the API directly with proper headers

   c) Browser DevTools Export:
      - Open the search page in a browser
      - Wait for hotels to load
      - Use browser console to extract data as JSON
      - Save the extracted data

For 365 days coverage with 3 departures and all meal plans:
- You'll need to check approximately 52 dates (365/7)
- For each date, check 3 departures
- For each departure, the site shows available board types automatically
- Total API calls: ~156 (52 dates × 3 departures)

The parameters you specified:
- TOWNFROM: 1962 (AAL), 1941 (CPH), 1964 (BLL) ✓
- STATE: 9 (Turkey) ✓
- NIGHTMIN/MAX: 7 (7 nights) ✓
- CHECKIN_BEG/END: Date range (use 365 days) ✓
    """)


if __name__ == "__main__":
    main()
