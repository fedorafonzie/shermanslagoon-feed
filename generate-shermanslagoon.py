import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# Configuratie
URL = 'https://www.gocomics.com/shermanslagoon'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Script gestart: Ophalen van {URL}")

try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    source_code = response.text
    print("SUCCES: Pagina opgehaald.")
except Exception as e:
    print(f"FOUT: Kon pagina niet ophalen. {e}")
    exit(1)

# STAP 2: Zoek de unieke asset ID
# We zoeken naar de link die eindigt op een 32-tekens lange ID (0-9 en a-f)
# Dit patroon negeert eventuele backslashes die in de broncode kunnen staan.
match = re.search(r'https?://featureassets\.gocomics\.com/assets/([a-f0-9]{32})', source_code)

if not match:
    # Backup: Zoek naar het amuniversal domein als featureassets ontbreekt
    match = re.search(r'https?://assets\.amuniversal\.com/([a-f0-9]{32})', source_code)

if not match:
    print("FOUT: Kon geen strip-URL vinden in de broncode.")
    # Optioneel: print een deel van de code om te zien wat er misgaat
    exit(1)

# ID uit de match halen en de schone URL opbouwen
asset_id = match.group(1)
image_url = f"https://featureassets.gocomics.com/assets/{asset_id}"
# Voeg optimalisatie parameters toe voor de RSS reader
image_url_full = f"{image_url}?optimizer=image&width=1400&quality=85"

print(f"SUCCES: Strip gevonden met ID: {asset_id}")
print(f"URL: {image_url_full}")

# STAP 3: Bouw de RSS-feed
fg = FeedGenerator()
fg.id(URL)
fg.title('Sherman\'s Lagoon Daily')
fg.link(href=URL, rel='alternate')
fg.description('Dagelijkse strip van Sherman\'s Lagoon')
fg.language('en')

current_date = datetime.now(timezone.utc)
fe = fg.add_entry()
fe.id(image_url_full)
fe.title(f'Sherman\'s Lagoon - {current_date.strftime("%Y-%m-%d")}')
fe.link(href=URL)
fe.pubDate(current_date)
fe.description(f'<img src="{image_url_full}" alt="Sherman\'s Lagoon" />')

try:
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print("SUCCES: 'shermanslagoon.xml' is aangemaakt.")
except Exception as e:
    print(f"FOUT: Kon bestand niet wegschrijven: {e}")
    exit(1)
    