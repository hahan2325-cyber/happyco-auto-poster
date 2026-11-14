from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    url = "https://happyco.asia/blog/tin-noi-that/thiet-ke-vach-tivi-phong-khach-ket-hop-tu-ruou-canh-kinh-hien-dai-dang-cap-sang-trong-tu-xuong-happyco.html"
    page.goto(url, timeout=30000)
    page.wait_for_load_state("networkidle")
    
    # Scroll down slowly to trigger lazyload
    for y in range(0, 5000, 400):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(300)
        
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    # Check loaded images
    imgs = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.post-content img, article img, .content img')).map(img => ({
            src: img.src,
            dataIsrc: img.getAttribute('data-isrc'),
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            complete: img.complete
        }));
    }''')
    print("Images after scroll:")
    for im in imgs:
        print(" ->", im)
        
    page.screenshot(path=r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\scrolled_page_verified.png", full_page=True)
    print("Full page screenshot saved!")
    browser.close()
