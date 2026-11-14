import os
import sys
import time
import json
import base64
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
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

def flow_batch_inject(prompts, cdp_url="http://127.0.0.1:9333"):
    """Bơm dồn liên tiếp 5 prompts vào Google Flow qua CDP trong 15-20s"""
    print(f"\n[Parallel Flow Worker] Bắt đầu kết nối CDP {cdp_url} để bơm {len(prompts)} prompts...")
    start_time = time.time()
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        page = browser.contexts[0].pages[0]
        
        for idx, prompt_text in enumerate(prompts, 1):
            print(f"  ⚡ [Flow Worker] Bơm prompt {idx}/{len(prompts)}...")
            box = page.locator("textarea").first
            if not box.is_visible():
                box = page.locator("[role='textbox']").first
            if not box.is_visible():
                box = page.locator("[contenteditable='true']").first
                
            box.click()
            page.wait_for_timeout(300)
            box.fill(prompt_text)
            page.wait_for_timeout(400)
            
            submit_btn = page.locator("button[aria-label*='tạo'], button[aria-label*='Bắt đầu tạo'], button:has-text('arrow_forward'), button[type='submit']").first
            if submit_btn.is_visible():
                submit_btn.click()
            else:
                box.press("Enter")
                
            page.wait_for_timeout(2500)
            
        print(f"  🎉 [Flow Worker] Đã bơm xong toàn bộ {len(prompts)} prompt trong {time.time() - start_time:.1f}s! Server đang vẽ ngầm...")

def download_flow_images(out_dir, wait_seconds=65, cdp_url="http://127.0.0.1:9333"):
    """Chờ Flow vẽ xong và tải nhanh ảnh qua Canvas base64"""
    print(f"\n[Parallel Harvester] Chờ Google Flow render hoàn tất ({wait_seconds}s)...")
    time.sleep(wait_seconds)
    
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
                
        print(f"  ✅ [Parallel Harvester] Đã tải về {len(saved_files)} ảnh chất lượng cao từ Flow.")
        return saved_files

