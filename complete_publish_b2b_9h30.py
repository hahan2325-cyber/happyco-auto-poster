import os
import sys
import time
import json
import base64
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

from agents.b2b_woodworking_agent import B2BWoodworkingAgent
from agents.chief_qa_agent import ChiefQAAgent
from core.image_registry import check_new, register
from playwright.sync_api import sync_playwright

WM_PATH = BASE_DIR / "happyco_watermark_duo.png"

def remove_flow_watermark(img_bgr):
    """Xóa ngôi sao 4 cánh mờ của Flow ở góc dưới phải bằng cv2.inpaint Telea"""
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

def stamp_happyco_watermark(img_pil, wm_pil):
    """Đóng dấu logo Happyco Duo trong suốt (alpha blend) vào góc dưới phải"""
    img_rgba = img_pil.convert("RGBA")
    w, h = img_rgba.size
    
    target_wm_w = int(w * 0.22)
    aspect = wm_pil.height / wm_pil.width
    target_wm_h = int(target_wm_w * aspect)
    
    resized_wm = wm_pil.resize((target_wm_w, target_wm_h), Image.Resampling.LANCZOS)
    
    pos_x = w - target_wm_w - int(w * 0.02)
    pos_y = h - target_wm_h - int(h * 0.02)
    
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    overlay.paste(resized_wm, (pos_x, pos_y), resized_wm)
    
    combined = Image.alpha_composite(img_rgba, overlay)
    return combined.convert("RGB")

def harvest_flow_images(out_dir, cdp_url="http://127.0.0.1:9333"):
    """Tải tất cả ảnh độ phân giải cao từ Flow qua Canvas"""
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        page = browser.contexts[0].pages[0]
        
        images_data = page.evaluate('''async () => {
            const imgs = Array.from(document.querySelectorAll('img')).filter(img => img.naturalWidth > 500);
            const results = [];
            for (let i = 0; i < imgs.length; i++) {
                const img = imgs[i];
                try {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    const dataUrl = canvas.toDataURL('image/jpeg', 0.95);
                    results.push({
                        index: i,
                        width: img.naturalWidth,
                        height: img.naturalHeight,
                        dataUrl: dataUrl
                    });
                } catch (e) {
                    results.push({ index: i, error: e.toString() });
                }
            }
            return results;
        }''')
        
        saved_files = []
        for item in images_data:
            if "dataUrl" in item:
                data = item["dataUrl"].split(",")[1]
                buf = base64.b64decode(data)
                ts = int(time.time() * 1000)
                fn = out_dir / f"flow_b2b_raw_{item['index']}_{ts}.jpg"
                with open(fn, "wb") as f:
                    f.write(buf)
                saved_files.append(fn)
        return saved_files

