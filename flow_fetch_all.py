import os
import sys
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

out_dir = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\output\flow_images")
out_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9333')
    context = browser.contexts[0]
    page = None
    for pg in context.pages:
        if 'flow.google.com' in pg.url:
            page = pg
            break
    
    if not page:
        print("Page not found")
        sys.exit(1)
        
    print("Found page:", page.url)
    
    # Download images with naturalWidth > 500
    images_data = page.evaluate('''async () => {
        const imgs = Array.from(document.querySelectorAll('img')).filter(img => img.naturalWidth > 500);
        const results = [];
        for (let i = 0; i < imgs.length; i++) {
            const img = imgs[i];
            try {
                const canvas = document.createElement('canvas');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
                results.push({
                    index: i,
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    dataUrl: dataUrl
                });
            } catch (e) {
                results.push({ index: i, error: e.toString() });
            }
        }
        return results;
    }''')
    
    print(f"Total large images retrieved: {len(images_data)}")
    for item in images_data:
        idx = item.get("index")
        if "dataUrl" in item:
            data = item["dataUrl"].split(",")[1]
            buf = base64.b64decode(data)
            fn = out_dir / f"flow_raw_{idx + 1}.jpg"
            with open(fn, "wb") as f:
                f.write(buf)
            print(f"Saved: {fn} ({item.get('width')}x{item.get('height')})")
        else:
            print(f"Error on img {idx}: {item.get('error')}")
