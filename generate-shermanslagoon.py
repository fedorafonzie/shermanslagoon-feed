import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# --- CONFIGURATIE ---
URL = 'https://www.gocomics.com/shermanslagoon'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
}

print(f"Script gestart voor {URL}")

# Stap 1: Pagina ophalen
try:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
    html = response.text
    print("SUCCES: Pagina-inhoud opgehaald.")
except Exception as e:
    print(f"FOUT: Pagina niet bereikbaar. {e}")
    exit(1)

# Stap 2: De juiste ID vinden
# We zoeken specifiek naar de ID die in het 'comic' object staat of bij 'blobName'
# Dit patroon negeert slashes en backslashes voor maximale compatibiliteit
asset_id = None

# Methode A: Zoeken in het comic-data object (meest specifiek)
match = re.search(r'\"comic\":{.*?\"url\":\".*?assets[\\\/]+([a-f0-9]{32})\"', html)

if not match:
    # Methode B: Fallback naar blobName
    match = re.search(r'\"blobName\":\"([a-f0-9]{32})\"', html)

if match:
    asset_id = match.group(1)
    print(f"SUCCES: Strip ID gevonden: {asset_id}")
else:
    print("FOUT: Geen strip-ID gevonden in de broncode.")
    # Debug: Toon een klein deel van de broncode om te zien wat er binnenkomt
    print("Broncode fragment:", html[500:1500])
    exit(1)

# De URL samenstellen
image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"

# Stap 3: De RSS-feed opbouwen
try:
    fg = FeedGenerator()
    fg.id(URL)
    fg.title('Shermans Lagoon')
    fg.link(href=URL, rel='alternate')
    fg.description('Dagelijkse strip via GoComics')
    fg.language('en')

    current_date = datetime.now(timezone.utc)
    date_str = current_date.strftime("%Y-%m-%d")

    fe = fg.add_entry()
    fe.id(image_url)
    fe.title(f'Shermans Lagoon - {date_str}')
    fe.link(href=URL)
    fe.pubDate(current_date)
    fe.description(f'<img src="{image_url}" alt="Sherman\'s Lagoon strip" />')

    # Stap 4: Bestand wegschrijven
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print(f"SUCCES: 'shermanslagoon.xml' is aangemaakt.")
    print(f"Gebruikte link: {image_url}")
except Exception as e:
    print(f"FOUT bij opbouw van XML: {e}")
    exit(1)