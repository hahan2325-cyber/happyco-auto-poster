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
    json_path = BASE_DIR / "output" / "b2c_11h_article.json"
    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    article = payload["article"]
    prompts_list = payload["image_prompts"]
    raw_prompts = [p["prompt_en"] for p in prompts_list]

    print("==================================================================")
    print("🚀 CON TỔNG THỰC THI RENDER 5 ẢNH & ĐĂNG BÀI B2C LỊCH 11:00")
    print(f"📝 Tiêu đề: {article['title']}")
    print(f"📂 Chuyên mục: BLOG NỘI THẤT (cat_id: 266)")
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
    out_dir = BASE_DIR / "output" / f"b2c_11h_{int(time.time())}"
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
            page.fill("input[name='title']", f"Happyco B2C Interior 11h {idx + 1} {ts}")
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

        slug = article.get("slug") or f"blog-noi-that-11h-{ts}"
        if not slug.endswith(str(ts)[-4:]):
            slug = f"{slug.rstrip('-')}-{ts}"

        # 4. Tạo bài viết trên CMS (cat_id=266, lịch 14-11-2026 11:00)
        print("\n[Con Tổng] Tạo bài viết trên CMS (cat_id=266, lịch 14-11-2026 11:00)...")
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        page.fill('input[name="title"]', article["title"])
        page.fill('input[name="slug"]', slug)
        page.select_option('select[name="cat_id"]', "266")
        page.fill('input[name="meta_keyword"]', article.get("keywords", "thiết kế nội thất gỗ, blog nội thất, happyco"))

        publish_time = "14-11-2026 11:00"
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

        # Set thumbnail
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

        # Set description & content via CKEditor
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
        }""", {"desc": article["description"], "content": content_html})

        page.wait_for_timeout(1000)
        page.evaluate("""() => {
            for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(5000)

        # Kiểm tra danh sách bài viết trên CMS
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        first_row = page.locator("table tbody tr").first
        row_title = first_row.locator("td").nth(2).inner_text().strip()
        row_cat = first_row.locator("td").nth(3).inner_text().strip()
        row_time = first_row.locator("td").nth(4).inner_text().strip()
        edit_href = first_row.locator("a[href*='/edit']").first.get_attribute("href")
        print(f"  -> CMS Row Title: {row_title}")
        print(f"  -> CMS Row Cat: {row_cat}")
        print(f"  -> CMS Row Status/Time: {row_time}")
        print(f"  -> Edit URL: {edit_href}")

        proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_b2c_11h_scheduled_verified.png"
        page.screenshot(path=proof_path)
        print(f"📸 Saved CMS schedule proof: {proof_path}")
        browser.close()

    record_published(
        title=article["title"],
        cat="BLOG NỘI THẤT",
        formula_id=article.get("formula_id", "question_pain"),
        pool=article.get("pool", "b2c_japandi")
    )
    elapsed = time.time() - t0
    print(f"\n🎉 HOÀN TẤT ĐĂNG BÀI VÀ ĐẶT LỊCH B2C 11:00 TRONG {elapsed:.1f} GIÂY!")

if __name__ == "__main__":
    main()
