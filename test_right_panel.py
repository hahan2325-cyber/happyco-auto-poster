from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = b.contexts[0].pages[0]
    # Check all img tags in document
    imgs = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('img')).map((img, idx) => ({
            idx: idx,
            src: img.src.slice(0, 80),
            w: img.naturalWidth,
            h: img.naturalHeight,
            visible: img.offsetParent !== null
        }));
    }''')
    print(f"Total imgs: {len(imgs)}")
    for i in imgs:
        if i['w'] > 200:
            print(i)
