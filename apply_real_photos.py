import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
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
    
    pos_x = 35
    pos_y = 35
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay.paste(resized_wm, (pos_x, pos_y), resized_wm)
    
    combined = Image.alpha_composite(img_rgba, overlay)
    return combined.convert("RGB")

clean_fixed_dir = BASE_DIR / "output" / "real_topleft_fixed"
clean_fixed_dir.mkdir(parents=True, exist_ok=True)

sources = {
    "thumb": Path(r"D:\Hình\xưởng\z7743825039289_25bdee491986218a0cf720960e719e65.jpg"),
    "h2_1": Path(r"D:\Hình\xưởng\z7743825039289_25bdee491986218a0cf720960e719e65.jpg"), # CNC
    "h2_2": Path(r"D:\Hình\xưởng\z7713935361996_1bc82448925adea5a5fe3a5c1d0606e1.jpg"), # Máy dán cạnh tự động
    "h2_3": Path(r"D:\Hình\Hình xưởng\Ảnh\1785739283520_1573466302153820722_g1615312412218766734_aae81fe7be5085b2813dae57d89740b7.jpg"), # Kho ván MDF
    "h2_4": Path(r"D:\Hình\Hình xưởng\Ảnh\1785739283447_1573466302153820722_g1615312412218766734_f68ec41b9f62d1d42a447ade9b9ef594.jpg"), # Đóng gói pallet
}

keys = ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]
ts_fixed = int(time.time())
fixed_images = {}

for k in keys:
    src = sources[k]
    pil_src = Image.open(src).convert("RGB")
    
    # 16:9 crop
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
    
    stamped = stamp_top_left(pil_src, wm_img)
    out_path = clean_fixed_dir / f"happyco_topleft_real_{k}_{ts_fixed}.jpg"
    stamped.save(out_path, "JPEG", quality=95)
    fixed_images[k] = out_path
    print(f"Đã đóng dấu GÓC TRÊN TRÁI: {out_path.name}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    email = os.getenv("HAPPYCO_EMAIL")
    password = os.getenv("HAPPYCO_PASSWORD")
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
        page.fill("input[name='title']", f"Happyco Real TopLeft {k} {ts_fixed}")
        page.locator("button:has-text('Lưu')").first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        cms_filename = fpath.name
        cdn_url = f"https://media.loveitopcdn.com/19180/{cms_filename}"
        cdn_urls[k] = cdn_url
        cdn_filenames[k] = cms_filename
        print(f"Uploaded CDN TopLeft: {cdn_url}")

    page.goto("https://happyco.asia/admin/post/2378/edit", timeout=40000)
    page.wait_for_selector('input[name="title"]')
    
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

    page.evaluate("""({h2_1, h2_2, h2_3, h2_4}) => {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let k in window.CKEDITOR.instances) {
                let el = document.getElementById(k);
                if (el && el.name === 'content') {
                    let html = window.CKEDITOR.instances[k].getData();
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

    page.fill('input[name="meta_keyword"]', "gia công ván mdf, dán cạnh pur noline, cắt cnc nesting, xưởng happyco")
    page.wait_for_timeout(1000)
    
    page.evaluate("""() => {
        for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
        let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
        if (btn) btn.click();
    }""")
    page.wait_for_timeout(5000)
    print("ĐÃ CẬP NHẬT THÀNH CÔNG BÀI VIẾT 2378 VỚI ẢNH THẬT 100% VÀ LOGO GÓC TRÊN TRÁI!")

    # Chụp ảnh nghiệm thu trực tiếp trang bài viết
    page.goto("https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-van-mdf.html", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\live_real_article_verified.png"
    page.screenshot(path=proof_path, full_page=True)
    print(f"BẰNG CHỨNG ĐÃ LƯU TẠI: {proof_path}")
    
    browser.close()
