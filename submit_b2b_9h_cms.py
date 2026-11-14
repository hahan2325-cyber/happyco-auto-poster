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

from core.topic_memory import ensure_green_box, record_published

def main():
    t0 = time.time()
    json_path = BASE_DIR / "output" / "b2b_9h_article.json"
    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    article = payload["article"]

    cdn_urls = [
        "https://media.loveitopcdn.com/19180/happyco_flow_1_1794620971.jpg",
        "https://media.loveitopcdn.com/19180/happyco_flow_2_1794620971.jpg",
        "https://media.loveitopcdn.com/19180/happyco_flow_1_1794621019.jpg",
        "https://media.loveitopcdn.com/19180/happyco_flow_4_1794620971.jpg",
        "https://media.loveitopcdn.com/19180/happyco_flow_5_1794620971.jpg",
    ]
    cdn_filenames = [
        "happyco_flow_1_1794620971.jpg",
        "happyco_flow_2_1794620971.jpg",
        "happyco_flow_1_1794621019.jpg",
        "happyco_flow_4_1794620971.jpg",
        "happyco_flow_5_1794620971.jpg",
    ]

    print("==================================================================")
    print("🚀 ĐĂNG BÀI B2B VÀO CMS VÀ ĐẶT LỊCH 09:00 (14-11-2026)")
    print(f"📝 Tiêu đề: {article['title']}")
    print(f"📂 Chuyên mục: GIA CÔNG VÁN CÔNG NGHIỆP (cat_id: 265)")
    print("==================================================================")

    content_html = article["content_html"]
    for i in range(1, 5):
        content_html = content_html.replace(f"IMAGE_PLACEHOLDER_{i}", cdn_urls[i])
    content_html = ensure_green_box(content_html)

    ts = int(time.time())
    slug = article.get("slug") or f"5-loi-xuat-file-abf-sketchup-khi-cat-cnc-lam-hao-phoi-van-{ts}"
    if not slug.endswith(str(ts)[-4:]):
        slug = f"{slug.rstrip('-')}-{ts}"

    CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
    CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")

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

        # Create post
        print("\n[Con Tổng] Mở trang tạo bài viết https://happyco.asia/admin/post/create...")
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

        proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_b2b_9h_scheduled_verified.png"
        page.screenshot(path=proof_path)
        print(f"📸 Saved CMS schedule proof: {proof_path}")
        browser.close()

    record_published(article["title"], "GIA CÔNG VÁN CÔNG NGHIỆP", article.get("formula_id", "number_mistakes"), article.get("pool", "b2b_abf_mistakes"))
    print(f"\n🎉 HOÀN TẤT ĐĂNG BÀI VÀ ĐẶT LỊCH B2B 09:00 THÀNH CÔNG!")

if __name__ == "__main__":
    main()
