from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 1440, "height": 2200})
    page.goto('https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-van-mdf.html')
    page.wait_for_load_state("networkidle")
    # Scroll down to trigger lazy loading
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    page.wait_for_timeout(2000)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)
    
    screenshot_path = 'C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/output/live_post_2378_b2b_full.png'
    page.screenshot(path=screenshot_path, full_page=True)
    print("Screenshot saved to:", screenshot_path)
    b.close()
