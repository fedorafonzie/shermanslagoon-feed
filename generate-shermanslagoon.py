import requests
import re
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

print("Script gestart: Ophalen van de dagelijkse Shermans Lagoon strip via Regular Expression.")

# URL van de Shermans Lagoon pagina
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

# Stap 2: Zoek met een regular expression naar de afbeeldings-URL
print("Zoeken naar de afbeeldings-URL met een regular expression...")

# --- CORRECTIE gebaseerd op uw voorstel ---
# Het patroon zoekt naar de volledige URL die begint met de basis
# en gevolgd wordt door een reeks van hexadecimale karakters (a-f, 0-9).
match = re.search(r'(https://featureassets.gocomics.com/assets/[a-f0-9]+)', response.text)

if not match:
    print("FOUT: Kon het URL-patroon niet vinden in de broncode van de pagina.")
    exit(1)

# match.group(1) bevat de volledige, schone URL die we hebben gevonden.
image_url = match.group(1)
print(f"SUCCES: Afbeelding URL gevonden via Regular Expression: {image_url}")
# --- EINDE CORRECTIE ---
    
# Stap 3: Bouw de RSS-feed
fg = FeedGenerator()
fg.id(SHERMANSLAGOON_URL)
fg.title('Shermans Lagoon Strip')
fg.link(href=SHERMANSLAGOON_URL, rel='alternate')
fg.description('De dagelijkse Shermans Lagoon strip.')
fg.language('en')

current_date = datetime.now(timezone.utc)
current_date_str = current_date.strftime("%Y-%m-%d")

fe = fg.add_entry()
fe.id(image_url)
fe.title(f'Shermans Lagoon - {current_date_str}')
fe.link(href=SHERMANSLAGOON_URL)
fe.pubDate(current_date)
fe.description(f'<img src="{image_url}" alt="Shermans Lagoon Strip voor {current_date_str}" />')

# Stap 4: Schrijf het XML-bestand weg
try:
    fg.rss_file('shermanslagoon.xml', pretty=True)
    print("SUCCES: 'shermanslagoon.xml' is aangemaakt met de strip van vandaag.")
except Exception as e:
    print(f"FOUT: Kon het bestand niet wegschrijven. Foutmelding: {e}")
    exit(1)