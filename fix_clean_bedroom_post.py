import os
import sys
import time
import re
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

def remove_flow_watermark(img_bgr):
    h, w = img_bgr.shape[:2]
    x1, y1 = max(0, w - 220), max(0, h - 180)
    x2, y2 = w - 5, h - 5
    patch = img_bgr[y1:y2, x1:x2]
    
    gray_patch = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    tophat = cv2.morphologyEx(gray_patch, cv2.MORPH_TOPHAT, kernel)
    
    _, mask = cv2.threshold(tophat, 14, 255, cv2.THRESH_BINARY)
    dilated_mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=2)
    
    inpainted = cv2.inpaint(patch, dilated_mask, 5, cv2.INPAINT_TELEA)
    res = img_bgr.copy()
    res[y1:y2, x1:x2] = inpainted
    return res

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

raw_dir = BASE_DIR / "output" / "b2c_bedroom_flow_1794368324"
out_clean_dir = BASE_DIR / "output" / f"bedroom_clean_nostar_{int(time.time())}"
out_clean_dir.mkdir(parents=True, exist_ok=True)

clean_files = []
ts = int(time.time())

for idx in range(5):
    raw_p = raw_dir / f"raw_flow_{idx}.jpg"
    bgr = cv2.imread(str(raw_p))
    clean_bgr = remove_flow_watermark(bgr)
    clean_rgb = cv2.cvtColor(clean_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(clean_rgb)
    
    # Crop 16:9
    w, h = pil_img.size
    target_h = int(w * 9 / 16)
    if h > target_h:
        top = (h - target_h) // 2
        pil_img = pil_img.crop((0, top, w, top + target_h))
    elif h < target_h:
        target_w = int(h * 16 / 9)
        left = (w - target_w) // 2
        pil_img = pil_img.crop((left, 0, left + target_w, h))
        
    pil_img = pil_img.resize((1376, 768), Image.Resampling.LANCZOS)
    stamped = stamp_top_left(pil_img, wm_img)
    
    clean_p = out_clean_dir / f"happyco_clean_nostar_{idx}_{ts}.jpg"
    stamped.save(clean_p, "JPEG", quality=95)
    clean_files.append(clean_p)
    print(f"✅ Đã xóa sạch logo Google Flow & đóng dấu TopLeft: {clean_p.name}")

# Upload and update CMS
CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill("input[name='email']", CMS_EMAIL)
    page.fill("input[name='password']", CMS_PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    cdn_urls = []
    cdn_filenames = []
    for idx, fpath in enumerate(clean_files):
        page.goto("https://happyco.asia/admin/media", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        
        btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
        btn.click()
        page.wait_for_timeout(1000)
        page.set_input_files("input[name='media_file']", str(fpath))
        page.fill("input[name='title']", f"Happyco Clean NoStar {idx} {ts}")
        page.locator("button:has-text('Lưu')").first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        cms_fn = fpath.name
        cdn_url = f"https://media.loveitopcdn.com/19180/{cms_fn}"
        cdn_urls.append(cdn_url)
        cdn_filenames.append(cms_fn)
        print(f"  [+] Uploaded Clean CDN: {cdn_url}")
        
    # Tìm bài viết đầu tiên trên /admin/post (bài vừa lên lịch lúc 11h)
    page.goto("https://happyco.asia/admin/post", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    first_edit_link = page.locator("table tbody tr td a[href*='/edit']").first
    edit_url = first_edit_link.get_attribute("href")
    print(f"Target Edit URL: {edit_url}")
    
    page.goto(edit_url, timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    # Cập nhật thumbnail sạch
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
    
    # Thay thế 4 ảnh trong CKEditor
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
    
    # Bấm Lưu
    page.evaluate("""() => {
        for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
        let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
        if (btn) btn.click();
    }""")
    page.wait_for_timeout(5000)
    print("🎉 ĐÃ CẬP NHẬT TOÀN BỘ ẢNH SẠCH 100% (ĐÃ XÓA NGÔI SAO GOOGLE FLOW) LÊN BÀI VIẾT!")
    browser.close()
