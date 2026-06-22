"""
Neckermann Nordic Turkey Hotel Scraper - Complete Working Version
Scrapes ALL Turkey hotels with prices for 365 days, 7 nights, all meal plans, 3 departures

API Endpoint: https://neckermann-nordic.dk/api/search
Method: GET
Parameters: See build_params() method

Author: AI Assistant
Date: 2026-06-22
"""

import requests
import json
import csv
import os
from datetime import datetime, timedelta
import time


class NeckermannTurkeyScraper:
    """Complete scraper for Neckermann Nordic Turkey hotels."""
    
    def __init__(self):
        self.base_url = "https://neckermann-nordic.dk"
        self.api_url = "https://neckermann-nordic.dk/api/search"
        
        # Departure airports (TOWNFROM codes)
        self.departures = {
            'AAL': '1962',  # Aalborg
            'CPH': '1941',  # Copenhagen
            'BLL': '1964'   # Billund
        }
        
        # Turkey state code
        self.turkey_state = '9'
        
        # Meal plans (board types)
        self.meal_plans = {
            'RO': 'Room Only',
            'BB': 'Bed & Breakfast',
            'HB': 'Half Board',
            'AI': 'All Inclusive',
            'UAI': 'Ultra All Inclusive'
        }
        
        # Headers from browser (required for API access)
        self.headers = {
            'accept': 'application/json',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://neckermann-nordic.dk/search',
            'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
        }
        
        self.all_hotels = []
    
    def build_params(self, departure_code, checkin_beg, checkin_end, price_page=1):
        """Build API parameters for search.
        
        Args:
            departure_code: Airport code (AAL, CPH, BLL)
            checkin_beg: Check-in start date (YYYYMMDD)
            checkin_end: Check-in end date (YYYYMMDD)
            price_page: Page number for pagination
            
        Returns:
            dict: API parameters
        """
        return {
            'CHARTER': 'True',
            'ADULT': '2',
            'CHECKIN_BEG': checkin_beg,
            'CHECKIN_END': checkin_end,
            'CHILD': '0',
            'COSTMAX': '',
            'COSTMIN': '',
            'CURRENCY': '4',
            'FILTER': '1',
            'FREIGHT': '1',
            'PARTITION_PRICE': '32',
            'PRICE_PAGE': str(price_page),
            'RECONPAGE': '10',
            'REGULAR': 'True',
            'SEARCH_MODE': 'b2c',
            'SEARCH_TYPE': 'PACKET_TOUR',
            'SORT_TYPE': '0',
            'STATE': self.turkey_state,
            'THE_BEST_AT_TOP': 'true',
            'TOWNFROM': self.departures[departure_code],
            'TOWNTO': '',
            'NIGHTMIN': '7',
            'NIGHTMAX': '7',
            'HOTELLIST': '',
            'STARLIST': '',
            'MEALLIST': '',
            'HOTELATTR': '',
            'REGIONTO': '',
            'xdebug': 'true',
            'TOURTYPE': '-1',
        }
    
    def fetch_page(self, departure_code, checkin_beg, checkin_end, price_page=1):
        """Fetch a page of results from API.
        
        Args:
            departure_code: Airport code (AAL, CPH, BLL)
            checkin_beg: Check-in start date (YYYYMMDD)
            checkin_end: Check-in end date (YYYYMMDD)
            price_page: Page number
            
        Returns:
            list/dict: API response data or None
        """
        params = self.build_params(departure_code, checkin_beg, checkin_end, price_page)
        
        try:
            resp = requests.get(self.api_url, params=params, headers=self.headers, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def parse_hotel(self, price_data, departure_code, checkin_date):
        """Parse hotel data from API response.
        
        Args:
            price_data: Raw price data from API
            departure_code: Airport code
            checkin_date: Check-in date string
            
        Returns:
            dict: Parsed hotel data
        """
        return {
            'name': price_data.get('hotelName', ''),
            'name_local': price_data.get('hotelLName', ''),
            'star_rating': price_data.get('starName', ''),
            'meal_plan': price_data.get('mealName', ''),
            'meal_plan_local': price_data.get('mealLName', ''),
            'room_type': price_data.get('roomName', ''),
            'room_type_local': price_data.get('roomLName', ''),
            'ht_place': price_data.get('htPlaceName', ''),
            'price': price_data.get('price', 0),
            'original_price': price_data.get('priceOld', 0),
            'check_in': price_data.get('checkIn', ''),
            'check_out': price_data.get('checkOut', ''),
            'nights': price_data.get('nights', 7),
            'departure': departure_code,
            'full_number': price_data.get('fullNumber', ''),
            'hotel_inc': price_data.get('hotelInc', ''),
            'town_inc': price_data.get('townInc', ''),
            'star_inc': price_data.get('starInc', ''),
            'econom_in': price_data.get('economIn', 0),
            'econom_out': price_data.get('economOut', 0),
            'spog': price_data.get('spog', ''),
            'cat_claim': price_data.get('cat_Claim', ''),
            'cat_claim_inc': price_data.get('cat_Claim_Inc', ''),
            'scraped_at': datetime.now().isoformat()
        }
    
    def scrape_date_range(self, departure_code, days_range=365):
        """Scrape hotels for a date range.
        
        Args:
            departure_code: Airport code (AAL, CPH, BLL)
            days_range: Number of days to check (default 365)
            
        Returns:
            list: List of hotel dictionaries
        """
        today = datetime.now()
        all_hotels = []
        
        print(f"\n{'='*60}")
        print(f"Scraping for {departure_code} - {days_range} days range")
        print(f"{'='*60}")
        
        # Check every 7 days for the specified range
        for day_offset in range(0, days_range, 7):
            checkin_date = today + timedelta(days=day_offset)
            checkin_beg = checkin_date.strftime('%Y%m%d')
            checkin_end = (checkin_date + timedelta(days=6)).strftime('%Y%m%d')
            
            print(f"\nDate: {checkin_date.strftime('%Y-%m-%d')} (offset: {day_offset})")
            
            # Fetch first page
            data = self.fetch_page(departure_code, checkin_beg, checkin_end, 1)
            
            if data and isinstance(data, list) and len(data) > 0:
                item = data[0]
                
                if 'prices' in item:
                    prices = item['prices']
                    print(f"  Found {len(prices)} hotels on page 1")
                    
                    # Parse hotels from first page
                    for price_data in prices:
                        hotel = self.parse_hotel(price_data, departure_code, checkin_date.strftime('%Y-%m-%d'))
                        all_hotels.append(hotel)
                    
                    # Get total pages and fetch remaining
                    pages = item.get('pages', 1)
                    print(f"  Total pages: {pages}")
                    
                    for page in range(2, min(pages + 1, 20)):  # Limit to 20 pages
                        print(f"  Fetching page {page}...")
                        data = self.fetch_page(departure_code, checkin_beg, checkin_end, page)
                        
                        if data and isinstance(data, list) and len(data) > 0 and 'prices' in data[0]:
                            prices = data[0]['prices']
                            print(f"    Found {len(prices)} hotels")
                            
                            for price_data in prices:
                                hotel = self.parse_hotel(price_data, departure_code, checkin_date.strftime('%Y-%m-%d'))
                                all_hotels.append(hotel)
                        
                        time.sleep(0.5)  # Rate limiting
                else:
                    print(f"  No prices found in response")
            else:
                print(f"  No data returned")
            
            time.sleep(1)  # Rate limiting between dates
        
        return all_hotels
    
    def scrape_all_departures(self, days_range=365):
        """Scrape hotels for all departure airports.
        
        Args:
            days_range: Number of days to check (default 365)
            
        Returns:
            list: Combined list of all hotels
        """
        all_results = []
        
        for dep_code in self.departures.keys():
            hotels = self.scrape_date_range(dep_code, days_range)
            all_results.extend(hotels)
        
        return all_results
    
    def save_to_json(self, filename="turkey_hotels_all.json"):
        """Save results to JSON file.
        
        Args:
            filename: Output filename
        """
        os.makedirs('data', exist_ok=True)
        filepath = f'data/{filename}'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'hotels': self.all_hotels,
                'total': len(self.all_hotels),
                'scraped_at': datetime.now().isoformat(),
                'parameters': {
                    'departures': list(self.departures.keys()),
                    'nights': 7,
                    'days_range': 365,
                    'meal_plans': list(self.meal_plans.keys())
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(self.all_hotels)} hotels to {filepath}")
    
    def save_to_csv(self, filename="turkey_hotels_all.csv"):
        """Save results to CSV file.
        
        Args:
            filename: Output filename
        """
        os.makedirs('data', exist_ok=True)
        filepath = f'data/{filename}'
        
        if not self.all_hotels:
            print("No hotel data to save")
            return
        
        keys = self.all_hotels[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.all_hotels)
        
        print(f"Saved CSV to {filepath}")
    
    def print_summary(self):
        """Print summary of scraped results."""
        print(f"\n{'='*60}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"Total hotels found: {len(self.all_hotels)}")
        
        # By departure
        by_departure = {}
        for h in self.all_hotels:
            dep = h.get('departure', 'Unknown')
            by_departure[dep] = by_departure.get(dep, 0) + 1
        
        print(f"\nBy departure:")
        for dep, count in by_departure.items():
            print(f"  {dep}: {count} hotels")
        
        # By meal plan
        by_meal = {}
        for h in self.all_hotels:
            meal = h.get('meal_plan', 'Unknown')
            by_meal[meal] = by_meal.get(meal, 0) + 1
        
        print(f"\nBy meal plan:")
        for meal, count in sorted(by_meal.items(), key=lambda x: x[1], reverse=True):
            print(f"  {meal}: {count} hotels")
        
        # By star rating
        by_star = {}
        for h in self.all_hotels:
            star = h.get('star_rating', 'Unknown')
            by_star[star] = by_star.get(star, 0) + 1
        
        print(f"\nBy star rating:")
        for star, count in sorted(by_star.items(), key=lambda x: x[1], reverse=True):
            print(f"  {star}: {count} hotels")
        
        # Price range
        prices = [h['price'] for h in self.all_hotels if h.get('price')]
        if prices:
            print(f"\nPrice range: {min(prices):,.2f} - {max(prices):,.2f} EUR")
            print(f"Average price: {sum(prices)/len(prices):,.2f} EUR")
    
    def print_sample_hotels(self, count=10):
        """Print sample hotels.
        
        Args:
            count: Number of hotels to print
        """
        print(f"\n{'='*60}")
        print(f"SAMPLE HOTELS ({count})")
        print(f"{'='*60}")
        
        for h in self.all_hotels[:count]:
            print(f"\n{h['name']} ({h['star_rating']})")
            print(f"  Meal: {h['meal_plan']}, Room: {h['room_type']}")
            print(f"  Price: {h['price']:.2f} EUR (was {h['original_price']:.2f})")
            print(f"  Departure: {h['departure']}, Date: {h['check_in']}")


def main():
    """Main execution function."""
    scraper = NeckermannTurkeyScraper()
    
    print("Neckermann Nordic Turkey Hotel Scraper")
    print("="*60)
    print("Configuration:")
    print(f"  - Days: 365")
    print(f"  - Nights: 7")
    print(f"  - Departures: {', '.join(scraper.departures.keys())}")
    print(f"  - Meal Plans: All (RO, BB, HB, AI, UAI)")
    print(f"  - Destination: Turkey")
    print("="*60)
    
    # Scrape all hotels
    print("\nStarting scraper...")
    print("This will take approximately 5-10 minutes...")
    
    scraper.all_hotels = scraper.scrape_all_departures(days_range=365)
    
    # Save data
    scraper.save_to_json('turkey_hotels_365days.json')
    scraper.save_to_csv('turkey_hotels_365days.csv')
    
    # Print summary
    scraper.print_summary()
    scraper.print_sample_hotels(10)
    
    print("\n" + "="*60)
    print("Scraping completed!")
    print("="*60)


if __name__ == "__main__":
    main()
