import requests
import re
import json
from bs4 import BeautifulSoup

url = 'https://neckermann-nordic.dk/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7',
}

resp = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')
scripts = soup.find_all('script')

for i, s in enumerate(scripts):
    if s.string and 'initialData' in s.string and 'Ekavi Apartments' in s.string:
        text = s.string
        idx = text.find('"initialData":')
        if idx > 0:
            start = idx + len('"initialData":')
            bracket_count = 0
            in_string = False
            escape_next = False
            end = start
            
            for j in range(start, len(text)):
                ch = text[j]
                if escape_next:
                    escape_next = False
                    continue
                if ch == '\\':
                    escape_next = True
                    continue
                if ch == '"' and not escape_next:
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
            
            json_str = text[start:end]
            print(f'Extracted JSON length: {len(json_str)}')
            try:
                data = json.loads(json_str)
                print(f'Parsed {len(data)} hotels')
                for h in data[:2]:
                    print(json.dumps(h, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f'Error: {e}')
                print(f'First 500 chars: {json_str[:500]}')
        break
