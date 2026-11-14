import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\.env")
email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://happyco.asia/admin/login")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.goto("https://happyco.asia/admin/post")
    page.wait_for_load_state("networkidle")
    rows = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.table tbody tr')).slice(0, 8).map(r => {
            let tds = Array.from(r.querySelectorAll('td')).map(td => td.innerText.trim());
            return tds;
        });
    }''')
    for r in rows:
        print(r)
    browser.close()
