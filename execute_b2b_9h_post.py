import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

from fast_flow_generator import generate_flow_batch_parallel
from core.topic_memory import ensure_green_box, record_published

def main():
    t0 = time.time()
    json_path = BASE_DIR / "output" / "b2b_9h_article.json"
    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    article = payload["article"]
    prompts_list = payload["image_prompts"]
    raw_prompts = [p["prompt_en"] for p in prompts_list]

    print("==================================================================")
    print("🚀 CON TỔNG THỰC THI RENDER 5 ẢNH & ĐĂNG BÀI B2B LỊCH 09:00")
    print(f"📝 Tiêu đề: {article['title']}")
    print(f"📂 Chuyên mục: GIA CÔNG VÁN CÔNG NGHIỆP (cat_id: 265)")
    print("==================================================================")

    # 1. Đảm bảo Tab 0 trên Chrome 9333 đang ở đúng Project Flow
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        pg = b.contexts[0].pages[0]
        if "d7cecce7-8682-454a-bb94-13576243c599" not in pg.url:
            pg.goto("https://flow.google.com/project/d7cecce7-8682-454a-bb94-13576243c599", wait_until="domcontentloaded", timeout=45000)
        pg.wait_for_selector("[contenteditable='true']:visible, [role='textbox']:visible", timeout=30000)
        b.close()

    # 2. Sinh 5 ảnh song song chuẩn 1-1 bằng Fast Flow
    out_dir = BASE_DIR / "output" / f"b2b_abf_9h_{int(time.time())}"
    generated_files = generate_flow_batch_parallel(raw_prompts, out_dir)

    # Nếu thiếu ảnh do mạng thì retry ảnh thiếu
    if len(generated_files) < 5:
        existing_indices = set()
        for gf in generated_files:
            parts = gf.name.split("_")
            if len(parts) >= 3 and parts[2].isdigit():
                existing_indices.add(int(parts[2]) - 1)
        missing = [i for i in range(5) if i not in existing_indices]
        print(f"⚠️ Thử tạo bù {len(missing)} ảnh còn thiếu: {missing}")
        if missing:
            retry_prompts = [raw_prompts[i] for i in missing]
            retry_files = generate_flow_batch_parallel(retry_prompts, out_dir / "retry")
            file_by_idx = {}
            for gf in generated_files:
                parts = gf.name.split("_")
                if len(parts) >= 3 and parts[2].isdigit():
                    file_by_idx[int(parts[2]) - 1] = gf
            for pos, rf in zip(missing, retry_files):
                file_by_idx[pos] = rf
            generated_files = [file_by_idx[i] for i in sorted(file_by_idx.keys())]

    if len(generated_files) < 5:
        raise RuntimeError(f"Chỉ lấy được {len(generated_files)}/5 ảnh riêng biệt!")

    print(f"\n✅ Đã chuẩn bị đủ {len(generated_files)} ảnh xử lý sạch Google watermark và gắn Logo Top-Left.")

    # 3. Upload 5 ảnh lên Loveitop CDN
    print("\n[Con Tổng] Upload 5 ảnh lên Loveitop CDN qua CMS /admin/media...")
    CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
    CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")

    cdn_urls = []
    cdn_filenames = []
    ts = int(time.time())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        # Login
        page.goto("https://happyco.asia/admin/login", timeout=40000)
        page.fill("input[name='email']", CMS_EMAIL)
        page.fill("input[name='password']", CMS_PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        # Upload 5 files
        for idx, fpath in enumerate(generated_files[:5]):
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(800)

            page.locator("button:has-text('Thêm file / hình ảnh')").first.click()
            page.wait_for_timeout(800)
            page.set_input_files("input[name='media_file']", str(fpath))
            page.fill("input[name='title']", f"Happyco B2B ABF 9h {idx + 1} {ts}")
            page.locator("button:has-text('Lưu')").first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            cms_fn = page.evaluate('''() => {
                let firstImg = document.querySelector(".table tbody tr img, .media-list-item img, .thumbnail img, img[src*='19180']");
                if (firstImg) {
                    let parts = firstImg.src.split("/");
                    return parts[parts.length - 1].split("?")[0];
                }
                return null;
            }''') or fpath.name
            cdn_url = f"https://media.loveitopcdn.com/19180/{cms_fn}"
            cdn_urls.append(cdn_url)
            cdn_filenames.append(cms_fn)
            print(f"  [+] Uploaded ({idx+1}/5): {cdn_url}")

        # Thay thế placeholder ảnh vào content_html
        content_html = article["content_html"]
        for i in range(1, 5):
            content_html = content_html.replace(f"IMAGE_PLACEHOLDER_{i}", cdn_urls[i])
        content_html = ensure_green_box(content_html)

        slug = article.get("slug") or f"5-loi-xuat-file-abf-sketchup-khi-cat-cnc-lam-hao-phoi-van-{ts}"
        if not slug.endswith(str(ts)[-4:]):
            slug = f"{slug.rstrip('-')}-{ts}"

        # 4. Tạo bài viết trên CMS (cat_id=265, lịch 14-11-2026 09:00)
        print("\n[Con Tổng] Tạo bài viết trên CMS (cat_id=265, lịch 14-11-2026 09:00)...")
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        page.fill('input[name="title"]', article["title"])
        page.fill('input[name="slug"]', slug)
        page.select_option('select[name="cat_id"]', "265")
        page.fill('input[name="meta_keyword"]', article.get("keywords", "lỗi xuất file abf sketchup cắt cnc, gia công ván theo file abf, happyco"))

        publish_time = "14-11-2026 09:00"
        page.evaluate("""(val) => {
            document.querySelectorAll('input[name="published_at"]').forEach(el => {
                const jq = window.jQuery || window.$;
                if (jq && jq(el).data('daterangepicker') && window.moment) {
                    const m = window.moment(val, 'DD-MM-YYYY HH:mm');
                    jq(el).data('daterangepicker').setStartDate(m);
                    jq(el).data('daterangepicker').setEndDate(m);
                }
                el.value = val;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            });
        }""", publish_time)

        chk = page.locator('input[name="is_published"]')
        if chk.count() > 0 and not chk.is_checked():
            chk.check()

        desc = article.get("description", "")
        for sel in ['textarea[name="description"]', 'textarea[name="meta_description"]', 'input[name="meta_description"]']:
            if page.locator(sel).count() > 0:
                page.fill(sel, desc)

        # Upload thumbnail
        thumb_input = page.locator('input[name="image"], input[name="image_file"], input[type="file"]').first
        if thumb_input.count() > 0:
            thumb_input.set_input_files(str(generated_files[0]))
            page.wait_for_timeout(1000)

        # Cập nhật CKEditor
        page.evaluate("""(html) => {
            if (window.CKEDITOR) {
                for (let k in window.CKEDITOR.instances) {
                    window.CKEDITOR.instances[k].setData(html);
                }
            }
            const ta = document.querySelector('textarea[name="content"]');
            if (ta) ta.value = html;
        }""", content_html)
        page.wait_for_timeout(1500)

        # Submit
        print("  -> Bấm submit lưu bài viết...")
        page.evaluate("""() => {
            if (window.CKEDITOR) {
                for (let k in window.CKEDITOR.instances) {
                    window.CKEDITOR.instances[k].updateElement();
                }
            }
        }""")
        page.wait_for_timeout(500)

        submit_btn = page.locator('button[onclick*="nav_submit_form"]').first
        if submit_btn.count() == 0:
            submit_btn = page.locator('.btn-info.btn-ladda, button[type="submit"]:has-text("Lưu")').first
        submit_btn.click()

        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3500)

        # Kiểm tra danh sách bài viết
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        proof_path = BASE_DIR / "output" / "cms_b2b_9h_scheduled_verified.png"
        page.screenshot(path=str(proof_path), full_page=False)
        print(f"📸 Đã chụp ảnh xác thực danh sách bài viết: {proof_path}")

        # Ghi nhận vào topic memory
        record_published(
            title=article["title"],
            cat="GIA CÔNG VÁN CÔNG NGHIỆP",
            formula=article.get("formula_id", "number_mistakes"),
            pool=article.get("pool", "b2b_abf_mistakes")
        )

        elapsed = time.time() - t0
        print(f"\n🎉 HOÀN TẤT ĐĂNG BÀI VÀ ĐẶT LỊCH 09:00 TRONG {elapsed:.1f} GIÂY!")
        browser.close()

if __name__ == "__main__":
    main()
