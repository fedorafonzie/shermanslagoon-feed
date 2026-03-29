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

# Stap 2: Zoek naar de afbeeldings-URL met een flexibele regex
print("Zoeken naar de afbeeldings-URL...")

# We zoeken naar de link die begint met featureassets of assets.amuniversal
# De regex [\\\/]* matches mogelijke escaped slashes (zoals \/)
# De link eindigt bij een aanhalingsteken of vraagteken
regex_patroon = r'(https:[\\\/]+(?:featureassets\.gocomics\.com|assets\.amuniversal\.com)[\\\/]assets[\\\/][a-f0-9]+)'

match = re.search(regex_patroon, response.text)

if not match:
    # DEBUG: Als het mislukt, print een klein deel van de broncode om te zien wat er binnenkomt
    print("FOUT: Kon het patroon niet vinden.")
    print("Eerste 500 tekens van broncode ter controle:")
    print(response.text[:500])
    exit(1)

# Verwijder eventuele backslashes uit de gevonden URL
image_url = match.group(1).replace('\\', '')

# Voeg de kwaliteit-parameters toe voor de volledige strip
image_url_full = f"{image_url}?optimizer=image&width=1400&quality=85"

print(f"SUCCES: Afbeelding URL gevonden: {image_url_full}")
image_url = image_url_full # Overschrijf voor gebruik in de feed

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