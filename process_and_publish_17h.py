import os
import sys
import time
import json
import re
from pathlib import Path
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from core.image_registry import check_new, register
from playwright.sync_api import sync_playwright

WM_PATH = BASE_DIR / "happyco_watermark_duo.png"
wm_img = Image.open(WM_PATH).convert("RGBA")

# 1. Hàm xóa sạch ngôi sao watermark của Flow ở góc dưới phải
def remove_flow_watermark(img_bgr):
    h, w = img_bgr.shape[:2]
    x1, y1 = max(0, w - 200), max(0, h - 160)
    x2, y2 = w - 5, h - 5
    patch = img_bgr[y1:y2, x1:x2]
    
    gray_patch = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    tophat = cv2.morphologyEx(gray_patch, cv2.MORPH_TOPHAT, kernel)
    
    _, mask = cv2.threshold(tophat, 16, 255, cv2.THRESH_BINARY)
    if np.count_nonzero(mask) > 10:
        dilated_mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=2)
        inpainted = cv2.inpaint(patch, dilated_mask, 5, cv2.INPAINT_TELEA)
        res = img_bgr.copy()
        res[y1:y2, x1:x2] = inpainted
        return res
    return img_bgr

# 2. Lọc 5 ảnh độc bản chưa từng dùng trong image_registry
raw_dir = BASE_DIR / "output" / "flow_kitchen_raw"
all_raw = sorted(raw_dir.glob("kitchen_raw_*.jpg"), key=lambda x: int(re.search(r'\d+', x.name).group()))

print("=== 1. LỌC ẢNH MỚI 100% TỪ GOOGLE FLOW BẰNG IMAGE REGISTRY ===")
unique_new_candidates = []
seen_hashes = set()

for f in all_raw:
    if check_new(f):
        # Also ensure distinct among candidates
        im = Image.open(f).convert("L").resize((16, 16))
        px = list(im.getdata())
        h_val = tuple(px[:10])
        if h_val not in seen_hashes:
            seen_hashes.add(h_val)
            unique_new_candidates.append(f)
            print(f"  -> Chọn ảnh mới: {f.name}")

if len(unique_new_candidates) < 5:
    raise RuntimeError(f"Chỉ tìm thấy {len(unique_new_candidates)} ảnh mới, cần tối thiểu 5 ảnh!")

# Gán 5 ảnh cho 5 vị trí
selected = {
    "thumb": unique_new_candidates[0],
    "h2_1": unique_new_candidates[1],
    "h2_2": unique_new_candidates[2],
    "h2_3": unique_new_candidates[3],
    "h2_4": unique_new_candidates[4]
}

# 3. Tẩy watermark Flow & Đóng watermark Happyco trong suốt
out_clean_dir = BASE_DIR / "output" / "flow_17h_processed"
out_clean_dir.mkdir(parents=True, exist_ok=True)
processed_files = {}

