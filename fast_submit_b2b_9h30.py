import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

cdn_filenames = {
    "thumb": "happyco_b2b_cnc_thumb_1794363749.jpg",
    "h2_1": "happyco_b2b_cnc_h2_1_1794363749.jpg",
    "h2_2": "happyco_b2b_cnc_h2_2_1794363749.jpg",
    "h2_3": "happyco_b2b_cnc_h2_3_1794363749.jpg",
    "h2_4": "happyco_b2b_cnc_h2_4_1794363749.jpg",
}

cdn_urls = {k: f"https://media.loveitopcdn.com/19180/{fn}" for k, fn in cdn_filenames.items()}

title = "Gia Công Ván MDF Chống Ẩm Phủ Melamine: Dây Chuyền CNC Nesting & Tối Ưu Phôi Ván Tiết Kiệm 15% Chi Phí Cho Xưởng Mộc Tại Happyco"
slug = "gia-cong-van-mdf-chong-am-phu-melamine-cnc-nesting-happyco"
description = "Giải pháp gia công ván MDF chống ẩm phủ Melamine tối ưu phôi ván, tiết kiệm 15% chi phí tại xưởng mộc Happyco với công nghệ CNC Nesting và dán cạnh PUR noline."

content_html = f"""<p style="text-align: justify; font-size: 16px; line-height: 1.8;">Trong bối cảnh ngành sản xuất nội thất gỗ công nghiệp ngày càng cạnh tranh gay gắt, bài toán tối ưu chi phí nguyên vật liệu và đảm bảo tiến độ bàn giao công trình luôn là ưu tiên hàng đầu của các xưởng mộc và nhà thầu nội thất. Việc đầu tư dàn máy chế biến gỗ công nghiệp nặng đòi hỏi nguồn vốn hàng tỷ đồng cùng chi phí vận hành bảo dưỡng tốn kém. Do đó, giải pháp hợp tác cùng xưởng <strong>gia công ván MDF chống ẩm phủ Melamine</strong> chuyên nghiệp tại <a href="https://happyco.asia/gioi-thieu.html" style="color: #008848; font-weight: bold; text-decoration: underline;">Happyco</a> đang trở thành lựa chọn tối ưu, giúp thầu thợ giải phóng mặt bằng, giảm thiểu hao hụt phôi ván lên tới 15% và triệt tiêu hoàn toàn rủi ro sai lệch kích thước.</p>

<h2 style="color: #1e3a8a; font-size: 20px; margin-top: 25px;">1. Công Nghệ CNC Nesting 4 Đầu: Tối Ưu Hóa Phôi Ván Tiết Kiệm 15% Chi Phí</h2>
<p style="text-align: justify; font-size: 16px; line-height: 1.8;">Tại xưởng gia công Happyco, dây chuyền máy phay cắt CNC Nesting đa trục tốc độ cao được lập trình tự động hóa qua phần mềm xếp phôi thông minh. Thuật toán tối ưu sắp xếp các chi tiết cắt sát khít nhau trên bề mặt tấm ván tiêu chuẩn 1220 x 2440mm, giảm tối đa diện tích đề xê (vụn gỗ thừa). Nhờ sử dụng lưỡi dao phay hợp kim carbide chuyên dụng kết hợp hệ thống hút chân không công suất lớn, đường cắt đạt độ mịn phẳng tuyệt đối, triệt tiêu 100% hiện tượng mẻ viền Melamine.</p>

<p style="text-align: center; margin: 25px 0;">
  <img src="{cdn_urls['h2_1']}" alt="Gia công ván MDF chống ẩm bằng máy CNC Nesting tại xưởng Happyco" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />
  <br />
  <em style="color: #666; font-size: 14px; margin-top: 8px; display: inline-block;">Dây chuyền cắt CNC Nesting tự động hóa phôi ván MDF chống ẩm tại xưởng sản xuất Happyco</em>
</p>

<h2 style="color: #1e3a8a; font-size: 20px; margin-top: 25px;">2. Kỹ Thuật Dán Cạnh PUR Noline: Chống Nước Tuyệt Đối & Thẩm Mỹ Không Vết Keo</h2>
<p style="text-align: justify; font-size: 16px; line-height: 1.8;">Khác biệt hoàn toàn với các dòng keo dán nhiệt EVA truyền thống thường để lại đường chỉ đen lem nhem và dễ bong tróc khi gặp độ ẩm cao, Happyco áp dụng đồng bộ công nghệ keo dán PUR chống thấm nước chuyên sâu. Mối liên kết giữa nẹp chỉ PVC và cốt ván MDF lõi xanh kín khít tuyệt đối, không lộ đường keo (noline), ngăn chặn hoàn toàn nước xâm nhập vào lõi ván ngay cả trong môi trường tủ bếp ẩm ướt hoặc tủ lavabo nhà tắm.</p>

<p style="text-align: center; margin: 25px 0;">
  <img src="{cdn_urls['h2_2']}" alt="Kỹ thuật dán chỉ nẹp PUR Noline chống nước mép ván công nghiệp" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />
  <br />
  <em style="color: #666; font-size: 14px; margin-top: 8px; display: inline-block;">Hệ thống dán cạnh keo PUR noline không đường keo bảo vệ tối đa mép cốt ván</em>
</p>

<h2 style="color: #1e3a8a; font-size: 20px; margin-top: 25px;">3. Khoan Cam Chốt & Phay Rãnh Bản Lề Tự Động Theo File Thiết Kế ABF</h2>
<p style="text-align: justify; font-size: 16px; line-height: 1.8;">Để hỗ trợ các đơn vị thi công lắp ráp nhanh chóng tại công trình mà không cần mang theo máy móc cồng kềnh, hệ thống máy khoan liên kết ngang dọc tự động của Happyco xử lý chính xác 100% vị trí cam chốt, chốt gỗ, rãnh âm LED và rãnh trượt ngăn kéo. Mọi dữ liệu gia công được đồng bộ trực tiếp từ file thiết kế 3D (ABF, SketchUp, Cabinet Vision), kiểm soát dung sai dưới 0.2mm, giúp việc lắp ráp liên kết khung thùng tủ trở nên dễ dàng và chuẩn xác tuyệt đối.</p>

<p style="text-align: center; margin: 25px 0;">
  <img src="{cdn_urls['h2_3']}" alt="Kiểm tra độ chính xác dung sai chi tiết ván sau gia công bằng thước kẹp" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />
  <br />
  <em style="color: #666; font-size: 14px; margin-top: 8px; display: inline-block;">Kiểm định độ dày và rãnh liên kết cam chốt với dung sai cơ khí dưới 0.2mm</em>
</p>

<h2 style="color: #1e3a8a; font-size: 20px; margin-top: 25px;">4. Đóng Gói Mã Vạch Barcode Thông Minh & Giao Nhận Tận Nơi Toàn Miền Nam</h2>
<p style="text-align: justify; font-size: 16px; line-height: 1.8;">Mỗi tấm phôi sau khi gia công hoàn thiện đều được dán tem nhãn mã vạch định danh rõ ràng: tên module, vị trí lắp đặt, kích thước thực tế và tên phòng chức năng. Thợ mộc chỉ cần quét mã hoặc nhìn tem là phân loại lắp ráp ngay mà không lo nhầm lẫn. Phôi ván được bọc màng co PE bảo vệ góc cẩn thận, sắp xếp ngay ngắn trên pallet chuyên dụng và vận chuyển tận nơi tới công trình hoặc xưởng của đối tác đúng hẹn.</p>

<p style="text-align: center; margin: 25px 0;">
  <img src="{cdn_urls['h2_4']}" alt="Phôi ván công nghiệp hoàn thiện được dán tem mã vạch và đóng gói pallet cẩn thận" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />
  <br />
  <em style="color: #666; font-size: 14px; margin-top: 8px; display: inline-block;">Phôi ván thành phẩm được dán nhãn định danh và đóng gói màng bảo vệ trước khi xuất xưởng</em>
</p>

<div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 14px 18px; margin: 20px 0; border-radius: 0 8px 8px 0; font-size: 15px; color: #166534; line-height: 1.6;">
  💡 <em>Xem thêm:</em> Quý đối tác xưởng có thể tham khảo thêm giải pháp <a href="https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-plywood-phu-melamine.html" style="color: #15803d; font-weight: bold; text-decoration: underline;">gia công Plywood phủ Melamine dán nẹp PUR</a> | <a href="https://happyco.asia/dich-vu/gia-cong-van-hmr-phu-melamine-theo-file-abf-tai-bien-hoa.html" style="color: #15803d; font-weight: bold; text-decoration: underline;">gia công ván HMR theo file ABF</a> hoặc tham khảo thêm tại <a href="https://happyco.asia/blog.html" style="color: #15803d; font-weight: bold; text-decoration: underline;">cẩm nang chuyên ngành mộc</a> tại xưởng Happyco.
</div>

<div style="border: 2px dashed #008848; background: #f6fff9; border-radius: 8px; padding: 18px 22px; margin: 28px 0;">
  <p style="color: #008848; font-weight: bold; margin: 0 0 8px 0; font-size: 16px;">Chúng Tôi Nhận Thiết Kế Nội Thất Ngành Mộc Tại Các Khu Vực Sau:</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">- Miền Nam: Thành phố Hồ Chí Minh, Đồng Nai, Tây Ninh, Thành phố Cần Thơ, Vĩnh Long, Đồng Tháp, Cà Mau, An Giang.</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">📍 <strong>Địa chỉ công ty:</strong> 526/2, Khu phố 8A, Phường Long Bình, thành phố Đồng Nai.</p>
  <p style="margin: 6px 0; color: #d32f2f; font-weight: bold; font-size: 16px;">📞 Liên hệ: 0946 272 286 (Đức Anh)</p>
</div>"""

