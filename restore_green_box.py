import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

GREEN_BOX_HTML = """<div style="border: 2px dashed #008848; background: #f6fff9; border-radius: 8px; padding: 18px 22px; margin: 28px 0;">
  <p style="color: #008848; font-weight: bold; margin: 0 0 8px 0; font-size: 16px;">Chúng Tôi Nhận Thiết Kế Nội Thất Ngành Mộc Tại Các Khu Vực Sau:</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">- Miền Nam: Thành phố Hồ Chí Minh, Đồng Nai, Tây Ninh, Thành phố Cần Thơ, Vĩnh Long, Đồng Tháp, Cà Mau, An Giang.</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">📍 <strong>Địa chỉ công ty:</strong> 526/2, Khu phố 8A, Phường Long Bình, thành phố Đồng Nai.</p>
  <p style="margin: 6px 0; color: #d32f2f; font-weight: bold; font-size: 16px;">📞 Liên hệ: 0946 272 286 (Đức Anh)</p>
</div>"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill("input[name='email']", os.getenv("HAPPYCO_EMAIL"))
    page.fill("input[name='password']", os.getenv("HAPPYCO_PASSWORD"))
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)

    for post_id in ["2381", "2380", "2379", "2378"]:
        page.goto(f"https://happyco.asia/admin/post/{post_id}/edit", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1200)

        updated = page.evaluate("""(greenBox) => {
            if (!window.CKEDITOR || !window.CKEDITOR.instances) return 'no_editor';
            for (let k in window.CKEDITOR.instances) {
                let el = document.getElementById(k);
                if (el && el.name === 'content') {
                    let html = window.CKEDITOR.instances[k].getData();
                    // Xóa mọi box cũ nếu có để tránh trùng lặp, rồi gắn duy nhất 1 GREEN_BOX chuẩn ở cuối
                    html = html.replace(/(?:<hr[^>]*>\\s*)?<div[^>]*>[\\s\\S]*?526\\/2[\\s\\S]*?0946\\s*272\\s*286[\\s\\S]*?<\\/div>/gi, '');
                    html = html.replace(/(?:<hr[^>]*>\\s*)?<div[^>]*class=["'][^"']*happyco-footer[^"']*["'][^>]*>[\\s\\S]*?<\\/div>/gi, '');
                    html = html.trim() + "\\n" + greenBox;
                    window.CKEDITOR.instances[k].setData(html);
                    window.CKEDITOR.instances[k].updateElement();
                    el.value = html;
                    return 'restored';
                }
            }
            return 'no_content';
        }""", GREEN_BOX_HTML)

        page.evaluate("""() => {
            for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(3500)
        print(f"✅ Post {post_id}: {updated}")

    # Verify live Post 2381 footer shows BOTH green dashed box AND banner together
    page.goto("https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-dan-canh-pur-noline-vat-tay-nam-j-k-canh-tu-happyco-1794451236.html", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.62)")
    page.wait_for_timeout(1500)
    proof = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\live_2381_both_footers_restored.png"
    page.screenshot(path=proof)
    print(f"📸 Saved live proof: {proof}")
    browser.close()
