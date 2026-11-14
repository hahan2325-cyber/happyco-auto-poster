from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv("C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/.env")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://happyco.asia/admin/login")
    page.fill('input[name="email"]', os.getenv("HAPPYCO_EMAIL"))
    page.fill('input[name="password"]', os.getenv("HAPPYCO_PASSWORD"))
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    page.goto("https://happyco.asia/admin/media")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    imgs = page.locator("img[src*='19180']").all()
    print("Found media images count:", len(imgs))
    for i, im in enumerate(imgs[:10]):
        print(f"Img {i}: {im.get_attribute('src')}")
    browser.close()
