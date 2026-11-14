from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = b.contexts[0].pages[0]
    time.sleep(3)
    box = page.locator('textarea, [role="textbox"], [contenteditable="true"]').first
    box.click()
    page.wait_for_timeout(400)
    box.fill('Detailed industrial photography of a CNC router cutting clean cam and dowel holes on green moisture-resistant MDF cabinet parts, workshop dust extraction, 16:9 widescreen, no people')
    page.wait_for_timeout(600)
    btn = page.locator('button[aria-label*="tạo"], button:has-text("arrow_forward")').first
    btn.click()
    print('Submitted prompt 4!')
