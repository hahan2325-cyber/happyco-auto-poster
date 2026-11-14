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
    page.goto('https://happyco.asia/admin/post/create')
    inputs = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('input, textarea, select')).map(i => ({
            name: i.name,
            id: i.id,
            type: i.type,
            required: i.required
        }));
    }''')
    for inp in inputs:
        if inp['name']:
            print(inp)
    b.close()
