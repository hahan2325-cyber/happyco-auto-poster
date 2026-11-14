import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from core.image_registry import check_new

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = b.contexts[0].pages[0]
    imgs = page.evaluate('''async () => {
        const imgs = Array.from(document.querySelectorAll('img')).filter(img => img.naturalWidth > 500);
        const results = [];
        for (let i = 0; i < imgs.length; i++) {
            const canvas = document.createElement('canvas');
            canvas.width = imgs[i].naturalWidth;
            canvas.height = imgs[i].naturalHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(imgs[i], 0, 0);
            results.push({index: i, data: canvas.toDataURL('image/jpeg', 0.95)});
        }
        return results;
    }''')
    print('Fetched imgs:', len(imgs))
    out_dir = Path('output/check_new_test')
    out_dir.mkdir(parents=True, exist_ok=True)
    new_count = 0
    new_files = []
    for item in imgs:
        buf = base64.b64decode(item['data'].split(',')[1])
        fn = out_dir / f"test_{item['index']}.jpg"
        fn.write_bytes(buf)
        if check_new(fn):
            new_count += 1
            new_files.append(fn)
            print('NEW:', fn.name)
    print('Total NEW:', new_count)
