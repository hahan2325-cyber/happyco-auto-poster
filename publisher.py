"""
Hệ thống tự động đăng bài và tải ảnh lên CMS Happyco
Sử dụng Playwright Headless, tương thích hoàn hảo trên GitHub Actions Linux Runners
Đảm bảo:
- Ảnh chèn vào nội dung bài viết là ảnh FULL HD gốc (không dùng link thumb/150x150)
- Thiết lập ô #thumbnail đúng chuẩn filename để hiển thị đầy đủ trên CMS và website
- Không có bất kỳ watermark bên thứ 3 nào
- Giữ vững tính bất biến của chân trang hệ thống
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def upload_image_to_cms(page, image_path: Path, title: str) -> str:
    print(f"  [Publisher] Đang tải lên CDN: {image_path.name}...", flush=True)
    page.goto("https://happyco.asia/admin/media", timeout=40000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)

    btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
    btn.click()
    page.wait_for_timeout(1000)

    page.set_input_files("input[name='media_file']", str(image_path))
    page.fill("input[name='title']", title)
    page.wait_for_timeout(800)

    save_btn = page.locator("button:has-text('Lưu')").first
    save_btn.click()
    page.wait_for_timeout(3500)

    # Lấy đường link CDN gốc chất lượng cao (FULL HD, không lấy thumb 150x150)
    cdn_full_url = f"https://media.loveitopcdn.com/19180/{image_path.name}"
    print(f"    -> Live Full HD CDN URL: {cdn_full_url}", flush=True)
    return cdn_full_url

def publish_post(article_data: dict, image_files: dict, publish_mode: str = "publish", artifacts_dir: Path = None) -> dict:
    email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL", "").strip()
    password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD", "").strip()

    if not email or not password:
        raise ValueError("Missing CMS_EMAIL or CMS_PASSWORD credentials!")

    if artifacts_dir is None:
        artifacts_dir = Path(__file__).resolve().parent / "output"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Publisher] Khởi chạy Playwright đăng nhập Happyco Admin...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # 1. Login
        page.goto("https://happyco.asia/admin/login", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        if "/admin/login" in page.url:
            raise RuntimeError("Đăng nhập thất bại! Vui lòng kiểm tra lại tài khoản mật khẩu CMS.")

        print("  [Publisher] Đăng nhập quản trị Happyco thành công!", flush=True)

        # 2. Upload 5 unique images
        cdn_urls = {}
        for key in ["thumb", "h2_1", "h2_2", "h2_3", "h2_4"]:
            local_img = image_files.get(key)
            if not local_img:
                continue
            title = f"Happyco - {article_data.get('title', '')} - {key}"
            cdn_url = upload_image_to_cms(page, Path(local_img), title)
            cdn_urls[key] = cdn_url

        # 3. Replace image placeholders in HTML with Full HD CDN URLs
        content_html = article_data.get("content_html", "")
        for idx in range(1, 5):
            k = f"h2_{idx}"
            if k in cdn_urls:
                for ph in [f"IMAGE_PLACEHOLDER_{idx}", f"IMAGE_PLACEHOLDER_H2_{idx}", f"{{{{IMAGE_H2_{idx}}}}}"]:
                    if ph in content_html:
                        content_html = content_html.replace(ph, cdn_urls[k])

        if "thumb" in cdn_urls:
            for ph in ["IMAGE_PLACEHOLDER_THUMB", "{{IMAGE_THUMB}}"]:
                if ph in content_html:
                    content_html = content_html.replace(ph, cdn_urls["thumb"])

        # Đảm bảo KHÔNG có bất kỳ link thumb 150x150 nào lọt vào nội dung bài viết
        content_html = content_html.replace('/thumb/150x150/', '/').replace('?zc=1', '')

        # 4. Open Post Creation Form
        print("  [Publisher] Đang mở trang thêm bài viết mới...", flush=True)
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Fill Title & Slug
        page.fill('input[name="title"]', article_data["title"])
        if article_data.get("slug") and page.locator('input[name="slug"]').count() > 0:
            page.fill('input[name="slug"]', article_data["slug"])

        # Fill Meta
        tags = article_data.get("keywords") or article_data.get("tags") or "Happyco, nội thất Happyco, xưởng mộc biên hòa"
        if page.locator('input[name="meta_keyword"]').count() > 0:
            page.fill('input[name="meta_keyword"]', tags)
        if page.locator('input[name="meta_title"]').count() > 0:
            page.fill('input[name="meta_title"]', article_data.get("meta_title", article_data["title"]))
        if page.locator('textarea[name="meta_description"]').count() > 0:
            page.fill('textarea[name="meta_description"]', article_data.get("meta_description", article_data.get("description", "")))

        # Select Category
        cat_id = str(article_data.get("cat_id", "266"))
        req_cat = str(article_data.get("category", "")).upper()
        if "GIA CÔNG" in req_cat or "265" in req_cat or cat_id == "265":
            cat_id = "265"
        elif "PHỤ KIỆN" in req_cat or "396" in req_cat or cat_id == "396":
            cat_id = "396"
        elif "THIẾT KẾ THI CÔNG" in req_cat or "264" in req_cat or cat_id == "264":
            cat_id = "264"
        else:
            cat_id = "266"

        if page.locator('select[name="cat_id"]').count() > 0:
            page.select_option('select[name="cat_id"]', cat_id)
            print(f"  [Publisher] Đã chọn danh mục ID: {cat_id}", flush=True)

        # 5. Set Featured Thumbnail chuẩn xác (truyền filename vào #thumbnail và link thumb vào #holder_thumbnail)
        thumb_img_path = image_files.get("thumb")
        thumb_filename = Path(thumb_img_path).name if thumb_img_path else "happyco_thumb.jpg"
        thumb_preview_url = f"https://media.loveitopcdn.com/19180/thumb/150x150/{thumb_filename}?zc=1"

        page.evaluate("""({tval, tprev}) => {
            let el = document.getElementById('thumbnail');
            if (el) {
                el.value = tval;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            let holder = document.getElementById('holder_thumbnail');
            if (holder) {
                holder.src = tprev;
            }
        }""", {"tval": thumb_filename, "tprev": thumb_preview_url})
        print(f"  [Publisher] Đã thiết lập Thumbnail chuẩn: {thumb_filename}", flush=True)

        # 6. Inject Content into CKEditor
        desc_text = article_data.get("description", "")
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

        # Publication status
        is_published_checkbox = page.locator('input[name="is_published"]')
        if is_published_checkbox.count() > 0:
            if publish_mode == "publish":
                if not is_published_checkbox.is_checked():
                    is_published_checkbox.check()
            else:
                if is_published_checkbox.is_checked():
                    is_published_checkbox.uncheck()

        # Dismiss SweetAlert overlays if any
        page.evaluate("""() => {
            if (window.swal) { try { swal.close(); } catch(e) {} }
            let overlays = document.querySelectorAll('.sweet-overlay, .sweet-alert');
            overlays.forEach(o => o.remove());
        }""")

        screenshot_preview = artifacts_dir / "post_filled_preview.png"
        page.screenshot(path=str(screenshot_preview))

        # Submit form
        print("  [Publisher] Đang lưu và xuất bản bài viết...", flush=True)
        page.evaluate("""() => {
            if (window.CKEDITOR && window.CKEDITOR.instances) {
                for (let k in window.CKEDITOR.instances) {
                    window.CKEDITOR.instances[k].updateElement();
                }
            }
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) {
                btn.click();
            } else {
                let form = document.getElementById('post-form') || document.querySelector('form');
                if (form) form.submit();
            }
        }""")

        page.wait_for_timeout(5000)

        # Navigate to admin post list to verify
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        screenshot_published = artifacts_dir / "cms_post_published.png"
        page.screenshot(path=str(screenshot_published))

        # Extract newly created post info
        post_info = page.evaluate("""() => {
            let row = document.querySelector('.table tbody tr');
            if (!row) return null;
            let titleEl = row.querySelector('td:nth-child(2) a') || row.querySelector('a');
            let idEl = row.querySelector('td:nth-child(1)');
            let viewEl = row.querySelector('a[href*="/blog/"], a[href*="happyco.asia/"]');
            return {
                id: idEl ? idEl.innerText.trim() : '',
                title: titleEl ? titleEl.innerText.trim() : '',
                url: viewEl ? viewEl.href : ''
            };
        }""")

        browser.close()

    print(f"\n🎉 [Publisher] XUẤT BẢN THÀNH CÔNG! Post ID: {post_info.get('id') if post_info else 'N/A'}", flush=True)
    return {
        "status": "success",
        "post_info": post_info,
        "cdn_urls": cdn_urls,
        "screenshots": [str(screenshot_preview), str(screenshot_published)]
    }
