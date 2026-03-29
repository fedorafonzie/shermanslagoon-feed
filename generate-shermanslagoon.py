import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# --- CONFIGURATIE ---
SHERMANSLAGOON_URL = 'https://www.gocomics.com/shermanslagoon'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

print("Script gestart: Ophalen van de dagelijkse Shermans Lagoon strip.")

# Stap 1: Haal de webpagina op
try:
    response = requests.get(SHERMANSLAGOON_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    html = response.text
    print("SUCCES: Pagina-inhoud opgehaald.")
except Exception as e:
    print(f"FOUT: Kon de pagina niet laden. Fout: {e}")
    exit(1)

# Stap 2: Zoek de specifieke strip-ID via de 'blobName'
# GoComics gebruikt "blobName":"ID" voor de hoofdafbeelding van de strip.
# Dit is de meest betrouwbare manier om ruis (zoals badges/iconen) te filteren.
print("Zoeken naar de juiste strip-afbeelding...")
match = re.search(r'\"blobName\":\"([a-f0-9]{32})\"', html)

if not match:
    # Backup: zoek naar de ID direct in een assets URL
    match = re.search(r'featureassets\.gocomics\.com/assets/([a-f0-9]{32})', html)

if match:
    asset_id = match.group(1)
    # Bouw de volledige URL op met de gewenste kwaliteitsparameters
    image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
    print(f"SUCCES: Strip gevonden met ID: {asset_id}")
else:
    print("FOUT: Geen geldige strip-ID gevonden in de broncode.")
    exit(1)

# Stap 3: Bouw de RSS-feed
fg = FeedGenerator()
fg.id(SHERMANSLAGOON_URL)
fg.title('Sherman\'s Lagoon Strip')
fg.link(href=SHERMANSLAGOON_URL, rel='alternate')
fg.description('De dagelijkse Shermans Lagoon strip via GoComics.')
fg.language('en')

# Gebruik de huidige datum voor de entry
current_date = datetime.now(timezone.utc)
date_str = current_date.strftime("%Y-%m-%d")

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Shermans Lagoon - {date_str}')
fe.link(href=SHERMANSLAGOON_URL)
fe.pubDate(current_date)
# De description bevat de HTML-tag om de afbeelding direct in de RSS-reader te tonen
fe.description(f'<img src="{image_url}" alt="Sherman\'s Lagoon strip van {date_str}" />')

# Stap 4: Schrijf het XML-bestand weg
try:
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print(f"SUCCES: 'shermanslagoon.xml' is aangemaakt met de afbeelding van vandaag.")
    print(f"Gebruikte URL: {image_url}")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)