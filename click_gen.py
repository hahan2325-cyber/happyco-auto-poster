from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = b.contexts[0].pages[0]
    btn = page.locator('button[aria-label*="tạo"], button[aria-label*="Bắt đầu tạo"], button:has-text("arrow_forward")').first
    print("Button visible:", btn.is_visible())
    if btn.is_visible():
        btn.click()
        print("Clicked button successfully!")
