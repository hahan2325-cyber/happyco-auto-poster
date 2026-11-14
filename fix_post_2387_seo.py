import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")

# Chuẩn SEO 50-65 chars
SEO_TITLE_2387 = "5 Lỗi Xuất File ABF SketchUp Cắt CNC Làm Hao Phôi Ván"  # 53 ký tự
SEO_KEYWORDS_2387 = "lỗi file abf sketchup, cắt cnc nesting, gia công ván abf"
SEO_SLUG_2387 = "5-loi-xuat-file-abf-sketchup-cat-cnc-hao-phoi"

print(f"Post 2387 - Tiêu đề mới: {SEO_TITLE_2387} ({len(SEO_TITLE_2387)} chars)")
print(f"Post 2387 - Từ khóa mới: {SEO_KEYWORDS_2387}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill('input[name="email"]', CMS_EMAIL)
    page.fill('input[name="password"]', CMS_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    
    page.goto("https://happyco.asia/admin/post/2387/edit", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    
    page.fill('input[name="title"]', SEO_TITLE_2387)
    page.fill('input[name="meta_keyword"]', SEO_KEYWORDS_2387)
    page.fill('input[name="slug"]', SEO_SLUG_2387)
    
    page.evaluate("""() => {
        if (window.CKEDITOR) {
            for (let k in window.CKEDITOR.instances) {
                window.CKEDITOR.instances[k].updateElement();
            }
        }
    }""")
    page.wait_for_timeout(500)
    
    submit_btn = page.locator('button[onclick*="nav_submit_form"]').first
    if submit_btn.count() == 0:
        submit_btn = page.locator('.btn-info.btn-ladda, button[type="submit"]:has-text("Lưu")').first
    submit_btn.click()
    
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    
    # Mở lại trang edit chụp ảnh màn hình
    page.goto("https://happyco.asia/admin/post/2387/edit", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    
    proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_2387_seo_fixed.png"
    page.screenshot(path=proof_path)
    print(f"📸 Đã lưu ảnh minh chứng cập nhật SEO Post 2387: {proof_path}")
    browser.close()
