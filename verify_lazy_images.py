from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 1440, "height": 900})
    page.goto('https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-van-mdf.html')
    page.wait_for_load_state("networkidle")
    
    # Scroll smoothly through the page
    for i in range(10):
        page.evaluate(f"window.scrollTo(0, {i * 400})")
        page.wait_for_timeout(400)
        
    page.wait_for_timeout(1500)
    
    # Check Section 3 image
    img_status = page.evaluate('''() => {
        let imgs = Array.from(document.querySelectorAll('.detail-content img'));
        return imgs.map(img => ({
            src: img.src,
            loaded: img.complete,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight
        }));
    }''')
    print("Article images status:", img_status)
    b.close()
