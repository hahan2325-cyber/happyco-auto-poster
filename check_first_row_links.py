import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv('C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/.env')

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    page.goto('https://happyco.asia/admin/login')
    page.fill("input[name='email']", os.getenv('HAPPYCO_EMAIL'))
    page.fill("input[name='password']", os.getenv('HAPPYCO_PASSWORD'))
    page.click("button[type='submit']")
    page.wait_for_timeout(3000)
    page.goto('https://happyco.asia/admin/post')
    first_row = page.locator('table tbody tr').first
    links = first_row.evaluate('''el => {
        return Array.from(el.querySelectorAll('a')).map(a => a.href);
    }''')
    print('Row links:', links)
    b.close()
