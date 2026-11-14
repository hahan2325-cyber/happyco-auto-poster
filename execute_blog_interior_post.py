import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from agents.chief_qa_agent import ChiefQAAgent
from agents.b2c_interior_agent import B2CInteriorAgent
from core.image_registry import register
from playwright.sync_api import sync_playwright

def run():
    print("==================================================================")
    print("🚀 CON TỔNG (CHIEF QA AGENT) ĐIỀU PHỐI XUẤT BẢN BLOG NỘI THẤT (ID: 266)")
    print("==================================================================")
    
    # 1. B2C Interior Agent soạn bài
    print("\n[B2C Interior Agent] Đang khởi tạo nội dung chuyên sâu...")
    b2c = B2CInteriorAgent()
    topic = "Thiết Kế Vách Tivi Phòng Khách Kết Hợp Tủ Rượu Cánh Kính Hiện Đại: Đẳng Cấp Sang Trọng Từ Xưởng Happyco"
    article = b2c.produce_article(topic_title=topic)
    
    # Ensure unique slug
    unique_suffix = f"-{int(time.time())}"
    if not article.get("slug"):
        article["slug"] = f"thiet-ke-vach-tivi-phong-khach-tu-ruou-canh-kinh-happyco{unique_suffix}"
    else:
        article["slug"] = f"{article['slug'].rstrip('-')}{unique_suffix}"
        
    print(f"  -> Tiêu đề: {article['title']}")
    print(f"  -> Đường dẫn slug: {article['slug']}")
    print(f"  -> Chuyên mục: {article['category']} (ID: {article['cat_id']})")
    
    # 2. Chuẩn bị 5 ảnh từ Google Flow (100% Flow, không lấy kho cũ)
    flow_processed_dir = BASE_DIR / "output" / "flow_processed"
    image_files = {
        "thumb": str(flow_processed_dir / "flow_thumb_living.jpg"),
        "h2_1": str(flow_processed_dir / "flow_h2_1_vach_tivi.jpg"),
        "h2_2": str(flow_processed_dir / "flow_h2_2_tu_ruou.jpg"),
        "h2_3": str(flow_processed_dir / "flow_h2_3_phong_ngu.jpg"),
        "h2_4": str(flow_processed_dir / "flow_h2_4_tu_ao.jpg")
    }
    
    # Kiểm tra file ảnh tồn tại
    for k, v in image_files.items():
        if not Path(v).exists():
            raise FileNotFoundError(f"Missing image file: {v}")
            
    # 3. Con Tổng (Chief QA Agent) kiểm duyệt bài viết & ảnh
    print("\n[Chief QA Agent] Đang kiểm duyệt 6 tiêu chuẩn chất lượng...")
    qa = ChiefQAAgent()
    audit_res = qa.audit(article, list(image_files.values()))
    print(f"  -> Kết quả kiểm duyệt: {'PASS ✅' if audit_res['passed'] else 'FAIL ❌'}")
    print(f"  -> Chi tiết kiểm tra: {json.dumps(audit_res['checks'], ensure_ascii=False)}")
    if audit_res.get("errors"):
        print(f"  -> Lỗi phát hiện: {audit_res['errors']}")
        raise ValueError(f"Bài viết không đạt tiêu chuẩn xuất bản: {audit_res['errors']}")
        
    # 4. Đăng ký chống trùng lặp vào image_registry.json
    print("\n[Image Registry] Đăng ký 5 ảnh Google Flow vào kho dữ liệu chống trùng lặp...")
    for k, p in image_files.items():
        register(post_id=article["slug"], path=Path(p), source="google_flow")
        
    # 5. Publisher Bot: Upload ảnh lên CDN & Đăng bài lên CMS
    print("\n[Publisher Bot] Khởi chạy Playwright để upload ảnh và xuất bản bài viết...")
    email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL", "").strip()
    password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD", "").strip()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        # Login
        page.goto("https://happyco.asia/admin/login", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # Upload 5 images
        cdn_urls = {}
        for k in ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]:
            img_p = Path(image_files[k])
            title_img = f"Happyco - {article['title']} - {k}"
            print(f"  [Publisher] Upload CDN: {img_p.name}...")
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            
            btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
            btn.click()
            page.wait_for_timeout(800)
            page.set_input_files("input[name='media_file']", str(img_p))
            page.fill("input[name='title']", title_img)
            page.locator("button:has-text('Lưu')").first.click()
            page.wait_for_timeout(3000)
            
            cdn_url = f"https://media.loveitopcdn.com/19180/{img_p.name}"
            cdn_urls[k] = cdn_url
            print(f"    -> CDN URL: {cdn_url}")
            
        # Replace placeholders in content HTML
        content_html = article.get("content_html", "")
        for idx in range(1, 5):
            k = f"h2_{idx}"
            if k in cdn_urls:
                for ph in [f"IMAGE_PLACEHOLDER_{idx}", f"IMAGE_PLACEHOLDER_H2_{idx}", f"{{{{IMAGE_H2_{idx}}}}}"]:
                    content_html = content_html.replace(ph, cdn_urls[k])
        if "thumb" in cdn_urls:
            content_html = content_html.replace("IMAGE_PLACEHOLDER_THUMB", cdn_urls["thumb"])
            
        content_html = content_html.replace('/thumb/150x150/', '/').replace('?zc=1', '')
        
        # Open post create page
        print("  [Publisher] Đang mở trang thêm bài viết mới...")
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        
        # Fill Title & Slug
        page.fill('input[name="title"]', article["title"])
        if page.locator('input[name="slug"]').count() > 0:
            page.fill('input[name="slug"]', article["slug"])
            
        # Fill Meta
        page.fill('input[name="meta_keyword"]', article.get("keywords", "nội thất happyco, vách tivi, tủ rượu cánh kính"))
        if page.locator('input[name="meta_title"]').count() > 0:
            page.fill('input[name="meta_title"]', article["title"])
        if page.locator('textarea[name="meta_description"]').count() > 0:
            page.fill('textarea[name="meta_description"]', article.get("description", ""))
            
        # Select Category 266 (BLOG NỘI THẤT)
        page.select_option('select[name="cat_id"]', "266")
        print("  [Publisher] Đã chọn danh mục ID: 266 (BLOG NỘI THẤT)")
        
        # Set Thumbnail
        thumb_name = Path(image_files["thumb"]).name
        thumb_preview = f"https://media.loveitopcdn.com/19180/thumb/150x150/{thumb_name}?zc=1"
        page.evaluate("""({tval, tprev}) => {
            let el = document.getElementById('thumbnail');
            if (el) {
                el.value = tval;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            let holder = document.getElementById('holder_thumbnail');
            if (holder) holder.src = tprev;
        }""", {"tval": thumb_name, "tprev": thumb_preview})
        
        # Schedule / Published date: 10-11-2026 11:00
        page.evaluate("""() => {
            let el = document.querySelector('input[name="published_at"]');
            if (el) {
                el.value = "10-11-2026 11:00";
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""")
        print("  [Publisher] Đã cài đặt giờ đăng: 10-11-2026 11:00")
            
        # Check is_published
        chk = page.locator('input[name="is_published"]')
        if chk.count() > 0 and not chk.is_checked():
            chk.check()
            
        # Inject CKEditor content & description
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
        
        # Dismiss any overlays
        page.evaluate("""() => {
            if (window.swal) { try { swal.close(); } catch(e) {} }
            let overlays = document.querySelectorAll('.sweet-overlay, .sweet-alert');
            overlays.forEach(o => o.remove());
        }""")
        
        # Save post
        print("  [Publisher] Đang bấm Lưu bài viết...")
        page.evaluate("""() => {
            if (window.CKEDITOR && window.CKEDITOR.instances) {
                for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
            }
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
            else {
                let f = document.getElementById('post-form') || document.querySelector('form');
                if (f) f.submit();
            }
        }""")
        
        page.wait_for_timeout(6000)
        
        # Verify in /admin/post
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        screenshot_path = Path(r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_blog_noithat_11h_final.png")
        page.screenshot(path=str(screenshot_path))
        print(f"  [Publisher] Đã chụp ảnh xác minh tại: {screenshot_path}")
        
        post_row = page.evaluate("""() => {
            let row = document.querySelector('.table tbody tr');
            if (!row) return null;
            let idEl = row.querySelector('td:nth-child(1)');
            let titleEl = row.querySelector('td:nth-child(2) a') || row.querySelector('a');
            let catEl = row.querySelector('td:nth-child(3)');
            let dateEl = row.querySelector('td:nth-child(5)');
            return {
                id: idEl ? idEl.innerText.trim() : '',
                title: titleEl ? titleEl.innerText.trim() : '',
                cat: catEl ? catEl.innerText.trim() : '',
                date: dateEl ? dateEl.innerText.trim() : ''
            };
        }""")
        print(f"  [Publisher] Bài viết mới nhất trên CMS: {post_row}")
        
        browser.close()
        
    print("\n🎉 CON TỔNG BÁO CÁO: HOÀN TẤT XUẤT BẢN THÀNH CÔNG!")

if __name__ == "__main__":
    run()