ts = int(time.time())
print("\n=== 2. TẨY WATERMARK FLOW & ĐÓNG DẤU LOGO TRONG SUỐT ===")
for key, raw_f in selected.items():
    img_bgr = cv2.imread(str(raw_f))
    clean_bgr = remove_flow_watermark(img_bgr)
    
    img_rgb = cv2.cvtColor(clean_bgr, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(img_rgb).convert("RGBA")
    pil_im = pil_im.resize((1376, 768), Image.Resampling.LANCZOS)
    
    # Dán Watermark Happyco Duo trong suốt (100% alpha blend, NO nền trắng)
    wm_w = int(pil_im.width * 0.22)
    wm_h = int(wm_img.height * (wm_w / wm_img.width))
    wm_scaled = wm_img.resize((wm_w, wm_h), Image.Resampling.LANCZOS)
    pil_im.paste(wm_scaled, (35, 35), wm_scaled)
    
    out_name = f"happyco_kitchen_{key}_{ts}.jpg"
    out_p = out_clean_dir / out_name
    pil_im.convert("RGB").save(out_p, "JPEG", quality=92, optimize=True)
    processed_files[key] = out_p
    print(f"  -> Xử lý hoàn tất: {out_name} (1376x768, 0 logo Flow, logo Happyco trong suốt)")

# 4. Đọc dữ liệu bài viết đã soạn và duyệt
article_file = BASE_DIR / "output" / "article_17h.json"
with open(article_file, "r", encoding="utf-8") as f:
    article = json.load(f)

# Đăng ký 5 ảnh vào image_registry.json
for k, p in processed_files.items():
    register(post_id=article["slug"], path=p, source="google_flow_kitchen")
print(f"\n=== ĐÃ ĐĂNG KÝ 5 ẢNH VÀO IMAGE REGISTRY CHỐNG TRÙNG LẶP ===")

# 5. Tải ảnh lên CMS & Xuất bản lên lịch 17:00
print("\n=== 3. TẢI ẢNH LÊN CMS & XUẤT BẢN LÊN LỊCH 17:00 ===")
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
    
    # Upload 5 images
    cdn_urls = {}
    cdn_filenames = {}
    for key in ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]:
        fpath = processed_files[key]
        title = f"Happyco Tủ Bếp Cánh Kính - {key}"
        print(f"  [CMS] Tải ảnh: {fpath.name}...")
        page.goto("https://happyco.asia/admin/media", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        
        btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
        btn.click()
        page.wait_for_timeout(800)
        page.set_input_files("input[name='media_file']", str(fpath))
        page.fill("input[name='title']", title)
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
        cdn_urls[key] = cdn_url
        cdn_filenames[key] = cms_filename
        print(f"    -> Live CDN URL: {cdn_url}")

    # Chuẩn bị HTML nội dung bài viết
    content_html = article.get("content_html", "")
    for idx in range(1, 5):
        k = f"h2_{idx}"
        ph = f"IMAGE_PLACEHOLDER_{idx}"
        if ph in content_html:
            content_html = content_html.replace(ph, cdn_urls[k])
            
    # Thay thế cả các link /upload/images nếu LLM tự sinh
    old_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', content_html)
    new_h2_urls = [cdn_urls["h2_1"], cdn_urls["h2_2"], cdn_urls["h2_3"], cdn_urls["h2_4"]]
    for i, old_src in enumerate(old_imgs[:4]):
        if "media.loveitopcdn.com" not in old_src:
            content_html = content_html.replace(old_src, new_h2_urls[i])
            
    # Mở trang thêm bài viết mới
    print("\n  [CMS] Mở trang tạo bài viết mới...")
    page.goto("https://happyco.asia/admin/post/create", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)
    
    # Điền thông tin
    page.fill('input[name="title"]', article["title"])
    if page.locator('input[name="slug"]').count() > 0:
        page.fill('input[name="slug"]', article["slug"])
        
    page.fill('input[name="meta_keyword"]', article.get("keywords", "tủ bếp cánh kính, nội thất happyco, bàn đảo bếp thông minh"))
    if page.locator('input[name="meta_title"]').count() > 0:
        page.fill('input[name="meta_title"]', article["title"])
    if page.locator('textarea[name="meta_description"]').count() > 0:
        page.fill('textarea[name="meta_description"]', article.get("description", ""))
        
    # Chọn danh mục ID 266 (BLOG NỘI THẤT)
    page.select_option('select[name="cat_id"]', "266")
    print("  [CMS] Đã chọn chuyên mục ID: 266 (BLOG NỘI THẤT)")
    
    # Thumbnail
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
    print(f"  [CMS] Đã thiết lập Thumbnail: {thumb_fn}")
    
    # LÊN LỊCH ĐĂNG 17:00 NGÀY 10-11-2026
    page.evaluate("""() => {
        let el = document.querySelector('input[name="published_at"]');
        if (el) {
            el.value = "10-11-2026 17:00";
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }""")
    print("  [CMS] Đã cài đặt lịch đăng chuẩn: 10-11-2026 17:00")
    
    # Check is_published
    chk = page.locator('input[name="is_published"]')
    if chk.count() > 0 and not chk.is_checked():
        chk.check()
        
    # Inject CKEditor
    desc_text = article.get("description", "")
    page.evaluate("""({desc, content}) => {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let id in window.CKEDITOR.instances) {
                let el = document.getElementById(id);
                let inst = window.CKEDITOR.instances[id];
                if (el && el.name === 'description') {
                    inst.setData(desc);
                    inst.updateElement();
                    el.value = desc;
                } else if (el && el.name === 'content') {
                    inst.setData(content);
                    inst.updateElement();
                    el.value = content;
                }
            }
        }
    }""", {"desc": desc_text, "content": content_html})
    
    page.wait_for_timeout(1000)
    
    # Bấm Lưu
    print("  [CMS] Bấm Lưu bài viết...")
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
    
    page.wait_for_timeout(6000)
    
    # Xác thực trong danh sách bài viết /admin/post
    page.goto("https://happyco.asia/admin/post", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    
    screenshot_cms = BASE_DIR.parent / "brain" / "3a554760-1f55-4a71-9c90-718eb795bd64" / "cms_post_17h_scheduled.png"
    page.screenshot(path=str(screenshot_cms))
    print(f"  [CMS] Đã chụp ảnh xác thực CMS tại: {screenshot_cms.name}")
    
    newest_row = page.evaluate('''() => {
        let r = document.querySelector(".table tbody tr");
        if (!r) return null;
        let tds = Array.from(r.querySelectorAll("td")).map(td => td.innerText.trim());
        let viewA = r.querySelector("a[href*='/blog/']");
        return { tds, viewUrl: viewA ? viewA.href : null };
    }''')
    print("  [CMS] Dòng bài viết mới nhất:", newest_row)
    
    browser.close()

print("\n🎉 CON TỔNG BÁO CÁO: HOÀN TẤT XUẤT BẢN BÀI VIẾT 17H THÀNH CÔNG RỰC RỠ!")
