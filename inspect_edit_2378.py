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
    page.goto('https://happyco.asia/admin/post/2378/edit')
    page.wait_for_selector('input[name="title"]')
    
    val = page.evaluate('''() => {
        let contentEl = document.querySelector('textarea[name="content"]');
        let descEl = document.querySelector('textarea[name="description"]');
        let ckeContent = null;
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let k in window.CKEDITOR.instances) {
                let el = document.getElementById(k);
                if (el && el.name === 'content') ckeContent = window.CKEDITOR.instances[k].getData();
            }
        }
        return {
            contentElLen: contentEl ? contentEl.value.length : 0,
            ckeContentLen: ckeContent ? ckeContent.length : 0,
            ckePreview: ckeContent ? ckeContent.slice(0, 300) : null
        };
    }''')
    print('Content in edit page:', val)
    b.close()
