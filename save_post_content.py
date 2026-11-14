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
    page.goto("https://happyco.asia/admin/post/2376/edit")
    page.wait_for_load_state("networkidle")
    
    html = page.evaluate('''() => {
        for (let k in window.CKEDITOR.instances) {
            if (document.getElementById(k) && document.getElementById(k).name === 'content') {
                return window.CKEDITOR.instances[k].getData();
            }
        }
        return '';
    }''')
    
    with open(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\post_2376_content.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Saved post 2376 content! Length:", len(html))
    browser.close()
