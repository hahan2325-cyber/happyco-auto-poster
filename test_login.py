import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv('C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/.env')

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page()
    page.goto('https://happyco.asia/admin/login')
    print('Initial URL:', page.url)
    email = os.getenv('CMS_EMAIL') or os.getenv('HAPPYCO_EMAIL')
    password = os.getenv('CMS_PASSWORD') or os.getenv('HAPPYCO_PASSWORD')
    print('Email:', email)
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_timeout(5000)
    print('After submit URL:', page.url)
    page.screenshot(path='C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/output/login_debug.png')
    b.close()
