import os
import sys
import base64
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
out_raw_dir = BASE_DIR / "output" / "flow_kitchen_raw"
out_raw_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = browser.contexts[0].pages[0]
    print(f"Connected to Flow page: {page.url}")
    
    # Download all large images
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
            fn = out_raw_dir / f"kitchen_raw_{idx + 1}.jpg"
            with open(fn, "wb") as f:
                f.write(buf)
            print(f"Saved: {fn.name} ({item.get('width')}x{item.get('height')})")
