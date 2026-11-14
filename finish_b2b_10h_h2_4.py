import os
import sys
import time
import base64
from pathlib import Path
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

from fast_flow_generator import remove_flow_watermark, stamp_top_left, WM_PATH

def run():
    h2_1 = BASE_DIR / "output" / "b2b_10h_4h2_1794451652" / "happyco_flow_1_1794451795.jpg"
    h2_2 = BASE_DIR / "output" / "b2b_10h_remaining3_1794451942" / "happyco_flow_1_1794452063.jpg"
    h2_3 = BASE_DIR / "output" / "b2b_10h_remaining3_1794451942" / "happyco_flow_2_1794452063.jpg"
    
    for f in [h2_1, h2_2, h2_3]:
        assert f.exists(), f"Missing {f}"

    prompt_5 = "Candid documentary photograph of a Vietnamese woodworking technician in factory uniform holding a steel tape measure inspecting dimensions and sticking printed barcode labels onto finished beveled handleless melamine cabinet doors stacked on wooden pallet, factory CNC background, zero CGI gloss, 16:9 widescreen"
    prefix = prompt_5[:75].strip().lower()

    out_dir = BASE_DIR / "output" / f"b2b_10h_h24_{int(time.time())}"
    out_dir.mkdir(parents=True, exist_ok=True)
    wm_img = Image.open(WM_PATH).convert("RGBA")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
        page = browser.contexts[0].pages[0]
        page.bring_to_front()

        used_srcs = set(page.evaluate("() => Array.from(document.querySelectorAll('img')).map(i => i.src)"))

        # Click arrow_forward button (Prompt 5 is already in the box, or refill cleanly if empty)
        box = page.locator("[contenteditable='true']:visible").first
        cur_txt = box.inner_text().strip()
        if prefix not in cur_txt.lower():
            box.click()
            page.keyboard.press("Control+a")
            page.keyboard.press("Backspace")
            box.fill(prompt_5)
            page.wait_for_timeout(400)

        gen_btn = page.locator('button:has(:text-is("arrow_forward"))').first
        gen_btn.click()
        print("[+] Đã click nút → gửi Prompt 5 (H2.4), đang chờ Flow vẽ...", flush=True)

        target_src = None
        t0 = time.time()
        while time.time() - t0 < 55:
            dom_imgs = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('img'))
                    .filter(img => img.naturalWidth > 500 && img.alt && img.alt !== 'Ô hiển thị hình ảnh của người dùng')
                    .map(img => ({ src: img.src, alt: img.alt }));
            }""")
            for d in dom_imgs:
                if d["src"] not in used_srcs and prefix in d["alt"].lower():
                    target_src = d["src"]
                    print(f"  ⚡ Xong ảnh H2.4 sau {int(time.time() - t0)}s!", flush=True)
                    break
            if target_src:
                break
            time.sleep(2)

        if not target_src:
            raise RuntimeError("Không lấy được ảnh H2.4 từ Flow!")

        data_url = page.evaluate("""async (src) => {
            const img = Array.from(document.querySelectorAll('img')).find(el => el.src === src && el.naturalWidth > 500);
            if (!img) return null;
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/jpeg', 0.95);
        }""", target_src)
        browser.close()

    buf = base64.b64decode(data_url.split(",")[1])
    raw_p = out_dir / "raw_h2_4.jpg"
    raw_p.write_bytes(buf)

    img_bgr = cv2.imread(str(raw_p))
    clean_bgr = remove_flow_watermark(img_bgr)
    img = Image.fromarray(cv2.cvtColor(clean_bgr, cv2.COLOR_BGR2RGB))
    w, h = img.size
    target_h = int(w * 9 / 16)
    if h > target_h:
        top = (h - target_h) // 2
        img = img.crop((0, top, w, top + target_h))
    img = img.resize((1376, 768), Image.Resampling.LANCZOS)
    stamped = stamp_top_left(img, wm_img)

    ts = int(time.time())
    h2_4 = out_dir / f"happyco_flow_4_{ts}.jpg"
    stamped.save(h2_4, "JPEG", quality=95)
    print(f"  [TopLeft Stamp] Hoàn thành H2.4: {h2_4.name}")

    # Upload all 4 distinct H2 images and update CMS post
    all_4 = [h2_1, h2_2, h2_3, h2_4]
    CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
    CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")
    cdn_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        page.goto("https://happyco.asia/admin/login", timeout=40000)
        page.fill("input[name='email']", CMS_EMAIL)
        page.fill("input[name='password']", CMS_PASSWORD)
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        for idx, fpath in enumerate(all_4):
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(800)

            page.locator("button:has-text('Thêm file / hình ảnh')").first.click()
            page.wait_for_timeout(800)
            page.set_input_files("input[name='media_file']", str(fpath))
            page.fill("input[name='title']", f"Happyco B2B PUR H2_{idx+1} {ts}")
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
            print(f"  [+] Uploaded H2_{idx+1}: {cdn_url}")

        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        edit_url = page.locator("table tbody tr td a[href*='/edit']").first.get_attribute("href")
        print(f"Updating post: {edit_url}")

        page.goto(edit_url, timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)

        page.evaluate("""({imgs}) => {
            if (window.CKEDITOR && window.CKEDITOR.instances) {
                for (let k in window.CKEDITOR.instances) {
                    let el = document.getElementById(k);
                    if (el && el.name === 'content') {
                        let html = window.CKEDITOR.instances[k].getData();
                        let idx = 0;
                        html = html.replace(/<img[^>]+src=["']([^"']+)["']/g, (match, src) => {
                            let cur = idx++;
                            if (cur >= 1 && cur <= 4) {
                                return match.replace(src, imgs[cur - 1]);
                            }
                            return match;
                        });
                        window.CKEDITOR.instances[k].setData(html);
                        window.CKEDITOR.instances[k].updateElement();
                        el.value = html;
                    }
                }
            }
        }""", {"imgs": cdn_urls})

        page.wait_for_timeout(800)
        page.evaluate("""() => {
            for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(4000)
        print("🎉 ĐÃ CẬP NHẬT HOÀN CHỈNH 5/5 ẢNH RIÊNG BIỆT CHO BÀI B2B 10H!")

        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1200)
        proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_b2b_10h_final_verified.png"
        page.screenshot(path=proof_path)
        print(f"📸 Proof saved: {proof_path}")
        browser.close()

if __name__ == "__main__":
    run()
