import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\.env")
email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")

live_urls = {
    "thumb": "111312-flow_thumb_living.jpg",
    "h2_1": "https://media.loveitopcdn.com/19180/111320-flow_h2_1_vach_tivi.jpg",
    "h2_2": "https://media.loveitopcdn.com/19180/111327-flow_h2_2_tu_ruou.jpg",
    "h2_3": "https://media.loveitopcdn.com/19180/111335-flow_h2_3_phong_ngu.jpg",
    "h2_4": "https://media.loveitopcdn.com/19180/111343-flow_h2_4_tu_ao.jpg"
}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    # 1. Login
    page.goto("https://happyco.asia/admin/login")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    # 2. Go to post 2376 edit page
    edit_url = "https://happyco.asia/admin/post/2376/edit"
    print("Navigating to:", edit_url)
    page.goto(edit_url, timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    # 3. Get current content
    current_content = page.evaluate('''() => {
        let content = '';
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let k in window.CKEDITOR.instances) {
                if (document.getElementById(k) && document.getElementById(k).name === 'content') {
                    content = window.CKEDITOR.instances[k].getData();
                }
            }
        }
        return content;
    }''')
    
    # Replace all broken image URLs in sequential order
    # Find all <img ... src="..."
    old_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', current_content)
    print("Found old images in content:", old_imgs)
    
    h2_replacements = [live_urls["h2_1"], live_urls["h2_2"], live_urls["h2_3"], live_urls["h2_4"]]
    new_content = current_content
    for i, old_src in enumerate(old_imgs[:4]):
        new_src = h2_replacements[i]
        new_content = new_content.replace(old_src, new_src)
        print(f"Replaced: {old_src} -> {new_src}")
        
    # 4. Set thumbnail to correct CDN file
    thumb_name = live_urls["thumb"]
    thumb_preview = f"https://media.loveitopcdn.com/19180/thumb/150x150/{thumb_name}?zc=1"
    page.evaluate("""({tval, tprev}) => {
        let el = document.getElementById('thumbnail');
        if (el) {
            el.value = tval;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
        let holder = document.getElementById('holder_thumbnail');
        if (holder) holder.src = tprev;
    }""", {"tval": thumb_name, "tprev": thumb_preview})
    print(f"Set thumbnail: {thumb_name}")
    
    # 5. Inject updated content into CKEditor
    page.evaluate("""({content}) => {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let id in window.CKEDITOR.instances) {
                let el = document.getElementById(id);
                let inst = window.CKEDITOR.instances[id];
                if (el && el.name === 'content') {
                    inst.setData(content);
                    inst.updateElement();
                    el.value = content;
                }
            }
        }
    }""", {"content": new_content})
    
    page.wait_for_timeout(1000)
    
    # Dismiss any swal
    page.evaluate("""() => {
        if (window.swal) { try { swal.close(); } catch(e) {} }
        let overlays = document.querySelectorAll('.sweet-overlay, .sweet-alert');
        overlays.forEach(o => o.remove());
    }""")
    
    # Save post
    print("Clicking save...")
    page.evaluate("""() => {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
        }
        let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
        if (btn) btn.click();
        else {
            let f = document.getElementById('post-form') || document.querySelector('form');
            if (f) f.submit();
        }
    }""")
    
    page.wait_for_timeout(6000)
    
    # 6. Verify frontend post view
    view_url = "https://happyco.asia/blog/thiet-ke-vach-tivi-phong-khach-ket-hop-tu-ruou-canh-kinh-hien-dai-dang-cap-sang-trong-tu-xuong-happyco.html"
    print("Navigating to frontend article:", view_url)
    page.goto(view_url, timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    # Check all images on frontend
    page_imgs = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('.blog-detail img, .post-detail img, article img, .content img, img')).map(img => ({
            src: img.src,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight,
            complete: img.complete
        })).filter(x => x.src && x.src.includes('19180'));
    }''')
    print(f"Frontend images loaded: {len(page_imgs)}")
    for pi in page_imgs:
        print(" ->", pi)
        
    screenshot_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\frontend_post_verified.png"
    page.screenshot(path=screenshot_path)
    print("Screenshot saved to:", screenshot_path)
    
    browser.close()
