"""
Neckermann Nordic Flow 1 - Hotel List Extractor
Extracts unique hotel list with meal plans, departure airports, and URLs
No prices, just hotel catalog information
"""

import requests
import json
import csv
import os
from datetime import datetime, timedelta
import time


class NeckermannFlow1Extractor:
    """Flow 1: Extract unique hotel list with meal plans and departure airports."""
    
    def __init__(self):
        self.base_url = "https://neckermann-nordic.dk"
        self.api_url = "https://neckermann-nordic.dk/api/search"
        
        # Departure airports
        self.departures = {
            'AAL': '1962',  # Aalborg
            'CPH': '1941',  # Copenhagen
            'BLL': '1964'   # Billund
        }
        
        # Turkey state code
        self.turkey_state = '9'
        
        # Headers from browser
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
        
        # Unique hotels storage
        self.hotels = {}  # Key: hotel_inc, Value: hotel info
    
    def build_params(self, departure_code, checkin_date, price_page=1):
        """Build API parameters for hotel list extraction."""
        return {
            'CHARTER': 'True',
            'ADULT': '2',
            'CHECKIN_BEG': checkin_date,
            'CHECKIN_END': checkin_date,
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
    
    def fetch_page(self, departure_code, checkin_date, price_page=1, proxy=None):
        """Fetch a page of results from API.
        
        Args:
            departure_code: Airport code (AAL, CPH, BLL)
            checkin_date: Check-in date (YYYYMMDD)
            price_page: Page number
            proxy: Proxy URL (e.g., 'http://user:pass@proxy:port')
        """
        params = self.build_params(departure_code, checkin_date, price_page)
        
        proxies = None
        if proxy:
            proxies = {
                'http': proxy,
                'https': proxy
            }
        
        try:
            resp = requests.get(
                self.api_url, 
                params=params, 
                headers=self.headers, 
                proxies=proxies,
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def build_hotel_url(self, hotel_name, hotel_inc):
        """Build hotel detail URL."""
        # Convert hotel name to slug
        slug = hotel_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        slug = slug.strip('-')
        
        return f"{self.base_url}/tours/turkey/{slug}"
    
    def extract_hotel_info(self, price_data, departure_code):
        """Extract unique hotel information."""
        hotel_inc = price_data.get('hotelInc', '')
        hotel_name = price_data.get('hotelName', '')
        
        if not hotel_inc or not hotel_name:
            return None
        
        # Build URL
        hotel_url = self.build_hotel_url(hotel_name, hotel_inc)
        
        return {
            'hotel_inc': hotel_inc,
            'name': hotel_name,
            'name_local': price_data.get('hotelLName', ''),
            'star_rating': price_data.get('starName', ''),
            'star_inc': price_data.get('starInc', ''),
            'town_inc': price_data.get('townInc', ''),
            'meal_plan': price_data.get('mealName', ''),
            'meal_plan_local': price_data.get('mealLName', ''),
            'room_type': price_data.get('roomName', ''),
            'departure': departure_code,
            'url': hotel_url,
            'scraped_at': datetime.now().isoformat()
        }
    
    def extract_all_hotels(self, days_range=90, proxy=None):
        """Extract all unique hotels across multiple dates.
        
        Args:
            days_range: Number of days to check (default 90)
            proxy: Proxy URL (e.g., 'http://user:pass@proxy:port')
        """
        print("Flow 1: Extracting hotel list across multiple dates")
        print("="*60)
        print(f"Date range: {days_range} days")
        if proxy:
            print(f"Proxy: {proxy}")
        print("="*60)
        
        today = datetime.now()
        
        for dep_code in self.departures.keys():
            print(f"\nProcessing departure: {dep_code}")
            
            # Loop through dates (every 7 days)
            for day_offset in range(0, days_range, 7):
                checkin_date = today + timedelta(days=day_offset)
                checkin_str = checkin_date.strftime('%Y%m%d')
                
                print(f"\n  Date: {checkin_date.strftime('%Y-%m-%d')} (offset: {day_offset})")
                
                page = 1
                max_pages = 50  # Increased max pages
                consecutive_empty = 0
                
                while page <= max_pages and consecutive_empty < 3:
                    print(f"    Fetching page {page}...")
                    
                    data = self.fetch_page(dep_code, checkin_str, page, proxy)
                    
                    if not data or not isinstance(data, list) or len(data) == 0:
                        print(f"      No data returned, stopping")
                        break
                    
                    item = data[0]
                    
                    if 'prices' not in item or not item['prices']:
                        print(f"      No prices in response, stopping")
                        consecutive_empty += 1
                        if consecutive_empty >= 3:
                            print(f"      3 consecutive empty pages, stopping")
                            break
                        page += 1
                        continue
                    
                    consecutive_empty = 0
                    prices = item['prices']
                    print(f"      Found {len(prices)} hotels on page {page}")
                    
                    for price_data in prices:
                        hotel_info = self.extract_hotel_info(price_data, dep_code)
                        
                        if hotel_info:
                            hotel_inc = hotel_info['hotel_inc']
                            
                            # If hotel already exists, add departure and meal plan
                            if hotel_inc in self.hotels:
                                # Add departure if not already present
                                if dep_code not in self.hotels[hotel_inc]['departures']:
                                    self.hotels[hotel_inc]['departures'].append(dep_code)
                                
                                # Add meal plan if not already present
                                meal_plan = hotel_info['meal_plan']
                                if meal_plan and meal_plan not in self.hotels[hotel_inc]['meal_plans']:
                                    self.hotels[hotel_inc]['meal_plans'].append(meal_plan)
                                
                                # Add room type if not already present
                                room_type = hotel_info['room_type']
                                if room_type and room_type not in self.hotels[hotel_inc]['room_types']:
                                    self.hotels[hotel_inc]['room_types'].append(room_type)
                            else:
                                # New hotel
                                self.hotels[hotel_inc] = {
                                    'hotel_inc': hotel_inc,
                                    'name': hotel_info['name'],
                                    'name_local': hotel_info['name_local'],
                                    'star_rating': hotel_info['star_rating'],
                                    'star_inc': hotel_info['star_inc'],
                                    'town_inc': hotel_info['town_inc'],
                                    'departures': [dep_code],
                                    'meal_plans': [hotel_info['meal_plan']] if hotel_info['meal_plan'] else [],
                                    'room_types': [hotel_info['room_type']] if hotel_info['room_type'] else [],
                                    'url': hotel_info['url'],
                                    'scraped_at': hotel_info['scraped_at']
                                }
                    
                    page += 1
                    time.sleep(0.5)  # Rate limiting
                
                time.sleep(1)  # Rate limiting between dates
            
            print(f"  Total unique hotels so far: {len(self.hotels)}")
        
        return self.hotels
    
    def save_to_json(self, filename="flow1_hotel_list.json"):
        """Save hotel list to JSON."""
        os.makedirs('data', exist_ok=True)
        filepath = f'data/{filename}'
        
        # Convert dict to list
        hotel_list = list(self.hotels.values())
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'hotels': hotel_list,
                'total': len(hotel_list),
                'scraped_at': datetime.now().isoformat(),
                'parameters': {
                    'departures': list(self.departures.keys()),
                    'destination': 'Turkey',
                    'flow': 'Flow 1 - Hotel List Only'
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved {len(hotel_list)} unique hotels to {filepath}")
    
    def save_to_csv(self, filename="flow1_hotel_list.csv"):
        """Save hotel list to CSV."""
        os.makedirs('data', exist_ok=True)
        filepath = f'data/{filename}'
        
        if not self.hotels:
            print("No hotel data to save")
            return
        
        # Convert dict to list and flatten for CSV
        hotel_list = []
        for hotel in self.hotels.values():
            hotel_list.append({
                'hotel_inc': hotel['hotel_inc'],
                'name': hotel['name'],
                'name_local': hotel['name_local'],
                'star_rating': hotel['star_rating'],
                'star_inc': hotel['star_inc'],
                'town_inc': hotel['town_inc'],
                'departures': ', '.join(hotel['departures']),
                'meal_plans': ', '.join(hotel['meal_plans']),
                'room_types': ', '.join(hotel['room_types']),
                'url': hotel['url'],
                'scraped_at': hotel['scraped_at']
            })
        
        keys = hotel_list[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(hotel_list)
        
        print(f"Saved CSV to {filepath}")
    
    def print_summary(self):
        """Print summary of extracted hotels."""
        print(f"\n{'='*60}")
        print(f"FLOW 1 - HOTEL LIST SUMMARY")
        print(f"{'='*60}")
        print(f"Total unique hotels: {len(self.hotels)}")
        
        # Count by star rating
        by_star = {}
        for hotel in self.hotels.values():
            star = hotel.get('star_rating', 'Unknown')
            by_star[star] = by_star.get(star, 0) + 1
        
        print(f"\nBy star rating:")
        for star, count in sorted(by_star.items(), key=lambda x: x[1], reverse=True):
            print(f"  {star}: {count} hotels")
        
        # Count by departure
        by_departure = {}
        for hotel in self.hotels.values():
            for dep in hotel.get('departures', []):
                by_departure[dep] = by_departure.get(dep, 0) + 1
        
        print(f"\nBy departure airport:")
        for dep, count in sorted(by_departure.items(), key=lambda x: x[1], reverse=True):
            print(f"  {dep}: {count} hotels")
        
        # Count by meal plan
        by_meal = {}
        for hotel in self.hotels.values():
            for meal in hotel.get('meal_plans', []):
                by_meal[meal] = by_meal.get(meal, 0) + 1
        
        print(f"\nBy meal plan:")
        for meal, count in sorted(by_meal.items(), key=lambda x: x[1], reverse=True):
            print(f"  {meal}: {count} hotels")
    
    def print_sample_hotels(self, count=10):
        """Print sample hotels."""
        print(f"\n{'='*60}")
        print(f"SAMPLE HOTELS ({count})")
        print(f"{'='*60}")
        
        for i, hotel in enumerate(list(self.hotels.values())[:count]):
            print(f"\n{i+1}. {hotel['name']} ({hotel['star_rating']})")
            print(f"   Hotel INC: {hotel['hotel_inc']}")
            print(f"   Departures: {', '.join(hotel['departures'])}")
            print(f"   Meal Plans: {', '.join(hotel['meal_plans'])}")
            print(f"   Room Types: {', '.join(hotel['room_types'])}")
            print(f"   URL: {hotel['url']}")


def main():
    """Main execution function."""
    extractor = NeckermannFlow1Extractor()
    
    print("="*60)
    print("Neckermann Nordic - Flow 1: Hotel List Extractor")
    print("="*60)
    print("Extracting: Hotel list, meal plans, departure airports, URLs")
    print("No prices - just hotel catalog information")
    print("="*60)
    
    # Get proxy from environment variable or use None
    proxy = os.environ.get('PROXY_URL', None)
    if proxy:
        print(f"Using proxy: {proxy}")
    else:
        print("No proxy configured (set PROXY_URL environment variable)")
    
    # Extract all hotels (90 days range)
    extractor.extract_all_hotels(days_range=90, proxy=proxy)
    
    # Save data
    extractor.save_to_json()
    extractor.save_to_csv()
    
    # Print summary
    extractor.print_summary()
    extractor.print_sample_hotels(10)
    
    print("\n" + "="*60)
    print("Flow 1 extraction completed!")
    print("="*60)


if __name__ == "__main__":
    main()
