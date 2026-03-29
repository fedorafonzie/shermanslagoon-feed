import requests
import re
import sys
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = 'https://www.gocomics.com/shermanslagoon'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

print(f"--- START DIAGNOSE ---")
print(f"URL: {URL}")

try:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
    html = response.text
    print(f"SUCCES: Pagina opgehaald (Lengte: {len(html)} tekens)")
except Exception as e:
    print(f"FOUT: Pagina onbereikbaar. {e}")
    sys.exit(1)

# we zoeken naar 'assets', gevolgd door eventuele (back)slashes, en dan de 32-cijferige ID
# Patroon: assets + een of meer slashes/backslashes + 32 hex karakters
regex_patroon = r'assets[\\\/]+([a-f0-9]{32})'
print(f"Zoeken met patroon: {regex_patroon}")

match = re.search(regex_patroon, html)

if match:
    asset_id = match.group(1)
    image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
    print(f"GEVONDEN ID: {asset_id}")
    print(f"GEGENEREERDE URL: {image_url}")
else:
    print("FOUT: De ID '9a170560...' is niet gevonden in de buurt van de map 'assets'.")
    
    # We printen nu een relevant deel van de broncode voor jou om te inspecteren
    # We zoeken waar de tekst 'blobName' of 'comic' staat, want daar zit de ID meestal
    print("\n--- INSPECTIE VAN BRONCODE (Zoek hier zelf naar de ID) ---")
    start_index = html.find('__NEXT_DATA__') # Dit is waar GoComics alle data verstopt
    if start_index == -1:
        start_index = 0
    print(html[start_index:start_index + 5000]) # Print 5000 tekens vanaf het datablok
    print("\n--- EINDE BRONCODE ---")
    sys.exit(1)

# RSS Feed opbouw (alleen als ID gevonden is)
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

try:
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print("Bestand 'shermanslagoon.xml' is succesvol bijgewerkt.")
except Exception as e:
    print(f"Fout bij opslaan XML: {e}")