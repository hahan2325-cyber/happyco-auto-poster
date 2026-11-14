import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\.env")
email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto("https://happyco.asia/admin/login")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.goto("https://happyco.asia/admin/media")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_media_page_screenshot.png")
    print("Media page screenshot saved!")
    
    # Also check post 2376 in frontend again
    page.goto("https://happyco.asia/blog/tin-noi-that/thiet-ke-vach-tivi-phong-khach-ket-hop-tu-ruou-canh-kinh-hien-dai-dang-cap-sang-trong-tu-xuong-happyco.html")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_post_frontend_now.png", full_page=True)
    print("Frontend post screenshot saved!")
    browser.close()
