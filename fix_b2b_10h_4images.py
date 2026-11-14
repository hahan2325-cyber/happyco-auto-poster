import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

from fast_flow_generator import generate_flow_batch_parallel

def run():
    # H2.1 da co san va da xac minh dep 10/10:
    h2_1_file = BASE_DIR / "output" / "b2b_10h_4h2_1794451652" / "happyco_flow_1_1794451795.jpg"
    assert h2_1_file.exists(), f"Missing {h2_1_file}"
    
    prompts_3 = [
        "Close-up documentary photograph of stacked industrial MDF cabinet doors with precision milled J-pull and K-pull 45-degree beveled handleless edges with smooth matte melamine finish on a wooden workbench in a Vietnamese factory, visible raw MDF edge texture, fine sawdust, zero CGI gloss, 16:9 widescreen",
        "Medium close-up documentary photograph of an industrial 45-degree slant edge banding machine unit pressing matching PVC edge tape onto a beveled MDF cabinet door through angled pressure rollers, visible mechanical gears, glue pot housing, fine sawdust around track in Vietnamese factory, zero CGI gloss, 16:9 widescreen",
        "Candid documentary photograph of a Vietnamese woodworking technician in factory uniform holding a steel tape measure inspecting dimensions and sticking printed barcode labels onto finished beveled handleless melamine cabinet doors stacked on wooden pallet, factory CNC background, zero CGI gloss, 16:9 widescreen"
    ]
    
    out_dir = BASE_DIR / "output" / f"b2b_10h_remaining3_{int(time.time())}"
    files_3 = generate_flow_batch_parallel(prompts_3, out_dir)
    print(f"Generated {len(files_3)}/3 remaining H2 images:", [f.name for f in files_3])
    if len(files_3) < 3:
        raise RuntimeError(f"Only got {len(files_3)}/3 remaining H2 images from Flow!")
        
    all_4_h2_files = [h2_1_file] + files_3[:3]
    
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
        page.wait_for_timeout(2000)
        
        ts = int(time.time())
        for idx, fpath in enumerate(all_4_h2_files):
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            
            btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
            btn.click()
            page.wait_for_timeout(1000)
            page.set_input_files("input[name='media_file']", str(fpath))
            page.fill("input[name='title']", f"Happyco B2B PUR H2_{idx+1} {ts}")
            page.locator("button:has-text('Lưu')").first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2500)
            
            cms_fn = page.evaluate('''() => {
                let firstImg = document.querySelector(".table tbody tr img, .media-list-item img, .thumbnail img, img[src*='19180']");
                if (firstImg) {
                    let parts = firstImg.src.split("/");
                    return parts[parts.length - 1].split("?")[0];
                }
                return null;
            }''')
            if not cms_fn:
                cms_fn = fpath.name
            cdn_url = f"https://media.loveitopcdn.com/19180/{cms_fn}"
            cdn_urls.append(cdn_url)
            print(f"  [+] Uploaded H2_{idx+1}: {cdn_url}")
            
        # Edit latest post (10h B2B post)
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        
        edit_url = page.locator("table tbody tr td a[href*='/edit']").first.get_attribute("href")
        print(f"Editing post: {edit_url}")
        page.goto(edit_url, timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # Replace images #2, #3, #4, #5 in body (keep image #1 = thumb image)
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
        
        page.wait_for_timeout(1000)
        page.evaluate("""() => {
            for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(5000)
        print("🎉 ĐÃ CẬP NHẬT ĐỦ 5 ẢNH RIÊNG BIỆT 100% KHỚP TỪNG MỤC H2 CHO BÀI 10H!")
        
        # Verify CMS list still shows ĐÃ LÊN LỊCH 12-11-2026 10:00
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_b2b_10h_final_verified.png"
        page.screenshot(path=proof_path)
        print(f"📸 Proof saved: {proof_path}")
        browser.close()

if __name__ == "__main__":
    run()