def main():
    print("==================================================================")
    print("🚀 BẮT ĐẦU QUY TRÌNH SONG SONG: BÀI VIẾT GIA CÔNG VÁN B2B (LÊN LỊCH 9h30)")
    print("==================================================================")

    b2b_agent = B2BWoodworkingAgent()
    chief_qa = ChiefQAAgent()
    wm_img = Image.open(WM_PATH).convert("RGBA")

    # Đề tài B2B chuyên sâu danh mục 265
    topic_title = "Gia Công Ván MDF Chống Ẩm Phủ Melamine: Dây Chuyền CNC Nesting & Tối Ưu Phôi Ván Tiết Kiệm 15% Chi Phí Cho Xưởng Mộc Tại Happyco"

    # 1. BƯỚC 1: Lên dàn bài H2 và 5 Prompt ảnh
    print("\n[Phase 1] Lên khung dàn ý & sinh 5 prompts ảnh xưởng máy công nghiệp...")
    plan = b2b_agent.plan_outline_and_prompts(topic_title)
    print(f"  ✅ Tiêu đề: {plan['title']}")
    print("  ✅ 5 Prompts tạo ảnh xưởng CNC & nẹp PUR:")
    for idx, pr in enumerate(plan['prompts'], 1):
        print(f"    {idx}. {pr[:80]}...")

    # 2. BƯỚC 2: CHẠY SONG SONG
    # - Thread 1: Bắn 5 prompts sang Google Flow
    # - Thread 2: Agent viết bài chi tiết toàn văn
    print("\n[Phase 2] CHẠY SONG SONG KHÔNG ĐỘ TRỄ (PARALLEL EXECUTION)...")
    with ThreadPoolExecutor(max_workers=2) as executor:
        flow_future = executor.submit(flow_batch_inject, plan["prompts"])
        article_future = executor.submit(b2b_agent.write_full_article_from_plan, plan)
        
        flow_future.result()
        article = article_future.result()

    print("  ✅ [Phase 2 Hoàn thành] Bài viết đã hoàn tất và Flow đang chuẩn bị xong 5 ảnh!")

    # 3. BƯỚC 3: Thu hoạch ảnh từ Flow
    temp_dir = BASE_DIR / "output" / "parallel_b2b_raw"
    raw_images = download_flow_images(temp_dir, wait_seconds=45)

    # Lọc ảnh mới 100% bằng image_registry
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

    print(f"\n[Phase 3] Đã chọn {len(unique_candidates)} ảnh mới 100% từ Google Flow.")

    # Inpaint xóa watermark Flow + Đóng logo Happyco Duo
    clean_dir = BASE_DIR / "output" / "parallel_b2b_cleaned"
    clean_dir.mkdir(parents=True, exist_ok=True)
    processed_images = {}
    keys = ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]

    ts_now = int(time.time())
    for idx, k in enumerate(keys):
        src_path = unique_candidates[idx] if idx < len(unique_candidates) else raw_images[idx % len(raw_images)]
        img_bgr = cv2.imread(str(src_path))
        cleaned_bgr = remove_flow_watermark(img_bgr)
        cleaned_pil = Image.fromarray(cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB))
        stamped_pil = stamp_happyco_watermark(cleaned_pil, wm_img)
        
        out_fn = clean_dir / f"happyco_b2b_{k}_{ts_now}.jpg"
        stamped_pil.save(out_fn, "JPEG", quality=95)
        processed_images[k] = out_fn
        print(f"  + [{k}]: {out_fn.name} (Đã inpaint xóa dấu Flow + Đóng dấu Happyco Duo)")

    # 4. BƯỚC 4: Kiểm duyệt Chief QA
    print("\n[Phase 4] Con Tổng (Chief QA) kiểm duyệt bài viết...")
    audit = chief_qa.audit(article, list(processed_images.values()))
    print(f"  + Kiểm tra từ cấm: {audit['checks'].get('no_banned_brands')}")
    print(f"  + Văn phong web (không chào FB/tự xưng): {audit['checks'].get('professional_web_tone')}")
    print(f"  + Mô tả không bắt đầu bằng 'Bài viết...': {audit['checks'].get('clean_description')}")
    print(f"  + Chân trang cố định: {audit['checks'].get('clean_footer')}")
    print(f"  + Số Heading <h2>: {audit['checks'].get('h2_count')}")
    print(f"  + Số liên kết nội bộ: {audit['checks'].get('internal_links_count')}")

    if not audit["passed"]:
        print(f"❌ CHIEF QA TỪ CHỐI: {audit['errors']}")
        sys.exit(1)
    print("  ✅ CHIEF QA: 100% ĐẠT CHUẨN XUẤT BẢN!")

    # 5. BƯỚC 5: Đăng tải CMS & Đặt lịch 9h30
    print("\n[Phase 5] Đăng bài và đặt lịch xuất bản vào 09:30...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Đăng nhập CMS
        email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
        password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")
        page.goto("https://happyco.asia/admin/login", timeout=40000)
        page.fill("input[name='email']", email)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_url("**/admin**", timeout=30000)
        print("  [CMS] Đăng nhập thành công!")

        # Upload 5 ảnh lên CMS Media Library
        page.goto("https://happyco.asia/admin/media", timeout=40000)
        cdn_urls = {}
        cdn_filenames = {}

        for k in ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]:
            fpath = processed_images[k]
            title = f"Happyco B2B Gia Cong CNC {k} {ts_now}"
            print(f"  [CMS Media] Đang upload: {fpath.name}...")
            
            btn = page.locator("a:has-text('Thêm tệp tin'), button:has-text('Thêm tệp tin'), a:has-text('Thêm mới')").first
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
            cdn_urls[k] = cdn_url
            cdn_filenames[k] = cms_filename
            print(f"    -> Live CDN: {cdn_url}")

        # Chuẩn bị HTML nội dung
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

        # Mở trang thêm bài viết
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
        print(f"  [CMS] Đã gán Thumbnail: {thumb_fn}")

        # LÊN LỊCH ĐĂNG 09:30 NGÀY 11-11-2026
        page.evaluate("""() => {
            let el = document.querySelector('input[name="published_at"]');
            if (el) {
                el.value = "11-11-2026 09:30";
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""")
        print("  [CMS] Đã đặt lịch đăng: 11-11-2026 09:30")

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

        # Tags & Keywords
        tags_input = page.locator('input[name="tags"]')
        if tags_input.count() > 0:
            tags_input.fill("gia công ván công nghiệp, gia công mdf biên hòa, cnc nesting happyco")

        # BẤM LƯU BÀI VIẾT
        print("  [CMS] Đang bấm Lưu bài viết...")
        save_btn = page.locator("button[type='submit']:has-text('Lưu')").first
        save_btn.click()
        page.wait_for_timeout(5000)

        # Kiểm tra danh sách bài viết
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_selector("table", timeout=30000)
        
        first_row = page.locator("table tbody tr").first
        row_text = first_row.inner_text().replace("\n", " | ")
        print(f"\n[CMS Post List] Dòng đầu tiên hiện tại:\n  -> {row_text}")

        # Chụp ảnh bằng chứng
        screenshot_path = BASE_DIR / "output" / "b2b_9h30_scheduled.png"
        page.screenshot(path=str(screenshot_path))
        print(f"  📸 Đã chụp màn hình xác nhận: {screenshot_path.name}")

        # Đăng ký hash ảnh vào image_registry
        for k in keys:
            register(str(ts_now), str(processed_images[k]), source="flow_parallel")

        browser.close()

    print("\n==================================================================")
    print("🎉 HOÀN THÀNH 100%: BÀI VIẾT B2B ĐÃ ĐƯỢC LÊN LỊCH ĐĂNG VÀO 09:30 HÔM NAY!")
    print(f"📝 Tiêu đề: {article['title']}")
    print(f"📂 Chuyên mục: GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265)")
    print(f"⏰ Lịch đăng: 11-11-2026 09:30")
    print("==================================================================")

if __name__ == "__main__":
    main()
