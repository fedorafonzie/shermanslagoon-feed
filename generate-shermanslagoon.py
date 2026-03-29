import requests
import re
import sys
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# We doen ons voor als Googlebot om de Bunny Shield wachtpagina te omzeilen
URL = 'https://www.gocomics.com/shermanslagoon'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

print(f"--- START SCRAPE (Googlebot emulatie) ---")

try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    html = response.text
    print(f"Status: {response.status_code}")
    print(f"Paginatitel: {re.search(r'<title>(.*?)</title>', html).group(1) if re.search(r'<title>(.*?)</title>', html) else 'Geen titel'}")
    
    if "Establishing a secure connection" in html:
        print("FOUT: Nog steeds geblokkeerd door Bunny Shield. Googlebot methode werkt hier niet.")
        sys.exit(1)
        
except Exception as e:
    print(f"FOUT: Verbinding mislukt. {e}")
    sys.exit(1)

# Zoek de ID. We kijken naar de ID die in de 'comic' data of 'assets' URL staat.
# We zoeken specifiek naar de 32-tekens ID die bij de strip hoort.
# We negeren de Sentry-trace door te controleren of 'assets' in de buurt staat.
match = re.search(r'assets[\\\/]+([a-f0-9]{32})', html)

if match:
    asset_id = match.group(1)
    image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
    print(f"GEVONDEN ID: {asset_id}")
    print(f"URL: {image_url}")
else:
    print("FOUT: Geen strip-ID gevonden in de broncode.")
    # Toon de eerste 500 tekens om te zien waar we zijn beland
    print("Broncode preview:", html[:500])
    sys.exit(1)

# RSS opbouw
fg = FeedGenerator()
fg.id(URL)
fg.title('Shermans Lagoon')
fg.link(href=URL, rel='alternate')
fg.description('Dagelijkse strip')

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Shermans Lagoon - {datetime.now().strftime("%Y-%m-%d")}')
fe.link(href=URL)
fe.description(f'<img src="{image_url}" />')

fg.rss_file('shermanslagoon.xml', pretty=True)
print("KLAAR: XML bestand is aangemaakt.")