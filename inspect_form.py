import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv('C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/.env')

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    email = os.getenv('CMS_EMAIL') or os.getenv('HAPPYCO_EMAIL')
    password = os.getenv('CMS_PASSWORD') or os.getenv('HAPPYCO_PASSWORD')
    page.goto('https://happyco.asia/admin/login')
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_timeout(3000)
    page.goto('https://happyco.asia/admin/post/create')
    page.wait_for_selector('input[name="title"]')
    
    # Inspect all buttons and forms
    info = page.evaluate('''() => {
        let form = document.querySelector('form');
        let btns = Array.from(document.querySelectorAll('button, input[type="submit"], a.btn')).map(b => ({
            tag: b.tagName,
            type: b.type,
            text: b.innerText,
            classes: b.className,
            onclick: b.getAttribute('onclick')
        }));
        return {
            action: form ? form.action : null,
            method: form ? form.method : null,
            id: form ? form.id : null,
            btns: btns
        };
    }''')
    print('Form info:', info)
    b.close()
