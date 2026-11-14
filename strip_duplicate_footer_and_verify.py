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

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill("input[name='email']", os.getenv("HAPPYCO_EMAIL"))
    page.fill("input[name='password']", os.getenv("HAPPYCO_PASSWORD"))
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)

    # Clean duplicate footer box on posts 2381, 2380, 2379, 2378
    for post_id in ["2381", "2380", "2379", "2378"]:
        page.goto(f"https://happyco.asia/admin/post/{post_id}/edit", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        changed = page.evaluate("""() => {
            if (!window.CKEDITOR || !window.CKEDITOR.instances) return false;
            for (let k in window.CKEDITOR.instances) {
                let el = document.getElementById(k);
                if (el && el.name === 'content') {
                    let html = window.CKEDITOR.instances[k].getData();
                    let orig = html;
                    // Xóa các div footer tự chèn và hr trước nó
                    html = html.replace(/(?:<hr[^>]*>\\s*)?<div[^>]*class=["'][^"']*happyco-footer[^"']*["'][^>]*>[\\s\\S]*?<\\/div>/gi, '');
                    // Xóa mọi đoạn footer chứa 526/2 hoặc 0946 272 286 ở cuối bài nếu bị chèn thêm
                    html = html.replace(/(?:<hr[^>]*>\\s*)?<div[^>]*>[\\s\\S]*?526\\/2[\\s\\S]*?0946\\s*272\\s*286[\\s\\S]*?<\\/div>/gi, '');
                    if (html !== orig) {
                        window.CKEDITOR.instances[k].setData(html);
                        window.CKEDITOR.instances[k].updateElement();
                        el.value = html;
                        return true;
                    }
                }
            }
            return false;
        }""")

        if changed:
            page.evaluate("""() => {
                for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
                let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
                if (btn) btn.click();
            }""")
            page.wait_for_timeout(3500)
            print(f"✅ Removed duplicate footer from Post {post_id}")
        else:
            print(f"ℹ️ Post {post_id} already clean (no extra footer).")

    # Verify live frontend category URL from navigation menu
    page.goto("https://happyco.asia", timeout=40000)
    page.wait_for_load_state("networkidle")
    cat_href = page.evaluate("""() => {
        const links = Array.from(document.querySelectorAll('a'));
        const target = links.find(a => (a.textContent || '').trim().toUpperCase() === 'GIA CÔNG VÁN CÔNG NGHIỆP');
        return target ? target.href : null;
    }""")
    print("Menu link for GIA CÔNG VÁN CÔNG NGHIỆP:", cat_href)
    if cat_href:
        page.goto(cat_href, timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        proof_cat = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\live_menu_giacongvan_proof.png"
        page.screenshot(path=proof_cat)
        print(f"📸 Saved live menu category screenshot: {proof_cat}")

        # Open Post 2381 live page bottom to verify ONLY the website's 2 hardcoded footer blocks exist
        first_post_href = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('a'));
            const match = links.find(a => (a.textContent || '').includes('PUR Noline'));
            return match ? match.href : null;
        }""")
        print("Post 2381 live URL:", first_post_href)
        if first_post_href:
            page.goto(first_post_href, timeout=40000)
            page.wait_for_load_state("networkidle")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.65)")
            page.wait_for_timeout(1500)
            proof_bottom = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\live_2381_footer_clean_proof.png"
            page.screenshot(path=proof_bottom)
            print(f"📸 Saved live post 2381 footer screenshot: {proof_bottom}")
    browser.close()