print("Khởi chạy Playwright submit bài viết...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
    password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")
    page.goto("https://happyco.asia/admin/login", timeout=40000)
    page.fill("input[name='email']", email)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)
    print("Đăng nhập thành công!")

    page.goto("https://happyco.asia/admin/post/create", timeout=40000)
    page.wait_for_selector('input[name="title"]', timeout=30000)

    page.fill('input[name="title"]', title)
    page.fill('input[name="slug"]', slug)
    page.fill('input[name="meta_keyword"]', 'gia công ván mdf, cnc nesting happyco, gia công gỗ công nghiệp biên hòa')
    page.fill('input[name="meta_title"]', title)
    page.fill('textarea[name="meta_description"]', description)

    # Chọn chuyên mục 265
    page.select_option('select[name="cat_id"]', "265")
    print("Đã chọn chuyên mục ID 265 (GIA CÔNG VÁN CÔNG NGHIỆP)")

    # Thumbnail
    thumb_fn = cdn_filenames["thumb"]
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
    print("Đã gắn thumbnail:", thumb_fn)

    # Đặt lịch 11-11-2026 09:30
    page.evaluate("""() => {
        let el = document.querySelector('input[name="published_at"]');
        if (el) {
            el.value = "11-11-2026 09:30";
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }""")
    print("Đã đặt lịch đăng: 11-11-2026 09:30")

    chk = page.locator('input[name="is_published"]')
    if chk.count() > 0 and not chk.is_checked():
        chk.check()

    # CKEditor
    page.evaluate("""({desc, content}) => {
        if (window.CKEDITOR && window.CKEDITOR.instances) {
            for (let id in window.CKEDITOR.instances) {
                let el = document.getElementById(id);
                let inst = window.CKEDITOR.instances[id];
                if (el && el.name === 'description') {
                    inst.setData(desc);
                    inst.updateElement();
                    el.value = desc;
                }
                if (el && el.name === 'content') {
                    inst.setData(content);
                    inst.updateElement();
                    el.value = content;
                }
            }
        }
    }""", {"desc": description, "content": content_html})

    page.wait_for_timeout(1000)

    tags_input = page.locator('input[name="tags"]')
    if tags_input.count() > 0:
        tags_input.fill("gia công ván mdf, cnc nesting happyco, gia công nội thất biên hòa đồng nai")

    # Lưu bài viết
    print("Bấm Lưu bài viết...")
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
    page.wait_for_timeout(6000)

    # Kiểm tra
    page.goto("https://happyco.asia/admin/post", timeout=40000)
    page.wait_for_selector("table", timeout=30000)

    first_row = page.locator("table tbody tr").first
    row_text = first_row.inner_text().replace("\n", " | ")
    print(f"\n[CMS Post List] Bài viết đầu tiên:\n{row_text}")

    screenshot_path = BASE_DIR / "output" / "b2b_9h30_cms_verified.png"
    page.screenshot(path=str(screenshot_path))
    print(f"Đã chụp ảnh xác thực: {screenshot_path.name}")

    browser.close()
    print("\n🎉 XUẤT BẢN THÀNH CÔNG!")
