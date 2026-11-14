from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = b.contexts[0].pages[0]
    time.sleep(3)
    box = page.locator('textarea, [role="textbox"], [contenteditable="true"]').first
    box.click()
    page.wait_for_timeout(400)
    box.fill('Close-up shot of a stainless steel digital vernier caliper precisely measuring the thickness and groove depth of green MDF core panel after CNC cutting, high precision woodworking, 16:9, no people')
    page.wait_for_timeout(600)
    btn = page.locator('button[aria-label*="tạo"], button:has-text("arrow_forward")').first
    btn.click()
    print('Submitted prompt 3!')
