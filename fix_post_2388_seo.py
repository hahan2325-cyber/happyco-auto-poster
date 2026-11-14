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

# Tiêu đề chuẩn SEO (50-65 ký tự, chứa từ khóa chính ngay đầu, không bị cắt trên Google Search)
SEO_TITLE = "Nội Thất Phong Cách Japandi Gỗ Sồi Đẹp Tinh Tế Cho Nhà Phố"  # 57 ký tự
SEO_KEYWORDS = "nội thất japandi gỗ sồi, phong cách japandi, nội thất nhà phố"  # 3 cụm ngắn chuẩn
SEO_SLUG = "noi-that-phong-cach-japandi-go-soi-cho-nha-pho"

print(f"Tiêu đề mới: {SEO_TITLE} ({len(SEO_TITLE)} ký tự - Chuẩn Google 50-65 chars)")
print(f"Từ khóa mới: {SEO_KEYWORDS}")
print(f"Slug mới: {SEO_SLUG}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill('input[name="email"]', CMS_EMAIL)
    page.fill('input[name="password"]', CMS_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)
    
    page.goto("https://happyco.asia/admin/post/2388/edit", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    
    # Cập nhật Tiêu đề, Từ khóa, Slug
    page.fill('input[name="title"]', SEO_TITLE)
    page.fill('input[name="meta_keyword"]', SEO_KEYWORDS)
    page.fill('input[name="slug"]', SEO_SLUG)
    
    # Đồng bộ CKEditor trước khi submit
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
    
    # Mở lại trang edit để chụp ảnh màn hình xác nhận form đã chuẩn
    page.goto("https://happyco.asia/admin/post/2388/edit", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    
    proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_2388_seo_fixed.png"
    page.screenshot(path=proof_path)
    print(f"📸 Đã lưu ảnh minh chứng cập nhật SEO: {proof_path}")
    browser.close()
