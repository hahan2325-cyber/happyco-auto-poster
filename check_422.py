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
    
    # Capture response
    def on_response(response):
        if response.status == 422:
            print("422 RESPONSE BODY:", response.text())
            
    page.on("response", on_response)
    
    # Fill title and category
    page.fill('input[name="title"]', 'Test Submission Title')
    page.fill('input[name="slug"]', 'test-submission-title')
    page.select_option('select[name="cat_id"]', '265')
    
    btn = page.locator('button[onclick*="nav_submit_form"]').first
    btn.click()
    page.wait_for_timeout(3000)
    b.close()
