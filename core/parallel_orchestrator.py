"""
Happyco Parallel Zero-Latency Orchestrator
Đột phá tối ưu hóa tốc độ xuất bản:
1. Phase 1 (Outline & Prompts): Agent lên dàn ý (Title, 4 H2, 5 câu Prompt tiếng Anh cực nét).
2. Phase 2 (Song song / Parallel):
   - Thread A (Background): Bơm dồn 5 Prompt vào Google Flow qua CDP trong 15s, Flow tự động vẽ trên Cloud.
   - Thread B (Main): Sub-Agent (B2B hoặc B2C) viết chi tiết toàn bộ thân bài, bảng kỹ thuật, liên kết nội bộ.
3. Phase 3 (Sync & Clean):
   - Đón 5 ảnh từ Flow về máy, loại bỏ ảnh trùng (image_registry).
   - Tự động Inpaint xóa 100% dấu sao watermark của Flow.
   - Đóng logo Happyco Duo trong suốt (alpha blend).
4. Phase 4 (QA & Publish):
   - Con Tổng (Chief QA) duyệt nghiêm ngặt: Không từ cấm, không văn phong FB, hotline & địa chỉ xưởng cố định.
   - Publisher Bot tự động upload CDN và đưa vào CMS Happyco.
"""

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

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from core.image_registry import check_new, register
from agents.chief_qa_agent import ChiefQAAgent
from agents.b2b_woodworking_agent import B2BWoodworkingAgent
from agents.b2c_interior_agent import B2CInteriorAgent

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
    from playwright.sync_api import sync_playwright
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
            
            submit_btn = page.locator("button:has-text('keyboard_return'), button[aria-label*='Generate'], button[aria-label*='Send'], button:has-text('arrow_upward')").first
            if submit_btn.is_visible():
                submit_btn.click()
            else:
                box.press("Enter")
                
            page.wait_for_timeout(1500)
            
        print(f"  🎉 [Flow Worker] Đã bơm xong toàn bộ prompt trong {time.time() - start_time:.1f}s! Đang render ngầm...")

def flow_download_recent_images(out_dir, min_images=5, cdp_url="http://127.0.0.1:9333", wait_seconds=60):
    """Chờ Flow render xong và tải nhanh qua Canvas base64"""
    from playwright.sync_api import sync_playwright
    print(f"\n[Parallel Image Harvester] Đang chờ Google Flow hoàn tất ({wait_seconds}s)...")
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
                fn = out_dir / f"flow_raw_{item['index']}_{ts}.jpg"
                with open(fn, "wb") as f:
                    f.write(buf)
                saved_files.append(fn)
                
        print(f"  ✅ [Parallel Image Harvester] Đã tải về {len(saved_files)} ảnh chất lượng cao.")
        return saved_files

