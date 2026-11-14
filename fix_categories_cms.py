import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

updates = [
    ("2381", "265"),  # GIA CÔNG VÁN CÔNG NGHIỆP
    ("2380", "266"),  # BLOG NỘI THẤT
    ("2379", "266"),  # BLOG NỘI THẤT
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill("input[name='email']", os.getenv("HAPPYCO_EMAIL"))
    page.fill("input[name='password']", os.getenv("HAPPYCO_PASSWORD"))
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)

    for post_id, cat_id in updates:
        page.goto(f"https://happyco.asia/admin/post/{post_id}/edit", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1200)

        page.select_option('select[name="cat_id"]', cat_id)
        page.wait_for_timeout(500)

        page.evaluate("""() => {
            for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(4000)
        print(f"✅ Updated Post {post_id} -> cat_id={cat_id}")

    # Verify CMS post list
    page.goto("https://happyco.asia/admin/post", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    proof_cms = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_fixed_categories_verified.png"
    page.screenshot(path=proof_cms)
    print(f"📸 CMS Proof: {proof_cms}")

    # Check live frontend category page from menu: BLOG -> DỊCH VỤ -> GIA CÔNG VÁN CÔNG NGHIỆP
    page.goto("https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep.html", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    proof_fe = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\frontend_giacongvan_category_verified.png"
    page.screenshot(path=proof_fe)
    print(f"📸 Frontend Category Proof ({page.url}): {proof_fe}")
    browser.close()
