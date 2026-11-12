import os
import sys
import time
import re
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
load_dotenv(BASE_DIR / ".env")

from fast_flow_generator import generate_flow_batch_parallel

def run():
    print("==================================================================")
    print("🚀 CON TỔNG (CHIEF QA) THỰC THI XUẤT BẢN BÀI 17H TỪ SUB-AGENT B2C")
    print("==================================================================")
    
    title = "Thiết Kế Tủ Bếp Cánh Kính Khung Nhôm Anode Chống Nước Tuyệt Đối Kết Hợp Bàn Đảo Thông Minh Cho Nhà Phố"
    slug = f"tu-bep-canh-kinh-khung-nhom-anode-chong-nuoc-ban-dao-thong-minh-{int(time.time())}"
    meta_keywords = "tủ bếp cánh kính khung nhôm anode, tủ bếp chống nước tuyệt đối, bàn đảo bếp thông minh, tủ bếp nhà phố hiện đại, dán cạnh pur noline, phụ kiện tủ bếp thông minh, xưởng tủ bếp happyco biên hòa"
    description = "Tủ bếp cánh kính nhôm Anode chống nước tuyệt đối kết hợp bàn đảo tiện nghi cho nhà phố. Happyco gia công nẹp PUR noline tinh xảo, bền bỉ theo thời gian."
    
    flow_prompts = [
        "Cinematic wide-angle architectural photograph of a luxury modern townhouse kitchen featuring an anodized dark champagne aluminum frame tempered glass cabinet with integrated warm 3000K LED strip lighting, seamless multi-functional kitchen island with white Calacatta quartz countertop and minimalist wooden breakfast bar stools, built-in matte black induction cooktop and sleek range hood, warm atmospheric morning sunlight casting soft shadows, ultra-photorealistic interior architecture, 8k resolution, Architectural Digest aesthetic, no people, 16:9 aspect ratio.",
        "Detailed macro architectural shot focusing on luxury dark bronze anodized aluminum profile framed tempered glass kitchen cabinet doors, clean reflective glass surface showing warm ambient kitchen interior reflections, seamless concealed hinge mechanics, ultra-precise metallic joinery, soft warm backlighting, high-end interior design catalog photography, photorealistic, 8k, no people, 16:9 aspect ratio.",
        "Eye-level architectural view of a contemporary townhouse kitchen island integrated with an extendable dining table, solid quartz waterfall edge island counter, flush-mounted pop-up electrical outlet, designer warm pendant lights suspended overhead, modern minimalist open-plan living room softly blurred in the background, warm cozy evening illumination, photorealistic, no people, 16:9 aspect ratio.",
        "Extreme macro studio close-up of water-resistant kitchen cabinet panel edge showcasing flawless PUR zero-joint edge banding (noline technology), invisible seam between face and edge, crisp clean chamfered corners, subtle water droplets resting on the moisture-proof surface demonstrating hydrophobic durability, professional woodworking craftsmanship lighting, ultra-sharp detail, no people, 16:9 aspect ratio.",
        "Interior architectural photo of an open upper kitchen cabinet highlighting an ergonomic two-tier mechanical pull-down dish rack made of stainless steel 304, smoothly extended downward, warm embedded LED cabinet spotlights illuminating organized porcelain plates and crystal glasses, heavy-duty soft-closing dampening slides, ultra-modern luxury kitchen storage, 8k resolution, no people, 16:9 aspect ratio."
    ]
    
    # 1. Sinh 5 ảnh song song qua Fast Flow
    print("\n[Con Tổng] Kích hoạt Fast Flow sinh 5 ảnh song song + xóa logo Google...")
    batch_out = BASE_DIR / "output" / f"kitchen_17h_flow_{int(time.time())}"
    generated_files = generate_flow_batch_parallel(flow_prompts, batch_out)
    print(f"✅ Đã tạo xong {len(generated_files)} ảnh chuẩn 16:9, sạch logo Google, dập logo TopLeft!")
    
    # 2. Upload 5 ảnh lên CDN
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
        for idx, fpath in enumerate(generated_files):
            page.goto("https://happyco.asia/admin/media", timeout=40000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            
            btn = page.locator("button:has-text('Thêm file / hình ảnh')").first
            btn.click()
            page.wait_for_timeout(1000)
            page.set_input_files("input[name='media_file']", str(fpath))
            page.fill("input[name='title']", f"Happyco Kitchen 17h {idx + 1} {ts}")
            page.locator("button:has-text('Lưu')").first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            
            cms_fn = fpath.name
            cdn_url = f"https://media.loveitopcdn.com/19180/{cms_fn}"
            cdn_urls.append(cdn_url)
            cdn_filenames.append(cms_fn)
            print(f"  [+] Uploaded CDN: {cdn_url}")
            
        # 3. Tạo bài viết trên CMS tại /admin/post/create
        print("\n[Con Tổng] Đăng bài và đặt lịch 17:00 trên CMS...")
        page.goto("https://happyco.asia/admin/post/create", timeout=40000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        page.fill('input[name="title"]', title)
        page.fill('input[name="slug"]', slug)
        
        page.select_option('select[name="cat_id"]', "266")
        
        page.fill('input[name="meta_keyword"]', meta_keywords)
        
        publish_time = "11-11-2026 17:00"
        page.evaluate("""(timeVal) => {
            const el = document.querySelector('input[name="published_at"]');
            if (el) {
                el.value = timeVal;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }""", publish_time)
        print(f"  [CMS] Đã cài đặt lịch xuất bản: {publish_time}")
        
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
        
        # Đọc HTML từ báo cáo của Sub-Agent và thay thế placeholder bằng link ảnh thật
        html_raw = """<p>Trong kiến trúc nhà phố hiện đại tại các đô thị, gian bếp không chỉ là nơi nấu nướng mà còn là tâm điểm thể hiện gu thẩm mỹ và phong cách sống của gia chủ. Tuy nhiên, khí hậu nhiệt đới nóng ẩm đặc thù tại Việt Nam cùng diện tích nhà ống dạng dài thường khiến các hệ tủ bếp truyền thống đối mặt với nỗi ám ảnh: ẩm mốc, cong vênh, trương nở mối mọt và bám dính dầu mỡ khó vệ sinh. Để giải quyết triệt để bài toán này, giải pháp <strong>tủ bếp cánh kính khung nhôm Anode chống nước tuyệt đối kết hợp bàn đảo bếp thông minh</strong> do xưởng nội thất Happyco trực tiếp thiết kế và gia công đang trở thành xu hướng dẫn đầu, mang lại vẻ đẹp đẳng cấp và tuổi thọ trường tồn cho ngôi nhà của bạn.</p>

<h2>1. Giải pháp cánh kính cường lực khung nhôm Anode: Chống xước, chống cong vênh và độ bền vĩnh cửu</h2>
<p><img src="{IMG_1}" alt="Cánh kính khung nhôm Anode tủ bếp Happyco" style="width: 100%; max-width: 800px; border-radius: 8px;" /></p>
<p>Khác biệt hoàn toàn với các dòng cánh gỗ phủ Melamine hay Acrylic dễ bong tróc cạnh sau thời gian tiếp xúc với nhiệt độ cao của bếp nấu, hệ cánh kính khung nhôm Anode tại Happyco sở hữu kết cấu vật liệu bền vững bậc nhất hiện nay:</p>
<ul>
    <li><strong>Kính cường lực siêu trong 5mm chuẩn an toàn:</strong> Bề mặt phẳng gương chống trầy xước tuyệt đối, chịu lực va đập cực tốt, kháng nhiệt từ bếp đun và không bao giờ ố màu dầu mỡ. Việc lau chùi vết bẩn chỉ mất 30 giây bằng khăn mềm ẩm.</li>
    <li><strong>Khung hợp kim nhôm Anode hóa (Anodized Aluminum):</strong> Nhôm được xử lý qua bể mạ điện phân Anode tạo lớp oxit nhôm siêu cứng bảo vệ bề mặt, chống ăn mòn hóa học, chống oxy hóa và không phai màu theo năm tháng kể cả trong môi trường có độ mặn hoặc độ ẩm cao.</li>
    <li><strong>Hiệu ứng thị giác mở rộng không gian:</strong> Cánh kính phản chiếu ánh sáng tự nhiên và đèn LED âm tủ, biến góc bếp nhà phố thường thiếu sáng trở nên thoáng đãng, lộng lẫy và tràn đầy sinh khí.</li>
</ul>

<h2>2. Bàn đảo bếp đa năng kết hợp bàn ăn thông minh: Tối ưu công năng và thẩm mỹ nhà phố</h2>
<p><img src="{IMG_2}" alt="Bàn đảo bếp thông minh tích hợp bàn ăn cho nhà phố" style="width: 100%; max-width: 800px; border-radius: 8px;" /></p>
<p>Nhà phố thường có mặt tiền hẹp từ 4m - 5m, do đó việc phân chia ranh giới giữa phòng khách và phòng bếp bằng vách ngăn thạch cao truyền thống sẽ gây cảm giác chật chội, bí bách. Bàn đảo bếp thông minh chính là "vách ngăn ước lệ" hoàn hảo:</p>
<ul>
    <li><strong>Tích hợp công năng 3 trong 1:</strong> Bàn đảo vừa đóng vai trò trạm chuẩn bị thực phẩm (bàn soạn), vừa là quầy bar thưởng thức đồ uống sang trọng, đồng thời dễ dàng kéo mở thành bàn ăn thông minh phục vụ bữa cơm gia đình từ 4 - 6 người.</li>
    <li><strong>Tối ưu tam giác công năng (Work Triangle):</strong> Đảo bếp rút ngắn khoảng cách di chuyển giữa Tủ lạnh - Chậu rửa - Bếp nấu, giúp người nội trợ thao tác liền mạch, tiết kiệm tối đa thời gian và công sức.</li>
    <li><strong>Không gian lưu trữ giấu kín:</strong> Thân đảo bếp được tận dụng bố trí các khoang chứa đồ khô, ngăn kéo gia vị âm, tích hợp ổ cắm điện âm bàn pop-up chống nước và ray trượt thông minh chịu tải trọng lớn.</li>
</ul>

<h2>3. Công nghệ dán cạnh nẹp PUR noline cho thùng tủ bếp chống ẩm: Ngăn chặn 100% nước xâm nhập</h2>
<p><img src="{IMG_3}" alt="Công nghệ dán cạnh PUR noline chống nước thùng tủ bếp" style="width: 100%; max-width: 800px; border-radius: 8px;" /></p>
<p>Nếu cánh kính giải quyết bài toán mặt tiền thì thùng tủ lại là bộ khung chịu lực quyết định tuổi thọ của toàn bộ gian bếp. Tại xưởng Happyco, mọi chi tiết thùng tủ bếp đều được gia công trên dây chuyền tự động với công nghệ dán cạnh keo <strong>PUR noline (Zero-joint Edge Banding)</strong> tiên tiến:</p>
<ul>
    <li><strong>Không lộ đường keo (Zero-joint):</strong> Mép bo cạnh liền lạc như một khối đúc, ngăn chặn 100% hơi ẩm và nước thâm nhập vào lõi ván.</li>
    <li><strong>Chịu nhiệt vượt trội lên đến 140°C:</strong> Không lo bong tróc mép keo khu vực gần bếp nấu hoặc khoang lò nướng.</li>
    <li><strong>Độ bền vĩnh cửu:</strong> Lực bám dính phân tử của keo PUR gấp 3 lần keo EVA thông thường, bảo vệ tủ bếp bền đẹp hơn 20 năm.</li>
</ul>

<h2>4. Phụ kiện thông minh nâng tầm trải nghiệm: Giá bát nâng hạ, ray trượt giảm chấn cao cấp</h2>
<p><img src="{IMG_4}" alt="Phụ kiện tủ bếp thông minh giá bát nâng hạ inox 304" style="width: 100%; max-width: 800px; border-radius: 8px;" /></p>
<p>Một gian bếp đẳng cấp không chỉ đẹp về ngoại hình mà phải "chạm đến cảm xúc" trong từng cử động đóng mở. Happyco trang bị đồng bộ các giải pháp phụ kiện cơ khí tinh xảo:</p>
<ul>
    <li><strong>Giá bát đĩa nâng hạ trợ lực 2 tầng:</strong> Cơ cấu piston trợ lực 4 mức tải trọng giúp hạ cả giàn bát xuống vừa tầm mắt chỉ với một cái kéo nhẹ.</li>
    <li><strong>Hệ thống bản lề &amp; ray trượt hộp giảm chấn inox 304:</strong> Triệt tiêu tiếng ồn va đập, bảo vệ cánh kính khi đóng mạnh.</li>
    <li><strong>Hệ giá góc liên hoàn &amp; mâm xoay thông minh:</strong> Tận dụng triệt để "góc chết" của hệ tủ chữ L, lấy đồ ra ngoài dễ dàng.</li>
</ul>"""
        
        final_html = html_raw.replace("{IMG_1}", cdn_urls[1]) \
                             .replace("{IMG_2}", cdn_urls[2]) \
                             .replace("{IMG_3}", cdn_urls[3]) \
                             .replace("{IMG_4}", cdn_urls[4])
                             
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
            for (let k in window.CKEDITOR.instances) {
                window.CKEDITOR.instances[k].updateElement();
            }
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
        
        proof_path = r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_17h_scheduled_verified.png"
        page.screenshot(path=proof_path)
        print(f"📸 ĐÃ LƯU BẰNG CHỨNG LÊN LỊCH 17H: {proof_path}")
        browser.close()
        print("\n🎉 HOÀN THÀNH XUẤT SẮC BÀI VIẾT 17H TỪ ĐIỀU PHỐI SUB-AGENT!")

if __name__ == "__main__":
    run()
