import requests
import re
import json
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# Instellingen
SHERMANSLAGOON_URL = 'https://www.gocomics.com/shermanslagoon'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Script gestart: Ophalen van Shermans Lagoon via gestructureerde JSON-data.")

try:
    response = requests.get(SHERMANSLAGOON_URL, headers=headers, timeout=15)
    response.raise_for_status()
    html = response.text
except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon pagina niet ophalen. {e}")
    exit(1)

# Stap 2: Zoek de afbeelding in de JSON-LD blokken
image_url = None
json_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)

for block in json_blocks:
    try:
        data = json.loads(block)
        # Zoek specifiek naar het ImageObject van de strip
        if data.get('@type') == 'ImageObject' and 'url' in data:
            # Controleer of het een assets link is (om iconen over te slaan)
            if "assets" in data['url']:
                image_url = data['url']
                break
    except json.JSONDecodeError:
        continue

if not image_url:
    print("FOUT: Geen afbeelding gevonden in de JSON-LD data.")
    exit(1)

# Voeg optimalisatie parameters toe voor de RSS feed
image_url_full = f"{image_url}?optimizer=image&width=1400&quality=85"
print(f"SUCCES: Afbeelding gevonden: {image_url_full}")

# Stap 3: RSS Feed genereren
fg = FeedGenerator()
fg.id(SHERMANSLAGOON_URL)
fg.title('Shermans Lagoon Strip')
fg.link(href=SHERMANSLAGOON_URL, rel='alternate')
fg.description('De dagelijkse Shermans Lagoon strip.')

fe = fg.add_entry()
fe.id(image_url_full)
fe.title(f'Shermans Lagoon - {datetime.now().strftime("%Y-%m-%d")}')
fe.link(href=SHERMANSLAGOON_URL)
fe.description(f'<img src="{image_url_full}" alt="Shermans Lagoon Strip" />')

try:
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print("Bestand 'shermanslagoon.xml' succesvol aangemaakt.")
except Exception as e:
    print(f"FOUT bij wegschrijven: {e}")