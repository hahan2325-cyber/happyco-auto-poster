from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = b.contexts[0].pages[0]
    box = page.locator('textarea, [role="textbox"], [contenteditable="true"]').first
    box.click()
    page.wait_for_timeout(400)
    box.fill('Detailed macro close-up of a high-speed CNC nesting spindle router bit precisely cutting clean joints on green moisture-resistant MDF core, sharp edge, architectural documentary, 16:9, no people')
    page.wait_for_timeout(600)
    btn = page.locator('button[aria-label*="tạo"], button:has-text("arrow_forward")').first
    btn.click()
    print('Submitted prompt 1!')
    page.wait_for_timeout(4000)
    box.click()
    box.fill('Close-up technical documentary shot inside an industrial PUR edge banding machine, zero joint glue line, smooth roller press on green MDF panel, 16:9, no people')
    page.wait_for_timeout(600)
    btn = page.locator('button[aria-label*="tạo"], button:has-text("arrow_forward")').first
    btn.click()
    print('Submitted prompt 2!')
