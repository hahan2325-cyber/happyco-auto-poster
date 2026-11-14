import os
import re
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\.env")
email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    # Login
    page.goto("https://happyco.asia/admin/login")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    # Check the top 2 posts in /admin/post
    page.goto("https://happyco.asia/admin/post")
    page.wait_for_load_state("networkidle")
    
    edit_urls = page.evaluate('''() => {
        return Array.from(document.querySelectorAll(".table tbody tr")).slice(0, 2).map(r => {
            let a = r.querySelector("a[href*='/edit']");
            return a ? a.href : null;
        });
    }''')
    print("Top 2 post edit URLs:", edit_urls)
    
    for edit_url in edit_urls:
        if not edit_url: continue
        print(f"\nChecking and cleaning: {edit_url}...")
        page.goto(edit_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        
        # 1. Clean description
        desc_el = page.locator("textarea[name='meta_description']").first
        if desc_el.is_visible():
            val = desc_el.input_value()
            clean_desc = re.sub(r'^(?:Bài viết|Bài viết này|Bài viết chia sẻ|Bài viết nhằm)\s*(?:này\s*)?(?:chia sẻ|giới thiệu|phân tích|cung cấp)?\s*[:,-]?\s*', '', val, flags=re.IGNORECASE).strip()
            if clean_desc != val:
                desc_el.fill(clean_desc)
                print(f"  -> Cleaned description: '{val[:40]}...' -> '{clean_desc[:40]}...'")
                
        # 2. Clean content in CKEditor
        content = page.evaluate('''() => {
            for (let k in window.CKEDITOR.instances) {
                if (document.getElementById(k) && document.getElementById(k).name === 'content') {
                    return window.CKEDITOR.instances[k].getData();
                }
            }
            return '';
        }''')
        
        orig_content = content
        # Remove FB greetings and title intro
        content = re.sub(r'(?:Chào anh em|Xin chào anh em|Chào các bạn|Xin chào các bạn|Anh em thân mến|Chào các bác thợ)[!,\.]?\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Với tư cách là[^,\.\n]+,\s*(?:tôi\s*)?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Tôi là[^,\.\n]+(?:kiêm|của)[^,\.\n]+,\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Chúng tôi là đội ngũ kỹ sư[^,\.\n]+,\s*', '', content, flags=re.IGNORECASE)
        
        if content != orig_content:
            print("  -> Found and cleaned Facebook phrases / personal title mentions from content!")
            page.evaluate("""({newc}) => {
                for (let k in window.CKEDITOR.instances) {
                    let el = document.getElementById(k);
                    let inst = window.CKEDITOR.instances[k];
                    if (el && el.name === 'content') {
                        inst.setData(newc);
                        inst.updateElement();
                        el.value = newc;
                    }
                }
            }""", {"newc": content})
            page.wait_for_timeout(1000)
            
            # Save
            print("  -> Saving cleaned post...")
            page.evaluate("""() => {
                if (window.swal) { try { swal.close(); } catch(e) {} }
                let overlays = document.querySelectorAll('.sweet-overlay, .sweet-alert');
                overlays.forEach(o => o.remove());
                for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
                let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
                if (btn) btn.click();
                else {
                    let f = document.getElementById('post-form') || document.querySelector('form');
                    if (f) f.submit();
                }
            }""")
            page.wait_for_timeout(5000)
            print("  -> Post saved successfully!")
        else:
            print("  -> Content already 100% clean!")
            
    browser.close()
    print("\n🎉 HOÀN TẤT DỌN SẠCH CẢ 2 BÀI VIẾT TRÊN CMS!")