class ParallelPublishingPipeline:
    def __init__(self):
        self.chief_qa = ChiefQAAgent()
        self.b2b_agent = B2BWoodworkingAgent()
        self.b2c_agent = B2CInteriorAgent()
        self.wm_img = Image.open(WM_PATH).convert("RGBA") if WM_PATH.exists() else None

    def execute_parallel_workflow(self, topic: str, category_id: int, schedule_time: str = None):
        print("==================================================================")
        print("🚀 KHỞI ĐỘNG PARALLEL ZERO-LATENCY PIPELINE (CHẠY SONG SONG 100%)")
        print(f"📌 Chủ đề: {topic}")
        print(f"📂 Phân loại danh mục: ID {category_id}")
        print(f"⏰ Lịch đăng: {schedule_time if schedule_time else 'Đăng ngay lập tức'}")
        print("==================================================================")
        
        is_b2b = (category_id == 265)
        active_agent = self.b2b_agent if is_b2b else self.b2c_agent
        
        # 1. BƯỚC 1: Lên khung H2 và 5 Prompt ảnh chuẩn xác
        print("\n[Phase 1] Lên dàn bài H2 và sinh 5 Prompts ảnh kiến trúc/xưởng...")
        plan = active_agent.plan_outline_and_prompts(topic)
        print(f"  ✅ Tiêu đề: {plan['title']}")
        print(f"  ✅ 5 Prompts tạo ảnh đã sẵn sàng!")
        
        # 2. BƯỚC 2: CHẠY SONG SONG
        # - Thread 1: Bắn 5 prompt vào Google Flow
        # - Thread 2: Agent viết bài chi tiết (văn bản, bảng, liên kết)
        print("\n[Phase 2] KÍCH HOẠT SONG SONG (PARALLEL EXECUTION)...")
        print("  ⚡ Thread A: Bơm 5 Prompt sang Google Flow để render ngầm...")
        print("  📝 Thread B: Agent nội dung bắt đầu viết chi tiết toàn bài...")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            flow_future = executor.submit(flow_batch_inject, plan["prompts"])
            article_future = executor.submit(active_agent.write_full_article_from_plan, plan)
            
            # Chờ cả 2 hoàn tất
            flow_future.result()
            article_data = article_future.result()
            
        print("  ✅ [Phase 2 Done] Nội dung bài viết đã hoàn tất và Flow đang chuẩn bị xong ảnh!")
        
        # 3. BƯỚC 3: Thu hoạch ảnh, xóa watermark Flow, đóng logo Happyco
        print("\n[Phase 3] Thu hoạch ảnh Flow & Xử lý tự động...")
        temp_flow_dir = BASE_DIR / "output" / "parallel_flow_temp"
        raw_images = flow_download_recent_images(temp_flow_dir, min_images=5, wait_seconds=45)
        
        # Lọc ảnh mới 100%
        unique_images = []
        for f in raw_images:
            if check_new(f):
                unique_images.append(f)
                if len(unique_images) >= 5:
                    break
                    
        # Inpaint xóa dấu Flow + Đóng dấu logo
        processed_images = {}
        keys = ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]
        output_clean_dir = BASE_DIR / "output" / "parallel_clean_assets"
        output_clean_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, key in enumerate(keys):
            raw_path = unique_images[idx] if idx < len(unique_images) else raw_images[idx % len(raw_images)]
            img_bgr = cv2.imread(str(raw_path))
            cleaned_bgr = remove_flow_watermark(img_bgr)
            
            cleaned_pil = Image.fromarray(cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB))
            if self.wm_img:
                final_pil = stamp_happyco_watermark(cleaned_pil, self.wm_img)
            else:
                final_pil = cleaned_pil
                
            clean_name = f"happyco_parallel_{key}_{int(time.time())}.jpg"
            save_path = output_clean_dir / clean_name
            final_pil.save(save_path, "JPEG", quality=95)
            processed_images[key] = save_path
            print(f"  + [{key}]: {save_path.name} (Đã xóa logo Flow + Đóng dấu Happyco Duo)")
            
        # 4. BƯỚC 4: Kiểm duyệt Chief QA
        print("\n[Phase 4] Kiểm duyệt Chief QA chuẩn bị xuất bản...")
        audit = self.chief_qa.audit(article_data, list(processed_images.values()))
        if not audit["passed"]:
            print(f"  ❌ Lỗi QA: {audit['errors']}")
            raise ValueError("Không vượt qua kiểm duyệt QA!")
        print("  ✅ 100% TIÊU CHUẨN KIỂM DUYỆT ĐẠT CHUẨN!")
        
        # 5. BƯỚC 5: Xuất bản vào CMS
        print("\n[Phase 5] Đăng tải lên CMS Happyco...")
        from publisher import publish_post
        result = publish_post(article_data, processed_images, publish_mode="publish", artifacts_dir=output_clean_dir)
        print("🎉 XUẤT BẢN THÀNH CÔNG VỚI QUY TRÌNH SONG SONG ZERO-LATENCY!")
        return result
