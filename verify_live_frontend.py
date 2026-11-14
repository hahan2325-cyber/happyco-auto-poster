from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1200})
    
    url = "https://happyco.asia/blog/thiet-ke-vach-tivi-phong-khach-ket-hop-tu-ruou-canh-kinh-hien-dai-dang-cap-sang-trong-tu-xuong-happyco-1794283976.html"
    print("Navigating to:", url)
    res = page.goto(url, timeout=30000)
    print("Status code:", res.status if res else "None")
    page.wait_for_load_state("networkidle")
    
    # Check all images on page
    imgs = page.evaluate('''() => {
        return Array.from(document.querySelectorAll("img")).map(img => ({
            src: img.src,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            complete: img.complete
        })).filter(x => x.src.includes('19180'));
    }''')
    print(f"Total CDN images on page: {len(imgs)}")
    for im in imgs:
        print(" ->", im)
        
    page.screenshot(path=r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\live_post_frontend_verified.png", full_page=True)
    print("Screenshot saved to live_post_frontend_verified.png")
    browser.close()
