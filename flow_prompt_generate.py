import time
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

out_dir = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\output\flow_images")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9333')
    context = browser.contexts[0]
    page = [pg for pg in context.pages if 'flow.google.com' in pg.url][0]
    
    print("Page URL:", page.url)
    
    # Count current large images
    initial_count = page.evaluate("() => document.querySelectorAll('img').length")
    print("Initial img count:", initial_count)
    
    # Find the prompt input
    # In Google Flow, prompt box is often textarea or contenteditable
    prompt_box = page.locator("textarea").first
    if not prompt_box.is_visible():
        prompt_box = page.locator("[contenteditable='true']").first
        
    print("Prompt box found:", prompt_box)
    prompt_text = "Modern luxury walk-in wardrobe closet interior with slim glass doors, warm led strip illumination, organized wooden shelves, clean architectural photography, 16:9, no people"
    
    prompt_box.click()
    prompt_box.fill(prompt_text)
    time.sleep(1)
    prompt_box.press("Enter")
    print("Prompt submitted! Waiting for generation...")
    
    # Wait up to 30 seconds for new images to appear
    for attempt in range(15):
        time.sleep(3)
        current_imgs = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('img'))
                .filter(img => img.naturalWidth > 500)
                .map(img => img.src);
        }''')
        print(f"Check {attempt + 1}: Found {len(current_imgs)} large images")
        if len(current_imgs) > 4:
            print("New images detected!")
            break
            
    # Download the latest image
    latest_img = page.evaluate('''() => {
        const imgs = Array.from(document.querySelectorAll('img')).filter(img => img.naturalWidth > 500);
        if (imgs.length === 0) return null;
        const img = imgs[imgs.length - 1];
        const canvas = document.createElement('canvas');
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        return {
            width: img.naturalWidth,
            height: img.naturalHeight,
            dataUrl: canvas.toDataURL('image/jpeg', 0.95)
        };
    }''')
    
    if latest_img and "dataUrl" in latest_img:
        data = latest_img["dataUrl"].split(",")[1]
        buf = base64.b64decode(data)
        fn = out_dir / "flow_raw_5.jpg"
        with open(fn, "wb") as f:
            f.write(buf)
        print(f"Saved 5th image: {fn} ({latest_img['width']}x{latest_img['height']})")
