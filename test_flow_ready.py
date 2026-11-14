from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = browser.contexts[0].pages[0]
    if 'd7cecce7-8682-454a-bb94-13576243c599' not in page.url:
        page.goto('https://flow.google.com/project/d7cecce7-8682-454a-bb94-13576243c599', wait_until='domcontentloaded')
    page.wait_for_selector('[contenteditable="true"]:visible, [role="textbox"]:visible', timeout=30000)
    print('Project URL:', page.url)
    print('Page Title:', page.title())
    box = page.locator('[contenteditable="true"]:visible, [role="textbox"]:visible').first
    print('Prompt input box visible:', box.is_visible())

