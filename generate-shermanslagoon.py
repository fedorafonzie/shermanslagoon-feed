import re
import sys
from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = 'https://www.gocomics.com/shermanslagoon'

def run():
    with sync_playwright() as p:
        # We gebruiken Chromium met extra argumenten om minder op een bot te lijken
        browser = p.chromium.launch(headless=True)
        
        # Maak een context aan die een echte Windows-gebruiker simuleert
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
        )
        
        page = context.new_page()
        
        # Verberg de webdriver-vlag (essentieel tegen Bunny Shield)
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"Browser gestart. Navigeren naar {URL}...")
        
        try:
            # We gaan naar de pagina
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
            print("Pagina geladen, wachten tot de beveiligingscheck (Bunny Shield) voorbij is...")
            
            # In plaats van blind te wachten, wachten we tot een specifiek element van de strip verschijnt
            # We zoeken naar de 'Previous' knop die op elke comic pagina staat
            page.wait_for_selector('.ComicNavigation-module-scss-module__6S4TjW__controls', timeout=30000)
            
            # Geef de afbeelding een seconde om in de HTML te springen
            page.wait_for_timeout(2000)
            
            html = page.content()
            print(f"Succesvol voorbij de check! Broncode lengte: {len(html)}")
            
        except Exception as e:
            print(f"FOUT: Beveiligingscheck niet gepasseerd of element niet gevonden. {e}")
            # Maak een screenshot voor inspectie in de GitHub Artifacts
            page.screenshot(path="debug_screenshot.png")
            with open("debug_source.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            sys.exit(1)

        # Zoek de ID in de nu volledig geladen broncode
        match = re.search(r'assets[\\\/]+([a-f0-9]{32})', html)

        if match:
            asset_id = match.group(1)
            image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
            print(f"GEVONDEN: Strip ID is {asset_id}")
            
            # Feed genereren
            fg = FeedGenerator()
            fg.id(URL)
            fg.title('Shermans Lagoon')
            fg.link(href=URL, rel='alternate')
            fg.description('Dagelijkse strip via Playwright Stealth')
            
            fe = fg.add_entry()
            fe.id(image_url)
            fe.title(f'Shermans Lagoon - {datetime.now().strftime("%Y-%m-%d")}')
            fe.link(href=URL)
            fe.description(f'<img src="{image_url}" />')
            
            fg.rss_file('shermanslagoon.xml', pretty=True)
            print("RSS feed succesvol opgeslagen.")
        else:
            print("FOUT: Pagina geladen, maar geen asset ID gevonden in de HTML.")
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    run()