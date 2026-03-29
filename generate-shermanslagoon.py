import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

print("Script gestart: Ophalen van de dagelijkse Shermans lagoon strip via Regular Expression.")

# URL van de Shermans lagoon comic pagina
SHERMANSLAGOON_URL = 'https://www.gocomics.com/shermanslagoon'

# Stap 1: Haal de webpagina op
try:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(SHERMANSLAGOON_URL, headers=headers)
    response.raise_for_status()
    print("SUCCES: GoComics pagina HTML opgehaald.")
except requests.exceptions.RequestException as e:
    print(f"FOUT: Kon GoComics pagina niet ophalen. Fout: {e}")
    exit(1)

# Stap 2: Zoek met een verbeterde regular expression naar de afbeeldings-URL
print("Zoeken naar de afbeeldings-URL...")

# GoComics gebruikt tegenwoordig vaak assets.amuniversal.com
# We zoeken specifiek naar de meta-tag 'og:image' voor de meest betrouwbare link
match = re.search(r'property="og:image" content="(https://assets\.amuniversal\.com/[a-f0-9]+)"', response.text)

if not match:
    # Backup: zoek naar de URL zonder de meta-tag context
    match = re.search(r'(https://assets\.amuniversal\.com/[a-f0-9]+)', response.text)

if not match:
    print("FOUT: Kon het assets.amuniversal.com patroon niet vinden.")
    exit(1)

image_url = match.group(1)
print(f"SUCCES: Afbeelding URL gevonden: {image_url}")
    
# Stap 3: Bouw de RSS-feed
fg = FeedGenerator()
fg.id(SHERMANSLAGOON_URL)
fg.title('Shermans lagoon  Comic Strip')
fg.link(href=SHERMANSLAGOON_URL, rel='alternate')
fg.description('De dagelijkse Shermans lagoon strip.')
fg.language('en')

current_date = datetime.now(timezone.utc)
current_date_str = current_date.strftime("%Y-%m-%d")

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Shermans lagoon - {current_date_str}')
fe.link(href=SHERMANSLAGOON_URL)
fe.pubDate(current_date)
fe.description(f'<img src="{image_url}" alt="Shermans lagoon Strip voor {current_date_str}" />')

# Stap 4: Schrijf het XML-bestand weg
try:
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print("SUCCES: 'shermanslagoon.xml' is aangemaakt met de strip van vandaag.")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)