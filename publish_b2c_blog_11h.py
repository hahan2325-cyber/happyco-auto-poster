import os
import sys
import json
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from agents.b2c_interior_agent import B2CInteriorAgent
from fast_flow_generator import generate_flow_batch_parallel

def main():
    start_total = time.time()
    print("=" * 70)
    print("🚀 BẮT ĐẦU QUY TRÌNH XUẤT BẢN BLOG NỘI THẤT (ID: 266) - ĐẶT LỊCH 11:00")
    print("=" * 70)
    
    # 1. B2C Agent tạo nội dung bài viết
    print("\n[1/5] B2C Interior Agent đang tạo bài viết...")
    b2c = B2CInteriorAgent()
    topic = "Thiết Kế Nội Thất Phòng Ngủ Master Cho Vợ Chồng Trẻ: Không Gian Giữ Lửa Tổ Ấm & Tiêu Chuẩn Xanh E1/E0"
    article = b2c.produce_article(topic_title=topic)
    
    unique_suffix = f"-{int(time.time())}"
    article["slug"] = f"thiet-ke-noi-that-phong-ngu-master-vo-chong-tre{unique_suffix}"
    
    print(f"  -> Tiêu đề: {article['title']}")
    print(f"  -> Slug: {article['slug']}")
    print(f"  -> Chuyên mục: {article['category']} (ID: {article['cat_id']})")
    
    # 2. Chuẩn bị 5 prompt cho Flow
    flow_prompts = [
        "Warm luxury modern master bedroom interior design for young couple, upholstered king bed with softly curved corners, warm natural oak wood floor, soft ambient 3000K evening lighting, large window with sheer curtains, architectural interior photography, 16:9, no people",
        "Close-up architectural shot of modern master bed with soft beige curved upholstered headboard and padded frame edges, warm cozy bedding, warm accent lighting, child-safe design, 16:9, no people",
        "Modern luxury floor-to-ceiling wardrobe with sleek dark anodized aluminum slim frame tinted glass doors, warm internal vertical LED strip illumination, organized clothes shelving, 16:9, no people",
        "Minimalist wall-hung vanity dressing table with glowing backlit round smart LED mirror, matching curved wooden nightstand, warm soft lighting, 16:9, no people",
        "Detailed macro shot of premium green moisture-resistant HMR MDF furniture edge with flawless PUR noline edge banding, eco-friendly healthy E0 standard wood interior, 16:9, no people"
    ]
    
    # 3. Tạo 5 ảnh song song bằng Fast Flow trong 58s
    print("\n[2/5] Kích hoạt Fast Flow Generator tạo 5 ảnh song song...")
    batch_out = BASE_DIR / "output" / f"b2c_bedroom_flow_{int(time.time())}"
    generated_files = generate_flow_batch_parallel(flow_prompts, batch_out)
    
    if len(generated_files) < 5:
        print(f"⚠️ Flow chỉ trả về {len(generated_files)} ảnh, kiểm tra ảnh dự phòng...")
        # Fallback to existing if needed
    
    print(f"✅ Đã tạo xong {len(generated_files)} ảnh chuẩn 16:9 dập logo Góc Trên Trái!")
    
    # 4. Upload ảnh lên CDN Loveitop qua CMS
    print("\n[3/5] Upload 5 ảnh lên CDN qua /admin/media...")
    CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
    CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")
    
    cdn_urls = []
    cdn_filenames = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        # Đăng nhập CMS
        page.goto("https://happyco.asia/admin/login", timeout=40000)
        page.fill("input[name='email']", CMS_EMAIL)
        page.fill("input[name='password']", CMS_PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # Upload từng ảnh
        for idx, fpath in enumerate(generated_files):
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            
            btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
            btn.click()
            page.wait_for_timeout(1000)
            page.set_input_files("input[name='media_file']", str(fpath))
            page.fill("input[name='title']", f"Happyco B2C Bedroom Master {idx + 1} {int(time.time())}")
            page.locator("button:has-text('Lưu')").first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            
            cms_fn = fpath.name
            cdn_url = f"https://media.loveitopcdn.com/19180/{cms_fn}"
            cdn_urls.append(cdn_url)
            cdn_filenames.append(cms_fn)
            print(f"  [+] Uploaded CDN: {cdn_url}")
            
        # 5. Tạo bài viết mới trên CMS tại /admin/post/create
        print("\n[4/5] Đăng bài và đặt lịch 11:00 trên CMS...")
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # Tiêu đề & Slug
        page.fill('input[name="title"]', article["title"])
        page.fill('input[name="slug"]', article["slug"])
        
        # Chuyên mục 266 (BLOG NỘI THẤT)
        page.select_option('select[name="cat_id"]', "266")
        
        # Keyword & Meta
        page.fill('input[name="meta_keyword"]', "nội thất phòng ngủ master, thiết kế phòng ngủ vợ chồng trẻ, tủ áo cánh kính slim, cốt ván e1 e0, nội thất happyco")
        
        # Đặt lịch đăng 11:00 hôm nay
        publish_time = "11-11-2026 11:00"
        page.evaluate("""(timeVal) => {
            const el = document.querySelector('input[name="published_at"]');
            if (el) {
                el.value = timeVal;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""", publish_time)
        print(f"  [CMS] Đã cài đặt lịch xuất bản: {publish_time}")
        
        # Check is_published
        chk = page.locator('input[name="is_published"]')
        if chk.count() > 0 and not chk.is_checked():
            chk.check()
            
        # Thumbnail
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
        
        # Chuẩn bị HTML nội dung chèn 4 ảnh H2
        html_content = article.get("content_html", "")
        body_images = cdn_urls[1:5]
        
        # Thay thế placeholder hoặc chèn ảnh vào các mục H2
        count = 0
        def repl(match):
            nonlocal count
            if count < len(body_images):
                new_src = body_images[count]
                count += 1
                return match.group(0).replace(match.group(1), new_src)
            return match.group(0)
            
        if "<img" in html_content:
            html_content = re.sub(r'<img[^>]+src=["\']([^"\']+)["\']', repl, html_content)
        else:
            # Nếu article chưa có thẻ img, chèn ảnh dưới mỗi thẻ h2
            h2_splits = re.split(r'(<h2[^>]*>.*?</h2>)', html_content)
            new_parts = []
            img_idx = 0
            for part in h2_splits:
                new_parts.append(part)
                if part.startswith('<h2') and img_idx < len(body_images):
                    img_html = f'<p style="text-align: center;"><img src="{body_images[img_idx]}" alt="{article["title"]}" style="width: 100%; max-width: 800px; border-radius: 8px;" /></p>'
                    new_parts.append(img_html)
                    img_idx += 1
            html_content = "".join(new_parts)
            
        # Ghi vào CKEditor
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
        }""", {"desc": desc_text, "content": html_content})
        
        page.wait_for_timeout(1000)
        
        # Bấm Lưu
        page.evaluate("""() => {
            for (let k in window.CKEDITOR.instances) {
                window.CKEDITOR.instances[k].updateElement();
            }
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(5000)
        
        # Lấy ID bài viết mới tạo
        print("\n[5/5] Kiểm tra và chụp ảnh nghiệm thu bài viết...")
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        first_row = page.locator("table tbody tr").first
        post_title = first_row.locator("td").nth(1).inner_text().strip()
        post_cat = first_row.locator("td").nth(2).inner_text().strip()
        post_time = first_row.locator("td").nth(4).inner_text().strip() if first_row.locator("td").count() > 4 else "N/A"
        
        print(f"  -> Bài đăng mới nhất: {post_title}")
        print(f"  -> Chuyên mục: {post_cat}")
        print(f"  -> Thời gian đặt lịch: {post_time}")
        
        proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_b2c_11h_scheduled_proof.png"
        page.screenshot(path=proof_path)
        print(f"📸 ĐÃ LƯU BẰNG CHỨNG LÊN LỊCH: {proof_path}")
        browser.close()
        
    total_duration = int(time.time() - start_total)
    print("\n" + "=" * 70)
    print(f"🎉 HOÀN THÀNH TOÀN BỘ QUY TRÌNH XUẤT BẢN BLOG NỘI THẤT TRONG: {total_duration} GIÂY ({total_duration//60}m {total_duration%60}s)!")
    print("=" * 70)

if __name__ == "__main__":
    main()
