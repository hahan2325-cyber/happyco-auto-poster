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
    
    # Fill title and category
    page.fill('input[name="title"]', 'Test Submission Title')
    page.fill('input[name="slug"]', 'test-submission-title')
    page.select_option('select[name="cat_id"]', '265')
    
    # Listen to console and dialog
    page.on('console', lambda msg: print('PAGE LOG:', msg.text))
    page.on('dialog', lambda dialog: dialog.accept())
    
    # Click save button directly with Playwright locator
    btn = page.locator('button[onclick*="nav_submit_form"]').first
    print('Save btn visible:', btn.is_visible())
    btn.click()
    page.wait_for_timeout(4000)
    print('URL after click:', page.url)
    page.screenshot(path='C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/output/test_save_click.png')
    b.close()
