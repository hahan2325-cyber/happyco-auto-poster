import time
import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

prompts = [
    "Spacious modern luxury open-concept kitchen and dining interior, dark anodized aluminum glass cabinets, marble waterfall island with bar stools, warm 3000K ambient light, 16:9 widescreen, no people",
    "Modern luxury kitchen interior with sleek dark anodized aluminum frame glass upper cabinets, warm internal led illumination, quartz countertop, architectural photography, 16:9, no people",
    "Modern luxury kitchen island combined with minimalist wooden dining table, marble countertop, designer pendant lights, open floor plan, architectural photography, 16:9, no people",
    "Modern elegant kitchen cabinetry with softly rounded curved corner edges, matte warm grey finish, child safe minimalist design, architectural photography, 16:9, no people",
    "Clean modern architectural photo of premium customized kitchen cabinet system with built-in appliances, seamless PUR edge banding, warm ambient lighting, 16:9, no people"
]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
    page = browser.contexts[0].pages[0]
    print(f"Connected to Flow page: {page.url}")
    
    # Check textarea or prompt input box
    for idx, prompt_text in enumerate(prompts, 1):
        print(f"\n[Flow Queue] Đang gửi prompt {idx}/5...")
        
        # Look for textarea or role=textbox
        box = page.locator("textarea").first
        if not box.is_visible():
            box = page.locator("[role='textbox']").first
        if not box.is_visible():
            box = page.locator("[contenteditable='true']").first
            
        box.click()
        page.wait_for_timeout(400)
        box.fill(prompt_text)
        page.wait_for_timeout(600)
        
        # Click the submit button or press Enter
        submit_btn = page.locator("button:has-text('keyboard_return'), button[aria-label*='Generate'], button[aria-label*='Send'], button:has-text('arrow_upward')").first
        if submit_btn.is_visible():
            submit_btn.click()
            print(f"  -> Đã bấm nút gửi prompt {idx} thành công!")
        else:
            box.press("Enter")
            print(f"  -> Đã nhấn Enter gửi prompt {idx} thành công!")
            
        # Nghỉ 2 giây rồi bơm tiếp prompt tiếp theo ngay, KHÔNG CHỜ đợi sinh xong
        page.wait_for_timeout(2000)

    print("\n🎉 ĐÃ BƠM TOÀN BỘ 5 PROMPT LIÊN TIẾP VÀO GOOGLE FLOW ĐỂ TẠO SONG SONG!")
