import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = 'https://www.gocomics.com/shermanslagoon'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

print(f"Script gestart: Ophalen van {URL}")

try:
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    html = response.text
    print(f"SUCCES: Pagina opgehaald. Status code: {response.status_code}")
except Exception as e:
    print(f"FOUT: Pagina onbereikbaar. {e}")
    exit(1)

# We zoeken naar de unieke 32-cijferige code van de afbeelding.
# In de broncode staat dit vaak als: "blobName":"9a170560..." of in een URL.
# We zoeken naar de reeks van 32 hexadecimale tekens.
id_match = re.search(r'[a-f0-9]{32}', html)

if id_match:
    asset_id = id_match.group(0)
    image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
    print(f"SUCCES: Afbeelding ID gevonden: {asset_id}")
    print(f"Volledige URL: {image_url}")
else:
    print("FOUT: Geen strip-ID gevonden in de broncode.")
    # DEBUG: Laat zien wat de server naar GitHub stuurt (eerste 1000 tekens)
    print("--- BEGIN BRONCODE FRAGMENT ---")
    print(html[:1000]) 
    print("--- EINDE BRONCODE FRAGMENT ---")
    exit(1)

# RSS Feed opbouwen
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
    print("Bestand 'shermanslagoon.xml' is bijgewerkt.")
except Exception as e:
    print(f"Fout bij opslaan: {e}")