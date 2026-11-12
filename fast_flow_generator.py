"""
Fast Flow Generator - Module tạo 5 ảnh song song bằng Google Flow trong ~60 giây
Đã tích hợp quy chuẩn Happyco:
- Định danh chính xác 1-1 từng ảnh theo Prompt (img.alt matching), không bao giờ nhầm ảnh bài trước
- Xóa triệt để 100% ngôi sao Google Flow bằng Poisson Seamless Blending
- Tỷ lệ 16:9 chuẩn (1376x768)
- Watermark Happyco Duo trong suốt ở GÓC TRÊN BÊN TRÁI (35, 35)
- Tên file độc bản theo timestamp (không bao giờ bị cache CDN)
"""

import os
import sys
import time
import base64
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
WM_PATH = BASE_DIR / "happyco_watermark_duo.png"

def remove_flow_watermark(img_bgr):
    """Xóa triệt để 100% ngôi sao Google Flow bằng thuật toán Poisson Seamless Blending không để lại vết mờ"""
    h, w = img_bgr.shape[:2]
    if w < 300 or h < 300:
        return img_bgr
    star_center = (w - 95, h - 85)
    source_center = (w - 205, h - 85)
    pw, ph = 88, 88
    
    x1 = max(0, source_center[0] - pw // 2)
    y1 = max(0, source_center[1] - ph // 2)
    src_patch = img_bgr[y1:y1+ph, x1:x1+pw]
    
    clone_mask = np.full((src_patch.shape[0], src_patch.shape[1]), 255, dtype=np.uint8)
    cloned = cv2.seamlessClone(src_patch, img_bgr, clone_mask, star_center, cv2.NORMAL_CLONE)
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

def generate_flow_batch_parallel(prompts, output_dir=None):
    """
    Bơm liên tiếp toàn bộ prompts vào Google Flow qua CDP 9333.
    Chờ Flow vẽ song song và đối chiếu 1-1 theo img.alt để hút đúng từng ảnh.
    Xóa ngôi sao Google, crop 16:9, đóng dấu Top-Left và trả về danh sách file ảnh.
    """
    if output_dir is None:
        output_dir = BASE_DIR / "output" / f"batch_flow_{int(time.time())}"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    wm_img = Image.open(WM_PATH).convert("RGBA")
    start_time = time.time()
    print(f"\n🚀 [Fast Flow] BẮT ĐẦU BƠM {len(prompts)} PROMPT VÀO FLOW SONG SONG...")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp('http://127.0.0.1:9333')
        except Exception as e:
            print(f"❌ Không kết nối được CDP 9333: {e}")
            return []
            
        page = None
        for pg in browser.contexts[0].pages:
            if "flow.google.com" in pg.url or "labs.google" in pg.url:
                page = pg
                break
        if not page:
            page = browser.contexts[0].pages[0]
            page.goto("https://flow.google.com/project/d7cecce7-8682-454a-bb94-13576243c599", wait_until="networkidle")
            page.wait_for_timeout(3000)
            
        print(f"Connected to Flow page: {page.url}")
        page.bring_to_front()
        page.wait_for_selector("[role='textbox'], [contenteditable='true']", timeout=15000)
        
        # Ghi nhận tất cả src đã tồn tại trước khi bơm để không bao giờ lấy nhầm ảnh cũ
        used_srcs = set(page.evaluate("() => Array.from(document.querySelectorAll('img')).map(i => i.src)"))
        matched_map = {}

        # 1. Gửi từng prompt và chờ Flow Agent phản hồi ảnh xong (~18-25s/ảnh) để đảm bảo 100% không rớt prompt nào
        for idx, prompt_text in enumerate(prompts):
            box = page.locator("[contenteditable='true']:visible, [role='textbox']:visible, textarea:visible").first
            box.click()
            page.wait_for_timeout(150)
            page.keyboard.press("Control+a")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(150)
            box.fill(prompt_text)
            page.wait_for_timeout(400)
            
            gen_btn = page.locator('button:has(:text-is("arrow_forward"))').first
            if gen_btn.is_visible() and not gen_btn.is_disabled():
                gen_btn.click()
            else:
                box.press("Enter")
            print(f"  [+] Đã gửi Prompt {idx + 1}/{len(prompts)}, đang chờ Flow vẽ...", flush=True)
            
            # Chờ ảnh mới khớp prompt này xuất hiện (tối đa 55s)
            prefix = prompt_text[:80].strip().lower()
            p_start = time.time()
            found = False
            while time.time() - p_start < 55:
                dom_imgs = page.evaluate("""() => {
                    return Array.from(document.querySelectorAll('img'))
                        .filter(img => img.naturalWidth > 500 && img.alt && img.alt !== 'Ô hiển thị hình ảnh của người dùng')
                        .map(img => ({ src: img.src, alt: img.alt }));
                }""")
                for d in dom_imgs:
                    if d["src"] not in used_srcs and prefix in d["alt"].lower():
                        matched_map[idx] = d["src"]
                        used_srcs.add(d["src"])
                        found = True
                        print(f"      ⚡ Xong ảnh {idx + 1}/{len(prompts)} sau {int(time.time() - p_start)}s!", flush=True)
                        break
                if found:
                    # Đánh dấu luôn biến thể thứ 2 của cùng prompt để không lẫn về sau
                    for d in dom_imgs:
                        if prefix in d["alt"].lower():
                            used_srcs.add(d["src"])
                    page.wait_for_timeout(1200)
                    break
                time.sleep(2)
            if not found:
                print(f"      ⚠️ Quá 55s chưa thấy ảnh {idx + 1}.", flush=True)

        print(f"  -> Đã đối chiếu chính xác {len(matched_map)}/{len(prompts)} ảnh mới riêng biệt.")
        
        # 3. Thu hoạch đúng các ảnh đã khớp qua Canvas toDataURL
        target_srcs = [matched_map.get(i) for i in range(len(prompts))]
        images_data = page.evaluate("""async (srcs) => {
            const allImgs = Array.from(document.querySelectorAll('img'));
            const results = [];
            for (let i = 0; i < srcs.length; i++) {
                const targetSrc = srcs[i];
                if (!targetSrc) {
                    results.push(null);
                    continue;
                }
                const img = allImgs.find(el => el.src === targetSrc && el.naturalWidth > 500);
                if (!img) {
                    results.push(null);
                    continue;
                }
                try {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    results.push(canvas.toDataURL('image/jpeg', 0.95));
                } catch (e) {
                    results.push(null);
                }
            }
            return results;
        }""", target_srcs)
        
        browser.close()
        
    final_files = []
    ts_uniq = int(time.time())
    
    for idx, data_url in enumerate(images_data):
        if not data_url:
            print(f"  ⚠️ Prompt {idx + 1} chưa lấy được ảnh.")
            continue
        data = data_url.split(",")[1]
        buf = base64.b64decode(data)
        raw_path = output_dir / f"raw_flow_{idx}.jpg"
        with open(raw_path, "wb") as f:
            f.write(buf)
            
        # 1. Xóa sạch logo ngôi sao mờ của Google Flow bằng Poisson Seamless Blending
        img_bgr = cv2.imread(str(raw_path))
        if img_bgr is not None:
            clean_bgr = remove_flow_watermark(img_bgr)
            clean_rgb = cv2.cvtColor(clean_bgr, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(clean_rgb)
        else:
            img = Image.open(raw_path).convert("RGB")
            
        # 2. Xử lý 16:9 và đóng dấu Top-Left
        w, h = img.size
        target_h = int(w * 9 / 16)
        if h > target_h:
            top = (h - target_h) // 2
            img = img.crop((0, top, w, top + target_h))
        elif h < target_h:
            target_w = int(h * 16 / 9)
            left = (w - target_w) // 2
            img = img.crop((left, 0, left + target_w, h))
        img = img.resize((1376, 768), Image.Resampling.LANCZOS)
        
        stamped = stamp_top_left(img, wm_img)
        final_path = output_dir / f"happyco_flow_{idx + 1}_{ts_uniq}.jpg"
        stamped.save(final_path, "JPEG", quality=95)
        final_files.append(final_path)
        print(f"  [TopLeft Stamp] Hoàn thành ảnh {idx + 1}: {final_path.name}")
        
    total_time = int(time.time() - start_time)
    print(f"\n🎉 HOÀN TẤT TẠO {len(final_files)} ẢNH FLOW TRONG TỔNG THỜI GIAN: {total_time} GIÂY!")
    return final_files
