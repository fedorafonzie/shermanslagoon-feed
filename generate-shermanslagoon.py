import re
import sys
from playwright.sync_api import sync_playwright
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

URL = 'https://www.gocomics.com/shermanslagoon'

def run():
    with sync_playwright() as p:
        # Start een onzichtbare browser (Chromium)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        print(f"Browser gestart. Laden van {URL}...")
        try:
            # Ga naar de pagina en wacht tot de beveiligings-challenge is verwerkt
            page.goto(URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000) # Extra buffer voor rendering
            
            # Haal de broncode op nadat de browser de JavaScript heeft uitgevoerd
            html = page.content()
            print(f"Pagina geladen. Lengte broncode: {len(html)}")
        except Exception as e:
            print(f"FOUT: Kon pagina niet laden via browser. {e}")
            browser.close()
            sys.exit(1)

        # Zoek specifiek naar de ID achter 'assets/'
        # We gebruiken re.DOTALL omdat Next.js data vaak over meerdere regels verspreid is
        match = re.search(r'assets[\\\/]+([a-f0-9]{32})', html)

        if match:
            asset_id = match.group(1)
            image_url = f"https://featureassets.gocomics.com/assets/{asset_id}?optimizer=image&width=1400&quality=85"
            print(f"SUCCES: Strip gevonden! ID: {asset_id}")
            
            # Feed opbouwen
            fg = FeedGenerator()
            fg.id(URL)
            fg.title('Shermans Lagoon')
            fg.link(href=URL, rel='alternate')
            fg.description('Dagelijkse strip via Playwright')
            
            fe = fg.add_entry()
            fe.id(image_url)
            fe.title(f'Shermans Lagoon - {datetime.now().strftime("%Y-%m-%d")}')
            fe.link(href=URL)
            fe.description(f'<img src="{image_url}" />')
            
            fg.rss_file('shermanslagoon.xml', pretty=True)
            print("RSS feed 'shermanslagoon.xml' succesvol aangemaakt.")
        else:
            print("FOUT: De ID kon niet worden gevonden in de gerenderde broncode.")
            # Sla een screenshot op voor debuggen als het misgaat in de Actions
            page.screenshot(path="error_debug.png")
            browser.close()
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    run()