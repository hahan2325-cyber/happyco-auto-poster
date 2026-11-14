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
    
    # Check post 2375 (the one before 2376)
    page.goto("https://happyco.asia/admin/post/2375/edit")
    page.wait_for_load_state("networkidle")
    
    html = page.evaluate('''() => {
        for (let k in window.CKEDITOR.instances) {
            if (document.getElementById(k) && document.getElementById(k).name === 'content') {
                return window.CKEDITOR.instances[k].getData();
            }
        }
        return '';
    }''')
    
    print("Post 2375 content:")
    import re
    imgs = re.findall(r'<img[^>]+>', html)
    for im in imgs:
        print(" ->", im)
        
    browser.close()
