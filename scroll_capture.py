from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 1440, "height": 900})
    page.goto('https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-van-mdf.html')
    page.wait_for_load_state("networkidle")
    
    # Scroll slowly and steadily
    total_height = page.evaluate("document.body.scrollHeight")
    current_pos = 0
    step = 500
    while current_pos < total_height:
        current_pos += step
        page.evaluate(f"window.scrollTo(0, {current_pos})")
        page.wait_for_timeout(600)
        
    page.wait_for_timeout(2000)
    
    out_shot = 'C:/Users/CHAU/.gemini/antigravity/scratch/happyco-cloud-poster/output/b2b_verified_full_live.png'
    page.screenshot(path=out_shot, full_page=True)
    print("Full verified screenshot saved to:", out_shot)
    b.close()
