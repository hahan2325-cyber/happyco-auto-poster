from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    failed_requests = []
    page.on("requestfailed", lambda req: failed_requests.append({
        "url": req.url,
        "failure": req.failure
    }))
    
    responses = []
    page.on("response", lambda res: responses.append({
        "url": res.url,
        "status": res.status
    }) if "19180" in res.url or "flow" in res.url else None)
    
    page.goto("https://happyco.asia/blog/tin-noi-that/thiet-ke-vach-tivi-phong-khach-ket-hop-tu-ruou-canh-kinh-hien-dai-dang-cap-sang-trong-tu-xuong-happyco.html", timeout=30000)
    page.wait_for_load_state("networkidle")
    
    print("Failed requests:")
    for f in failed_requests:
        print(" -", f)
        
    print("\nImage responses:")
    for r in responses:
        print(" -", r)
        
    # Check the actual HTML of the <img> tags on frontend
    dom_imgs = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.post-content img, .detail-content img, article img, .content img')).map(img => ({
            outerHTML: img.outerHTML,
            currentSrc: img.currentSrc,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight
        }));
    }''')
    print("\nDOM img elements:")
    for di in dom_imgs:
        print(" -", di)
        
    browser.close()
