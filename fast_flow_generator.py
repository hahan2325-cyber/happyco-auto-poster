"""
Fast Flow Generator - Module tạo 5 ảnh song song bằng Google Flow trong 60 giây
Đã tích hợp quy chuẩn Happyco:
- Tỷ lệ 16:9 chuẩn
- Watermark Happyco Duo trong suốt ở GÓC TRÊN BÊN TRÁI (35, 35)
- Thu hoạch ảnh trực tiếp bằng Canvas toDataURL (không click chuột thủ công)
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
    """Xóa triệt để logo/ngôi sao mờ của Google Flow ở góc dưới bên phải bằng Inpainting"""
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

def generate_flow_batch_parallel(prompts, output_dir=None):
    """
    Bơm liên tiếp toàn bộ prompts vào Google Flow qua CDP 9333.
    Chờ Flow vẽ song song và hút ảnh bằng Canvas.
    Đóng dấu Top-Left và trả về danh sách file ảnh hoàn thiện.
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
        
        # 1. Bơm liên tiếp tất cả prompts vào input box (Queue nhanh)
        for idx, prompt_text in enumerate(prompts, 1):
            box = page.locator("textarea").first
            if not box.is_visible():
                box = page.locator("[role='textbox']").first
            if not box.is_visible():
                box = page.locator("[contenteditable='true']").first
                
            box.click()
            page.wait_for_timeout(200)
            box.fill(prompt_text)
            page.wait_for_timeout(300)
            box.press("Enter")
            print(f"  [+] Đã bắn Prompt {idx}/{len(prompts)} bằng phím Enter!")
            page.wait_for_timeout(1000)
            
        print(f"⏳ Toàn bộ {len(prompts)} prompt đã gửi xong trong {int(time.time() - start_time)}s. Đang chờ Flow vẽ ngầm song song...")
        
        # 2. Chờ 40 giây để Flow vẽ song song cả 5 bức ảnh
        time.sleep(38)
        
        # 3. Thu hoạch toàn bộ ảnh qua Canvas toDataURL
        print("⚡ Đang hút dữ liệu ảnh từ Canvas...")
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
                    results.push({
                        index: i,
                        dataUrl: canvas.toDataURL('image/jpeg', 0.95)
                    });
                } catch (e) {}
            }
            return results;
        }''')
        
        browser.close()
        
    print(f"✅ Đã hút được {len(images_data)} ảnh chất lượng cao.")
    
    # Lấy các ảnh mới nhất tương ứng với số prompts
    # Đóng dấu Top-Left và lưu
    final_files = []
    # Ưu tiên lấy các ảnh ở cuối danh sách (ảnh vừa sinh)
    recent_images = images_data[-len(prompts):] if len(images_data) >= len(prompts) else images_data
    
    for idx, item in enumerate(recent_images):
        data = item["dataUrl"].split(",")[1]
        buf = base64.b64decode(data)
        raw_path = output_dir / f"raw_flow_{idx}.jpg"
        with open(raw_path, "wb") as f:
            f.write(buf)
            
        # 1. Xóa sạch logo ngôi sao mờ của Google Flow ở góc dưới phải
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
        final_path = output_dir / f"final_topleft_img_{idx + 1}.jpg"
        stamped.save(final_path, "JPEG", quality=95)
        final_files.append(final_path)
        print(f"  [TopLeft Stamp] Hoàn thành ảnh {idx + 1}: {final_path.name}")
        
    total_time = int(time.time() - start_time)
    print(f"\n🎉 HOÀN TẤT TẠO {len(final_files)} ẢNH FLOW TRONG TỔNG THỜI GIAN: {total_time} GIÂY!")
    return final_files

if __name__ == "__main__":
    test_prompts = [
        "Spacious modern luxury open-concept kitchen, dark anodized aluminum glass cabinets, marble waterfall island, 16:9, no people",
        "Modern luxury kitchen interior with sleek dark anodized aluminum glass upper cabinets, warm internal led illumination, 16:9, no people",
        "Modern luxury kitchen island combined with minimalist wooden dining table, marble countertop, 16:9, no people",
        "Modern elegant kitchen cabinetry with softly rounded curved corner edges, matte warm grey finish, 16:9, no people",
        "Clean modern architectural photo of premium customized kitchen cabinet system with built-in appliances, seamless PUR edge banding, 16:9, no people"
    ]
    files = generate_flow_batch_parallel(test_prompts)
    print("Files produced:", [str(f) for f in files])
