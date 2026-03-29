import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# --- CONFIGURATIE ---
URL = 'https://www.gocomics.com/shermanslagoon'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

print(f"Script gestart: Ophalen van {URL}")

# Stap 1: Haal de broncode op
try:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
    html = response.text
    print("SUCCES: Pagina-inhoud geladen.")
except Exception as e:
    print(f"FOUT: Pagina niet bereikbaar. {e}")
    exit(1)

# Stap 2: Zoek exact de ID die achter de asset-URL staat
# We gebruiken het volledige domein als anker om de juiste 32-cijferige ID te vinden.
match = re.search(r'featureassets\.gocomics\.com/assets/([a-f0-9]{32})', html)

if match:
    asset_id = match.group(1)
    # Bouw de werkende URL zoals jij die in de broncode ziet
    image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
    print(f"SUCCES: De juiste strip-ID gevonden: {asset_id}")
else:
    print("FOUT: De strip-ID kon niet worden gevonden achter het asset-domein.")
    exit(1)

# Stap 3: Bouw de RSS-feed
fg = FeedGenerator()
fg.id(URL)
fg.title('Sherman\'s Lagoon')
fg.link(href=URL, rel='alternate')
fg.description('Dagelijkse strip via GoComics')

current_date = datetime.now(timezone.utc)
date_str = current_date.strftime("%Y-%m-%d")

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Sherman\'s Lagoon - {date_str}')
fe.link(href=URL)
fe.pubDate(current_date)
# Afbeelding in de RSS description plaatsen
fe.description(f'<img src="{image_url}" alt="Sherman\'s Lagoon" />')

# Stap 4: Bestand wegschrijven
try:
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print("SUCCES: 'shermanslagoon.xml' is aangemaakt met de juiste afbeelding.")
    print(f"Gegenereerde link: {image_url}")
except Exception as e:
    print(f"FOUT bij wegschrijven XML: {e}")