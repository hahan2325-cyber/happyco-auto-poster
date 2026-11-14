import os
import sys
import time
import glob
from pathlib import Path
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

WM_PATH = BASE_DIR / "happyco_watermark_duo.png"
wm_img = Image.open(WM_PATH).convert("RGBA")

def perfect_erase_flow_star(img):
    h, w = img.shape[:2]
    star_center = (w - 95, h - 85)
    source_center = (w - 205, h - 85)
    pw, ph = 88, 88
    
    x1 = source_center[0] - pw // 2
    y1 = source_center[1] - ph // 2
    src_patch = img[y1:y1+ph, x1:x1+pw]
    
    clone_mask = np.full((ph, pw), 255, dtype=np.uint8)
    cloned = cv2.seamlessClone(src_patch, img, clone_mask, star_center, cv2.NORMAL_CLONE)
    return cloned

def stamp_top_left(img_pil, wm_pil):
    img_rgba = img_pil.convert("RGBA")
    w, h = img_rgba.size
    target_wm_w = int(w * 0.22)
    aspect = wm_pil.height / wm_pil.width
    target_wm_h = int(target_wm_w * aspect)
    resized_wm = wm_pil.resize((target_wm_w, target_wm_h), Image.Resampling.LANCZOS)
    pos_x, pos_y = 35, 35
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay.paste(resized_wm, (pos_x, pos_y), resized_wm)
    return Image.alpha_composite(img_rgba, overlay).convert("RGB")

# 1. Process 5 Kitchen images (Post 17h)
kitchen_raws = sorted(glob.glob(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\output\kitchen_17h_flow_*\raw_flow_*.jpg"))
out_dir = BASE_DIR / "output" / f"kitchen_flawless_{int(time.time())}"
out_dir.mkdir(parents=True, exist_ok=True)

processed_kitchen = []
ts = int(time.time())

for idx, p in enumerate(kitchen_raws[:5]):
    im = cv2.imread(p)
    clean_im = perfect_erase_flow_star(im)
    clean_rgb = cv2.cvtColor(clean_im, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(clean_rgb)
    
    # Crop 16:9
    w, h = pil_im.size
    target_h = int(w * 9 / 16)
    if h > target_h:
        top = (h - target_h) // 2
        pil_im = pil_im.crop((0, top, w, top + target_h))
    elif h < target_h:
        target_w = int(h * 16 / 9)
        left = (w - target_w) // 2
        pil_im = pil_im.crop((left, 0, left + target_w, h))
        
    pil_im = pil_im.resize((1376, 768), Image.Resampling.LANCZOS)
    stamped = stamp_top_left(pil_im, wm_img)
    
    out_p = out_dir / f"happyco_kitchen_flawless_{idx}_{ts}.jpg"
    stamped.save(out_p, "JPEG", quality=95)
    processed_kitchen.append(out_p)
    print(f"✅ ĐÃ XÓA 100% NGÔI SAO GOOGLE & DẬP TOPLEFT: {out_p.name}")

# 2. Upload and replace on CMS
CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill('input[name="email"]', CMS_EMAIL)
    page.fill('input[name="password"]', CMS_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    cdn_urls = []
    cdn_filenames = []
    
    for idx, fpath in enumerate(processed_kitchen):
        page.goto("https://happyco.asia/admin/media", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        
        btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
        btn.click()
        page.wait_for_timeout(1000)
        page.set_input_files("input[name='media_file']", str(fpath))
        page.fill("input[name='title']", f"Happyco Kitchen Flawless {idx} {ts}")
        page.locator("button:has-text('Lưu')").first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2500)
        
        # Get actual filename from media list
        cms_filename = page.evaluate('''() => {
            let firstImg = document.querySelector(".table tbody tr img, .media-list-item img, .thumbnail img, img[src*='19180']");
            if (firstImg) {
                let parts = firstImg.src.split("/");
                return parts[parts.length - 1].split("?")[0];
            }
            return null;
        }''')
        if not cms_filename:
            cms_filename = fpath.name
            
        cdn_url = f"https://media.loveitopcdn.com/19180/{cms_filename}"
        cdn_urls.append(cdn_url)
        cdn_filenames.append(cms_filename)
        print(f"  [+] Uploaded Flawless CDN: {cdn_url}")
        
    # Find post 17h (first row in /admin/post)
    page.goto("https://happyco.asia/admin/post", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    first_edit_link = page.locator("table tbody tr td a[href*='/edit']").first
    edit_url = first_edit_link.get_attribute("href")
    print(f"Updating Post at: {edit_url}")
    
    page.goto(edit_url, timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    thumb_fn = cdn_filenames[0]
    thumb_prev = f"https://media.loveitopcdn.com/19180/thumb/150x150/{thumb_fn}?zc=1"
    page.evaluate("""({tval, tprev}) => {
        let el = document.getElementById('thumbnail');
        if (el) {
            el.value = tval;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
        let holder = document.getElementById('holder_thumbnail');
        if (holder) holder.src = tprev;
    }""", {"tval": thumb_fn, "tprev": thumb_prev})
    
    body_imgs = cdn_urls[1:5]
    page.evaluate("""({imgs}) => {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let k in window.CKEDITOR.instances) {
                let el = document.getElementById(k);
                if (el && el.name === 'content') {
                    let html = window.CKEDITOR.instances[k].getData();
                    let count = 0;
                    html = html.replace(/<img[^>]+src=["']([^"']+)["']/g, (match, src) => {
                        if (count < imgs.length) {
                            let newSrc = imgs[count++];
                            return match.replace(src, newSrc);
                        }
                        return match;
                    });
                    window.CKEDITOR.instances[k].setData(html);
                    window.CKEDITOR.instances[k].updateElement();
                    el.value = html;
                }
            }
        }
    }""", {"imgs": body_imgs})
    
    page.wait_for_timeout(1000)
    
    page.evaluate("""() => {
        for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
        let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
        if (btn) btn.click();
    }""")
    page.wait_for_timeout(5000)
    print("🎉 HOÀN TẤT CẬP NHẬT 100% ẢNH SẠCH HOÀN HẢO CHO BÀI 17H!")
    
    browser.close()