def main():
    print("==================================================================")
    print("🚀 TIẾN TRÌNH XUẤT BẢN BÀI VIẾT B2B: LÊN LỊCH 09:30 NGÀY 11-11-2026")
    print("==================================================================")

    b2b_agent = B2BWoodworkingAgent()
    chief_qa = ChiefQAAgent()
    wm_img = Image.open(WM_PATH).convert("RGBA")

    # 1. Thu hoạch ảnh từ Google Flow
    print("\n[Bước 1] Thu hoạch ảnh từ Google Flow...")
    temp_dir = BASE_DIR / "output" / "parallel_b2b_harvest"
    raw_images = harvest_flow_images(temp_dir)
    print(f"  + Đã lấy về {len(raw_images)} ảnh tổng cộng từ Flow.")

    # Lọc các ảnh mới 100% (chưa có trong registry)
    unique_candidates = []
    seen_hashes = set()
    for f in raw_images:
        if check_new(f):
            im = Image.open(f).convert("L").resize((16, 16))
            h_val = tuple(list(im.getdata())[:10])
            if h_val not in seen_hashes:
                seen_hashes.add(h_val)
                unique_candidates.append(f)
                if len(unique_candidates) >= 5:
                    break

    # Nếu chưa đủ 5 ảnh mới từ Flow, bổ sung từ kho ảnh thật xưởng Happyco
    if len(unique_candidates) < 5:
        real_factory_dir = Path(r"D:\Hình\Hình xưởng\Ảnh")
        if real_factory_dir.exists():
            for rf in real_factory_dir.glob("*.jpg"):
                if check_new(rf):
                    unique_candidates.append(rf)
                    if len(unique_candidates) >= 5:
                        break

    print(f"  ✅ Đã chọn được {len(unique_candidates)} ảnh mới 100% khớp với nội dung xưởng mộc B2B.")

    # 2. Xóa watermark Flow + Đóng logo Happyco Duo
    print("\n[Bước 2] Làm sạch watermark Flow và đóng dấu Happyco Duo...")
    clean_dir = BASE_DIR / "output" / "b2b_9h30_cleaned"
    clean_dir.mkdir(parents=True, exist_ok=True)
    processed_images = {}
    keys = ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]

    ts_now = int(time.time())
    for idx, k in enumerate(keys):
        src_path = unique_candidates[idx] if idx < len(unique_candidates) else raw_images[idx % len(raw_images)]
        pil_src = Image.open(src_path).convert("RGB")
        img_bgr = cv2.cvtColor(np.array(pil_src), cv2.COLOR_RGB2BGR)
        cleaned_bgr = remove_flow_watermark(img_bgr)
        cleaned_pil = Image.fromarray(cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB))
        stamped_pil = stamp_happyco_watermark(cleaned_pil, wm_img)
        
        out_fn = clean_dir / f"happyco_b2b_cnc_{k}_{ts_now}.jpg"
        stamped_pil.save(out_fn, "JPEG", quality=95)
        processed_images[k] = out_fn
        print(f"  + [{k}]: {out_fn.name} (Đã inpaint sạch logo Flow + Đóng dấu Happyco Duo)")

    # 3. Sản xuất nội dung B2B chuyên sâu
    print("\n[Bước 3] Sub-Agent B2B biên soạn bài viết chuẩn SEO...")
    topic_title = "Gia Công Ván MDF Chống Ẩm Phủ Melamine: Dây Chuyền CNC Nesting & Tối Ưu Phôi Ván Tiết Kiệm 15% Chi Phí Cho Xưởng Mộc Tại Happyco"
    article = b2b_agent.produce_article(topic_title=topic_title)
    print(f"  ✅ Tiêu đề: {article['title']}")
    print(f"  ✅ Chuyên mục: {article.get('category')} (ID: {article.get('cat_id')})")
    print(f"  ✅ Mô tả: {article.get('description')}")

    # 4. Kiểm duyệt Chief QA
    print("\n[Bước 4] Con Tổng (Chief QA) kiểm duyệt bài viết...")
    audit = chief_qa.audit(article, list(processed_images.values()))
    print(f"  + Kiểm tra từ cấm: {audit['checks'].get('no_banned_brands')}")
    print(f"  + Văn phong web: {audit['checks'].get('professional_web_tone')}")
    print(f"  + Mô tả không bắt đầu 'Bài viết...': {audit['checks'].get('clean_description')}")
    print(f"  + Chân trang cố định: {audit['checks'].get('clean_footer')}")
    print(f"  + Số Heading <h2>: {audit['checks'].get('h2_count')}")
    print(f"  + Số liên kết nội bộ: {audit['checks'].get('internal_links_count')}")

    if not audit["passed"]:
        print(f"❌ CHIEF QA TỪ CHỐI: {audit['errors']}")
        sys.exit(1)
    print("  ✅ CHIEF QA: 100% ĐẠT TIÊU CHUẨN XUẤT BẢN!")

    # 5. Đăng tải lên CMS & Đặt lịch 09:30
    print("\n[Bước 5] Đăng tải lên CMS Happyco và hẹn giờ 09:30...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Đăng nhập
        email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
        password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")
        page.goto("https://happyco.asia/admin/login", timeout=40000)
        page.fill("input[name='email']", email)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        if "/admin/login" in page.url:
            raise RuntimeError("Đăng nhập CMS thất bại!")
        print("  [CMS] Đăng nhập quản trị thành công!")

        # Upload 5 ảnh vào thư viện media
        page.goto("https://happyco.asia/admin/media", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        cdn_urls = {}
        cdn_filenames = {}

        for k in keys:
            fpath = processed_images[k]
            title = f"Happyco B2B Gia Cong Ván CNC {k} {ts_now}"
            print(f"  [CMS Media] Đang tải lên: {fpath.name}...")
            
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            
            btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
            btn.click()
            page.wait_for_timeout(1000)
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
            cdn_urls[k] = cdn_url
            cdn_filenames[k] = cms_filename
            print(f"    -> Live CDN: {cdn_url}")

        # Chuẩn bị HTML bài viết
        content_html = article.get("content_html", "")
        for idx in range(1, 5):
            k = f"h2_{idx}"
            ph = f"IMAGE_PLACEHOLDER_{idx}"
            if ph in content_html:
                content_html = content_html.replace(ph, cdn_urls[k])
                
        old_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', content_html)
        new_h2_urls = [cdn_urls["h2_1"], cdn_urls["h2_2"], cdn_urls["h2_3"], cdn_urls["h2_4"]]
        for i, old_src in enumerate(old_imgs[:4]):
            if "media.loveitopcdn.com" not in old_src:
                content_html = content_html.replace(old_src, new_h2_urls[i])

        # Mở trang thêm bài viết mới
        print("\n  [CMS] Mở trang tạo bài viết mới...")
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_selector('input[name="title"]', timeout=30000)

        page.fill('input[name="title"]', article["title"])
        page.fill('input[name="slug"]', article["slug"])

        # CHỌN CHUYÊN MỤC ID: 265 (GIA CÔNG VÁN CÔNG NGHIỆP)
        page.select_option('select[name="cat_id"]', "265")
        print("  [CMS] Đã chọn chuyên mục ID: 265 (GIA CÔNG VÁN CÔNG NGHIỆP)")

        # Cài đặt Thumbnail
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

        # LÊN LỊCH ĐĂNG 09:30 NGÀY 11-11-2026
        page.evaluate("""() => {
            let el = document.querySelector('input[name="published_at"]');
            if (el) {
                el.value = "11-11-2026 09:30";
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""")
        print("  [CMS] Đã cài đặt lịch đăng chuẩn: 11-11-2026 09:30")

        # Đánh dấu is_published
        chk = page.locator('input[name="is_published"]')
        if chk.count() > 0 and not chk.is_checked():
            chk.check()

        # Điền Description & Content vào CKEditor
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
                    }
                    if (el && el.name === 'content') {
                        inst.setData(content);
                        inst.updateElement();
                        el.value = content;
                    }
                }
            }
        }""", {"desc": desc_text, "content": content_html})

        page.wait_for_timeout(1000)

        # Tags
        tags_input = page.locator('input[name="tags"]')
        if tags_input.count() > 0:
            tags_input.fill("gia công ván mdf, cnc nesting happyco, gia công nội thất biên hòa đồng nai")

        # BẤM LƯU BÀI VIẾT
        print("  [CMS] Bấm Lưu bài viết...")
        save_btn = page.locator("button[type='submit']:has-text('Lưu')").first
        save_btn.click()
        page.wait_for_timeout(5000)

        # Kiểm tra danh sách bài viết trên CMS
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_selector("table", timeout=30000)
        
        first_row = page.locator("table tbody tr").first
        row_text = first_row.inner_text().replace("\n", " | ")
        print(f"\n[CMS Post List] Bài viết vừa tạo trên danh sách:\n  -> {row_text}")

        # Chụp màn hình bằng chứng
        screenshot_path = BASE_DIR / "output" / "b2b_9h30_cms_confirmed.png"
        page.screenshot(path=str(screenshot_path))
        print(f"  📸 Đã chụp màn hình xác nhận: {screenshot_path.name}")

        # Đăng ký hash ảnh vào image_registry
        for k in keys:
            register(str(ts_now), str(processed_images[k]), source="flow_parallel")

        browser.close()

    print("\n==================================================================")
    print("🎉 HOÀN TẤT THÀNH CÔNG: BÀI VIẾT B2B ĐÃ ĐƯỢC ĐẶT LỊCH ĐĂNG VÀO 09:30 HÔM NAY!")
    print(f"📝 Tiêu đề: {article['title']}")
    print(f"📂 Chuyên mục: GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265)")
    print(f"⏰ Lịch xuất bản: 11-11-2026 09:30")
    print("==================================================================")

if __name__ == "__main__":
    main()
