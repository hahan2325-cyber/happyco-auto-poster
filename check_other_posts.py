import os
import re
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
        return Array.from(document.querySelectorAll('.table tbody tr')).slice(1, 8).map(r => {
            let editA = r.querySelector('a[href*="/edit"]');
            return editA ? editA.href : null;
        });
    }''')
    print("Recent post edit URLs:", rows)
    
    for edit_url in rows:
        if not edit_url: continue
        page.goto(edit_url)
        page.wait_for_load_state("networkidle")
        data = page.evaluate('''() => {
            let title = document.querySelector('input[name="title"]') ? document.querySelector('input[name="title"]').value : '';
            let content = '';
            for (let k in window.CKEDITOR.instances) {
                if (document.getElementById(k) && document.getElementById(k).name === 'content') {
                    content = window.CKEDITOR.instances[k].getData();
                }
            }
            return { title, content };
        }''')
        imgs = re.findall(r'<img[^>]+>', data['content'])
        if imgs:
            print(f"\nPost: {data['title']} ({edit_url})")
            for im in imgs:
                print(" ->", im)
            break
            
    browser.close()
