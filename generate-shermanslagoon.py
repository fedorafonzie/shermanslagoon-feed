import re
import sys
import time
from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# We bepalen de datum van vandaag voor de directe URL
vandaag = datetime.now().strftime("%Y/%m/%d")
URL = f'https://www.gocomics.com/shermanslagoon/{vandaag}'

def run():
    with sync_playwright() as p:
        print(f"Browser opstarten (iPhone emulatie) voor: {URL}")
        # We simuleren een iPhone 13 om minder op een server-bot te lijken
        device = p.devices['iPhone 13']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**device)
        page = context.new_page()

        try:
            # Stap 1: Ga naar de pagina
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
            print("Pagina geladen. Wachten op het oplossen van de beveiligingspuzzel...")
            
            # Stap 2: We wachten tot de paginatitel verandert van "Establishing connection" naar de echte titel
            # We proberen dit max 60 seconden lang
            found_id = None
            for i in range(12): # 12 keer 5 seconden = 60 seconden
                html = page.content()
                # We zoeken direct naar de 32-cijferige ID in de broncode
                # We zoeken specifiek naar de versie die in een asset-URL staat
                match = re.search(r'assets[\\\/]+([a-f0-9]{32})', html)
                
                if match:
                    found_id = match.group(1)
                    print(f"SUCCES! Strip-ID gevonden na {i*5} seconden: {found_id}")
                    break
                
                print(f"Poging {i+1}: Nog geen ID... (Titel: {page.title()})")
                page.wait_for_timeout(5000)

            if not found_id:
                print("FOUT: Timeout bereikt. De beveiligingscheck werd niet gepasseerd.")
                page.screenshot(path="debug_screenshot.png")
                with open("debug_source.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                sys.exit(1)

            # Stap 3: De URL samenstellen
            image_url = f"https://featureassets.gocomics.com/assets/{found_id}?optimizer=image&width=1400&quality=85"

            # Stap 4: Feed maken
            fg = FeedGenerator()
            fg.id(URL)
            fg.title('Shermans Lagoon')
            fg.link(href=URL, rel='alternate')
            fg.description('Dagelijkse strip via Playwright (Bypass mode)')
            
            fe = fg.add_entry()
            fe.id(image_url)
            fe.title(f'Shermans Lagoon - {datetime.now().strftime("%Y-%m-%d")}')
            fe.link(href=URL)
            fe.description(f'<img src="{image_url}" />')
            
            fg.rss_file('shermanslagoon.xml', pretty=True)
            print("RSS feed 'shermanslagoon.xml' is succesvol aangemaakt.")

        except Exception as e:
            print(f"Onverwachte fout: {e}")
            page.screenshot(path="debug_screenshot.png")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    run()