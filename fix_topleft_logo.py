import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

WM_PATH = BASE_DIR / "happyco_watermark_duo.png"
wm_img = Image.open(WM_PATH).convert("RGBA")

def stamp_top_left(img_pil, wm_pil):
    """Đóng dấu logo Happyco Duo vào GÓC TRÊN BÊN TRÁI (35, 35) - 100% TRONG SUỐT"""
    img_rgba = img_pil.convert("RGBA")
    w, h = img_rgba.size
    
    target_wm_w = int(w * 0.22)
    aspect = wm_pil.height / wm_pil.width
    target_wm_h = int(target_wm_w * aspect)
    
    resized_wm = wm_pil.resize((target_wm_w, target_wm_h), Image.Resampling.LANCZOS)
    
    # GÓC TRÊN BÊN TRÁI: (35, 35)
    pos_x = 35
    pos_y = 35
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay.paste(resized_wm, (pos_x, pos_y), resized_wm)
    
    combined = Image.alpha_composite(img_rgba, overlay)
    return combined.convert("RGB")

# 1. Đóng lại dấu vào góc trên bên trái cho 5 ảnh gốc chưa bị đóng dấu dưới phải
raw_dir = BASE_DIR / "output" / "parallel_b2b_harvest"
clean_fixed_dir = BASE_DIR / "output" / "b2b_fixed_topleft"
clean_fixed_dir.mkdir(parents=True, exist_ok=True)

# Lấy 5 ảnh gốc từ D:\Hình và Flow raw
img_sources = [
    BASE_DIR / "output" / "parallel_b2b_harvest" / "flow_b2b_raw_0_1794363748623.jpg",
    BASE_DIR / "output" / "parallel_b2b_harvest" / "flow_b2b_raw_1_1794363748628.jpg",
    Path(r"D:\Hình\Hình xưởng\Ảnh\1785739283447_1573466302153820722_g1615312412218766734_f68ec41b9f62d1d42a447ade9b9ef594.jpg"),
    Path(r"D:\Hình\Hình xưởng\Ảnh\1785739283458_1573466302153820722_g1615312412218766734_82d37047b0f063e965c794b84a4a6fec.jpg"),
    Path(r"D:\Hình\Hình xưởng\Ảnh\1785739283520_1573466302153820722_g1615312412218766734_aae81fe7be5085b2813dae57d89740b7.jpg"),
]

keys = ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]
ts_fixed = int(time.time())
fixed_images = {}

for idx, k in enumerate(keys):
    src = img_sources[idx]
    pil_src = Image.open(src).convert("RGB")
    
    # Chuẩn hóa tỷ lệ 16:9
    w, h = pil_src.size
    target_h = int(w * 9 / 16)
    if h > target_h:
        top = (h - target_h) // 2
        pil_src = pil_src.crop((0, top, w, top + target_h))
    elif h < target_h:
        target_w = int(h * 16 / 9)
        left = (w - target_w) // 2
        pil_src = pil_src.crop((left, 0, left + target_w, h))
        
    pil_src = pil_src.resize((1376, 768), Image.Resampling.LANCZOS)
    
    # Đóng dấu vào GÓC TRÊN TRÁI
    stamped = stamp_top_left(pil_src, wm_img)
    out_path = clean_fixed_dir / f"happyco_topleft_{k}_{ts_fixed}.jpg"
    stamped.save(out_path, "JPEG", quality=95)
    fixed_images[k] = out_path
    print(f"Đã đóng dấu GÓC TRÊN TRÁI: {out_path.name}")

# 2. Upload lên CDN và cập nhật bài 2378
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
    password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    cdn_urls = {}
    cdn_filenames = {}
    for k in keys:
        fpath = fixed_images[k]
        page.goto("https://happyco.asia/admin/media", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        
        btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
        btn.click()
        page.wait_for_timeout(1000)
        page.set_input_files("input[name='media_file']", str(fpath))
        page.fill("input[name='title']", f"Happyco B2B TopLeft {k} {ts_fixed}")
        page.locator("button:has-text('Lưu')").first.click()
        page.wait_for_timeout(3500)
        
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
        cdn_urls[k] = cdn_url
        cdn_filenames[k] = cms_filename
        print(f"Uploaded CDN TopLeft: {cdn_url}")

    # Cập nhật bài 2378
    page.goto("https://happyco.asia/admin/post/2378/edit", timeout=40000)
    page.wait_for_selector('input[name="title"]')
    
    # Cập nhật thumbnail
    thumb_fn = cdn_filenames["thumb"]
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

    # Cập nhật nội dung CKEditor thay thế các link ảnh cũ bằng link mới
    page.evaluate("""({h2_1, h2_2, h2_3, h2_4}) => {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let k in window.CKEDITOR.instances) {
                let el = document.getElementById(k);
                if (el && el.name === 'content') {
                    let html = window.CKEDITOR.instances[k].getData();
                    // Thay thế 4 ảnh trong bài
                    let imgs = [h2_1, h2_2, h2_3, h2_4];
                    let count = 0;
                    html = html.replace(/<img[^>]+src=["']([^"']+)["']/g, (match, src) => {
                        if (count < 4) {
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
    }""", {"h2_1": cdn_urls["h2_1"], "h2_2": cdn_urls["h2_2"], "h2_3": cdn_urls["h2_3"], "h2_4": cdn_urls["h2_4"]})

    page.wait_for_timeout(1000)
    
    # Bấm Lưu
    page.evaluate("""() => {
        for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
        let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
        if (btn) btn.click();
    }""")
    page.wait_for_timeout(5000)
    print("ĐÃ CẬP NHẬT THÀNH CÔNG BÀI VIẾT 2378 VỚI LOGO GÓC TRÊN TRÁI!")
    browser.close()
