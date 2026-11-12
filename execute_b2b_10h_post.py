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
    start_total = time.time()
    print("==================================================================")
    print("🚀 CON TỔNG (CHIEF QA) THỰC THI XUẤT BẢN BÀI B2B 10H TỪ SUB-AGENT")
    print("==================================================================")
    
    title = "Gia Công Dán Cạnh PUR Noline & Vát Tay Nắm J-K Cánh Tủ: Đột Phá Không Đường Keo Cho Xưởng Mộc – Happyco"
    slug = f"gia-cong-dan-canh-pur-noline-vat-tay-nam-j-k-canh-tu-happyco-{int(time.time())}"
    meta_keywords = "dán cạnh PUR noline, gia công vát tay nắm J-K, dán cạnh vát nghiêng 45 độ, gia công ván công nghiệp Đồng Nai, dán cạnh không đường keo, gia công nhận file ABF, xưởng gia công Happyco Biên Hòa"
    description = "Giải pháp gia công dán cạnh PUR Noline không đường keo và phay vát tay nắm âm J-K trên dây chuyền vát nghiêng 45 độ tự động tại Happyco. Nhận file ABF, trả phôi hoàn thiện trong 24h-48h giúp xưởng mộc tối ưu chi phí đầu tư."
    
    prompts = [
        "Documentary photography, handheld eye-level wide shot inside a real industrial Vietnamese woodworking workshop in Dong Nai, showing a modern automatic edge banding machine production line in operation, neatly stacked melamine MDF panels on wooden pallets beside the conveyor, fine sawdust texture on the concrete floor and machine edges, natural overhead white tube LED lighting, candid industrial atmosphere, authentic work environment, realistic metal wear and dust, shot on 35mm lens, sharp focus, zero CGI gloss, zero 3D render look, 16:9 widescreen",
        "Documentary photography, handheld macro close-up eye-level shot of a light matte white melamine MDF cabinet panel edge finished with PUR zero-joint noline edge banding inside a real Vietnamese woodworking factory, seamless invisible glue line between the PVC edge band and panel surface, subtle fine sawdust specks on the workbench surface, natural industrial tube LED lighting reflecting softly off the matte wood surface, authentic workshop craftsmanship detail, realistic tactile texture, shot on 50mm macro lens, zero CGI gloss, zero 3D render look, 16:9 widescreen",
        "Documentary photography, handheld eye-level close-up of stacked industrial engineered wood cabinet doors featuring precision milled J-pull and K-pull 45-degree beveled handleless edges with smooth matte melamine finish, resting on a wooden worktable in a real Vietnamese woodworking workshop, visible fine MDF core texture along a freshly milled edge sample and subtle wood dust on the table, natural overhead tube LED factory lighting, authentic manufacturing quality, realistic shadows, zero CGI gloss, zero 3D render look, 16:9 widescreen",
        "Documentary photography, handheld eye-level medium close-up of an industrial automatic 45-degree slant edge banding machine unit actively pressing a matching PVC edge tape onto a beveled MDF cabinet door through angled steel and rubber pressure rollers, visible mechanical gears, glue pot housing, and fine sawdust particles around the conveyor track in a real Vietnamese woodworking factory, natural overhead tube LED workshop lighting, authentic industrial motion and wear, zero CGI gloss, zero 3D render look, 16:9 widescreen",
        "Documentary photography, handheld eye-level shot of a Vietnamese woodworking technician in workshop uniform using a steel tape measure to inspect dimensions and applying printed barcode labels onto finished beveled handleless melamine cabinet doors stacked neatly on a wooden pallet, real industrial factory background with CNC machines and stacked boards, fine sawdust texture in the air and floor, natural overhead tube LED lighting, candid authentic work moment, zero CGI gloss, zero 3D render look, 16:9 widescreen"
    ]
    
    # 1. Sinh 5 ảnh song song chuẩn 1-1 bằng Fast Flow
    batch_out = BASE_DIR / "output" / f"b2b_pur_10h_{int(time.time())}"
    generated_files = generate_flow_batch_parallel(prompts, batch_out)
    
    if len(generated_files) < 5:
        print(f"⚠️ Lưu ý: Đã lấy được {len(generated_files)}/5 ảnh mới từ Flow.")
        if len(generated_files) == 0:
            raise RuntimeError("Không tạo được ảnh nào từ Flow!")
        while len(generated_files) < 5:
            generated_files.append(generated_files[-1])
            
    # 2. Upload lên Loveitop CDN qua CMS
    print("\n[Con Tổng] Upload 5 ảnh lên CDN qua /admin/media...")
    CMS_EMAIL = os.getenv("HAPPYCO_EMAIL")
    CMS_PASSWORD = os.getenv("HAPPYCO_PASSWORD")
    
    cdn_urls = []
    cdn_filenames = []
    
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
        for idx, fpath in enumerate(generated_files[:5]):
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            
            btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
            btn.click()
            page.wait_for_timeout(1000)
            page.set_input_files("input[name='media_file']", str(fpath))
            page.fill("input[name='title']", f"Happyco B2B PUR {idx + 1} {ts}")
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
            cdn_filenames.append(cms_fn)
            print(f"  [+] Uploaded CDN ({idx+1}/5): {cdn_url}")
            
        # 3. Đăng bài trên CMS /admin/post/create (Category 265, Schedule 12-11-2026 10:00)
        print("\n[Con Tổng] Tạo bài viết trên CMS và lên lịch 10:00 (12-11-2026)...")
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        page.fill('input[name="title"]', title)
        page.fill('input[name="slug"]', slug)
        
        # Category 265 (GIA CÔNG VÁN CÔNG NGHIỆP)
        page.select_option('select[name="cat_id"]', "265")
        
        page.fill('input[name="meta_keyword"]', meta_keywords)
        
        publish_time = "12-11-2026 10:00"
        page.evaluate("""(timeVal) => {
            const el = document.querySelector('input[name="published_at"]');
            if (el) {
                el.value = timeVal;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""", publish_time)
        print(f"  [CMS] Đã đặt lịch xuất bản: {publish_time}")
        
        chk = page.locator('input[name="is_published"]')
        if chk.count() > 0 and not chk.is_checked():
            chk.check()
            
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
        
        html_raw = """<p>Trong thi công nội thất hiện đại, đặc biệt ở các hạng mục tủ bếp, tủ lavabo và hệ tủ áo cao cấp, chất lượng đường dán cạnh và độ sắc nét của tay nắm âm quyết định trực tiếp đến đẳng cấp công trình. Đối với các xưởng mộc và đơn vị thiết kế thi công, tình trạng hở mí keo, lộ đường chỉ đen mất thẩm mỹ hoặc nứt gãy nẹp khi gia công tay nắm vát cạnh luôn là bài toán kỹ thuật nan giải. Công nghệ dán cạnh <strong>PUR Noline (Zero-joint)</strong> kết hợp hệ thống phay vát và dán cạnh nghiêng 45 độ tự động tại <strong>Happyco</strong> giải quyết triệt để các khuyết điểm bề mặt, nâng chuẩn hoàn thiện phôi ván công nghiệp ngang tầm các dây chuyền nhà máy quy mô lớn.</p>

<p style="text-align: center; margin: 20px 0;"><img src="{IMG_THUMB}" alt="Toàn cảnh dây chuyền máy dán cạnh tự động hiện đại tại xưởng gia công gỗ công nghiệp Happyco Đồng Nai" style="width: 100%; max-width: 800px; border-radius: 8px;" /><br /><em style="color: #666; font-size: 14px;">Hệ thống dây chuyền dán cạnh tự động công suất lớn tại xưởng gia công Happyco (Biên Hòa, Đồng Nai).</em></p>

<h2>1. Khắc phục triệt để đường chỉ đen của keo EVA: Sức mạnh liên kết của keo PUR Noline (Zero-joint)</h2>

<p>Trong nhiều năm, keo nhiệt dẻo EVA (Ethylene Vinyl Acetate) là lựa chọn phổ biến tại các xưởng sản xuất nhờ chi phí thấp và dễ vận hành. Tuy nhiên, bản chất keo EVA đòi hỏi nhiệt độ nóng chảy cao (khoảng 180°C – 200°C) và tạo ra lớp màng keo có độ dày tương đối lớn tại khe tiếp giáp giữa cốt ván và chỉ nẹp nhựa. Khi hoàn thiện trên các mã ván Melamine hay bề mặt tông sáng (trắng sứ, xám nhạt, kem pastel), khe keo dày 0.15mm – 0.3mm dễ dàng bám bụi mịn và dầu mỡ theo thời gian, hình thành <strong>"đường chỉ đen"</strong> rất dễ nhận thấy bằng mắt thường.</p>

<p>Công nghệ dán cạnh <strong>keo PUR (Polyurethane Reactive)</strong> tại Happyco khắc phục hoàn toàn giới hạn này nhờ cơ chế đóng rắn phản ứng hóa học:</p>

<ul>
  <li><strong>Đường dán siêu mảnh Noline (Zero-joint):</strong> Nhờ độ nhớt tối ưu và đầu phun định lượng chính xác kết hợp cụm dao phay trích (pre-milling) làm phẳng tuyệt đối mép cắt trước khi ép, lượng keo PUR phủ lên cạnh ván cực mỏng và đồng đều.</li>
  <li><strong>Liên kết ngang kháng nước và chịu nhiệt vượt trội:</strong> Keo PUR tạo thành cấu trúc mạng lưới polymer bền vững, không bị nóng chảy trở lại, chịu nhiệt lên đến 150°C và chống thấm nước xâm nhập vào lõi ván tuyệt đối.</li>
  <li><strong>Giữ nguyên sắc độ đồng bộ của cánh tủ:</strong> Loại bỏ hoàn toàn hiện tượng ố vàng hoặc bám bẩn đen viền cạnh trên các dòng ván đơn sắc hiện đại.</li>
</ul>

<p style="text-align: center; margin: 20px 0;"><img src="{IMG_H2_1}" alt="Cận cảnh đường mép ván gỗ công nghiệp dán cạnh keo PUR Noline khít tuyệt đối không lộ vết keo" style="width: 100%; max-width: 800px; border-radius: 8px;" /><br /><em style="color: #666; font-size: 14px;">Mép ván gỗ công nghiệp sau khi dán keo PUR Noline kín khít tuyệt đối, không lộ đường chỉ đen.</em></p>

<h2>2. Gia công phay vát tay nắm âm J-K liền khối bằng hệ thống tự động: Thẩm mỹ tối giản &amp; Cầm nắm êm tay</h2>

<p>Xu hướng nội thất tối giản hiện đại ưu tiên các hệ cánh tủ phẳng không tay nắm nổi nhằm tạo sự liền mạch cho mặt đứng kiến trúc và đảm bảo an toàn va chạm trong sinh hoạt. Tại Happyco, quy trình <strong>phay vát tay nắm âm J và K liền khối</strong> được thực hiện trực tiếp trên phôi ván công nghiệp (MDF lõi xanh chống ẩm HMR, HDF, Plywood độ dày 17mm – 25mm) bằng hệ thống gia công tự động:</p>

<ul>
  <li><strong>Biên dạng vát chữ J (J-Pull):</strong> Tạo hốc móc tay bo cong mềm mại dọc theo cạnh cánh tủ, giúp ngón tay tiếp xúc tự nhiên với lực kéo nhẹ nhàng.</li>
  <li><strong>Biên dạng vát chữ K (K-Pull / Vát 45 độ kết hợp rãnh ngậm):</strong> Đường cắt vát sắc sảo tạo khe hở chuẩn kỹ thuật giữa hai cánh tủ, đảm bảo độ bám chắc chắn khi đóng mở cánh kích thước lớn.</li>
  <li><strong>Độ chính xác và đồng nhất hàng loạt:</strong> Dao phay kim cương chuyên dụng chạy ở tốc độ cao giúp bề mặt vát mịn tuyệt đối, không bị xơ lõi MDF hay mẻ dăm lớp phủ Melamine.</li>
</ul>

<p style="text-align: center; margin: 20px 0;"><img src="{IMG_H2_2}" alt="Cận cảnh cánh tủ gỗ công nghiệp phay vát cạnh tay nắm âm chữ J và chữ K phủ Melamine mịn" style="width: 100%; max-width: 800px; border-radius: 8px;" /><br /><em style="color: #666; font-size: 14px;">Chi tiết cánh tủ vát tay nắm âm J-K sắc nét, bề mặt vát mịn không ba-via, sẵn sàng lắp đặt hoàn thiện.</em></p>

<h2>3. Dây chuyền máy dán cạnh vát nghiêng 45 độ chuyên dụng tại Happyco: Xử lý nẹp PVC/ABS đồng màu không hở mí</h2>

<p>Nếu thực hiện dán thủ công hoặc ép nhiệt trên các dòng máy dán cạnh thẳng thông thường, nẹp PVC/ABS ở cạnh vát rất dễ bị gãy gập tại góc chuyển tiếp hoặc hở mí keo. Happyco đầu tư đồng bộ <strong>dây chuyền máy dán cạnh vát nghiêng 45 độ tự động đa chức năng</strong> chuyên biệt:</p>

<ol>
  <li><strong>Gia công phay tinh đồng bộ mặt nghiêng và mặt thẳng:</strong> Phôi ván định vị chuẩn xác 45 độ trên băng tải dẫn hướng.</li>
  <li><strong>Lăn keo PUR đồng đều trên hai bề mặt góc:</strong> Cụm nồi keo chuyên dụng phân bổ lớp keo PUR mỏng mịn phủ kín phần cạnh nghiêng lẫn mép nối.</li>
  <li><strong>Ép nẹp qua cụm con lăn góc nghiêng đa điểm:</strong> Dải nẹp PVC/ABS đồng màu ôm khít bề mặt cốt ván, loại bỏ hoàn toàn bọt khí hay hiện tượng hở mí.</li>
  <li><strong>Xén tinh, cạo keo và đánh bóng tự động:</strong> Xử lý gọn phần nẹp thừa tại giao điểm góc, chổi vải đánh bóng giúp mép tiếp giáp mượt mà đồng nhất màu sắc.</li>
</ol>

<p style="text-align: center; margin: 20px 0;"><img src="{IMG_H2_3}" alt="Cụm máy dán cạnh tự động đa chức năng vát nghiêng 45 độ đang chạy nẹp chỉ PVC qua con lăn ép" style="width: 100%; max-width: 800px; border-radius: 8px;" /><br /><em style="color: #666; font-size: 14px;">Cụm con lăn ép trên máy dán cạnh vát nghiêng 45 độ tự động đang xử lý nẹp chỉ PVC đồng màu.</em></p>

<h2>4. Chia sẻ hạ tầng máy móc hiện đại cho xưởng mộc: Tiết kiệm vốn đầu tư, nhận file ABF trả phôi hoàn thiện trong 24h-48h</h2>

<p>Thấu hiểu bài toán chi phí đầu tư thiết bị nặng của anh em xưởng mộc vừa và nhỏ, Happyco triển khai mô hình <strong>chia sẻ hạ tầng máy móc gia công B2B chuyên nghiệp</strong> tại khu vực Đồng Nai, Bình Dương, TP.HCM và các tỉnh lân cận:</p>

<ul>
  <li><strong>Tiếp nhận trực tiếp file thiết kế ABF và dữ liệu Nesting:</strong> Nhận file từ SketchUp ABF, PolyBoard, Bazis hoặc Excel cắt ván, kiểm tra chéo thông số trước khi đưa vào gia công.</li>
  <li><strong>Quản lý phôi bằng hệ thống tem mã vạch thông minh:</strong> Mỗi chi tiết đều dán tem định danh rõ kích thước, tên cấu kiện, vị trí dán cạnh giúp thợ lắp ráp rút ngắn 60% thời gian gia công thủ công.</li>
  <li><strong>Cam kết tiến độ trả phôi nhanh từ 24h – 48h:</strong> Quy trình khép kín giúp đảm bảo tiến độ bàn giao gấp cho các công trình căn hộ, biệt thự.</li>
</ul>

<p style="text-align: center; margin: 20px 0;"><img src="{IMG_H2_4}" alt="Thợ kỹ thuật xưởng mộc Happyco kiểm tra kích thước, dán tem mã vạch lên cánh tủ vát tay nắm xếp pallet" style="width: 100%; max-width: 800px; border-radius: 8px;" /><br /><em style="color: #666; font-size: 14px;">Kỹ thuật viên Happyco kiểm tra dung sai kích thước, dán tem mã vạch định danh trước khi đóng kiện bàn giao cho xưởng đối tác.</em></p>"""

        final_html = html_raw.replace("{IMG_THUMB}", cdn_urls[0]) \
                             .replace("{IMG_H2_1}", cdn_urls[1]) \
                             .replace("{IMG_H2_2}", cdn_urls[2]) \
                             .replace("{IMG_H2_3}", cdn_urls[3]) \
                             .replace("{IMG_H2_4}", cdn_urls[4])
                             
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
        }""", {"desc": description, "content": final_html})
        
        page.wait_for_timeout(1000)
        
        page.evaluate("""() => {
            for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
            let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
            if (btn) btn.click();
        }""")
        page.wait_for_timeout(5000)
        
        print("\n[Con Tổng] Kiểm tra nghiệm thu danh sách bài viết trên CMS...")
        page.goto("https://happyco.asia/admin/post", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        first_row = page.locator("table tbody tr").first
        post_title = first_row.locator("td").nth(1).inner_text().strip()
        post_cat = first_row.locator("td").nth(2).inner_text().strip()
        post_time = first_row.locator("td").nth(4).inner_text().strip() if first_row.locator("td").count() > 4 else "N/A"
        
        print(f"  -> Bài đăng mới nhất: {post_title}")
        print(f"  -> Chuyên mục: {post_cat}")
        print(f"  -> Trạng thái & Giờ hẹn: {post_time}")
        
        proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_b2b_10h_scheduled_proof.png"
        page.screenshot(path=proof_path)
        print(f"📸 ĐÃ LƯU BẰNG CHỨNG LÊN LỊCH 10H: {proof_path}")
        browser.close()
        
    total_time = int(time.time() - start_total)
    print("\n==================================================================")
    print(f"🎉 HOÀN TẤT XUẤT BẢN BÀI B2B LÊN LỊCH 10H TRONG TỔNG THỜI GIAN: {total_time}s!")
    print("==================================================================")

if __name__ == "__main__":
    run()
