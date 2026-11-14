import os
import sys
import json
import re
from pathlib import Path

# Set UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster")
sys.path.insert(0, str(BASE_DIR))

from core.topic_memory import ensure_green_box
from agents.chief_qa_agent import ChiefQAAgent

title = "5 Lỗi Xuất File ABF SketchUp Khi Cắt CNC Làm Hao Phôi Ván Và Cách Khắc Phục Chuẩn Kỹ Thuật"
slug = "5-loi-xuat-file-abf-sketchup-khi-cat-cnc-lam-hao-phoi-van"
description = "Tổng hợp 5 lỗi kỹ thuật thường gặp khi xuất file SketchUp ABF cắt CNC khiến hao phôi ván và giải pháp thiết lập layer chuẩn xác cho xưởng sản xuất nội thất."
keywords = "lỗi xuất file abf sketchup cắt cnc, gia công ván theo file abf, cắt cnc nesting tấm 1220x2440, xưởng gia công happyco, phần mềm abf sketchup"

content_html = """<p>Trong quy trình sản xuất nội thất gỗ công nghiệp hiện đại, việc ứng dụng giải pháp thiết kế trên SketchUp kết hợp plugin ABF để xuất mã G-code cắt CNC Nesting đã giúp tự động hóa khâu pha phôi. Tuy nhiên, trong thực tế vận hành tại các xưởng sản xuất, những sai sót nhỏ trong khâu thiết kế cấu kiện và thiết lập thông số xuất file thường dẫn đến hiện tượng hao hụt phôi ván từ 15% đến 20%, thậm chí làm sai lệch kích thước lắp ráp tại hiện trường. Việc hiểu rõ bản chất thuật toán bóc tách của ABF và các quy chuẩn máy CNC là yếu tố sống còn giúp tối ưu chi phí vật tư và nâng cao năng suất thi công.</p>

<h2>1. Lỗi Vẽ Trùng Mặt (Z-Fighting) Và Nhầm Chiều Vân Khiến Phần Mềm ABF Xoay Phôi Sai Khổ</h2>
<p>Một trong những lỗi phổ biến nhất của thợ vẽ bản vẽ là tạo các khối component hoặc group chồng lấn lên nhau, dẫn đến hiện tượng hai bề mặt cùng chia sẻ một tọa độ không gian (Z-fighting). Khi chạy thuật toán nesting, plugin ABF sẽ nhận diện nhầm hai chi tiết riêng biệt hoặc xác định sai véc-tơ pháp tuyến bề mặt. Hậu quả là phần mềm tự động xoay chi tiết 90 độ ngược chiều vân gỗ phủ Melamine để cố gắng nhét vừa khoảng trống trên tấm ván khổ chuẩn 1220x2440mm.</p>
<p>Đối với các cấu kiện kích thước lớn như hồi tủ áo hay cánh tủ dài 2200mm, việc bị xoay ngang sẽ khiến phần mềm báo lỗi vượt khổ hoặc tự động đẩy chi tiết sang một tấm ván mới toanh, biến tấm ván nguyên thành phôi đề-xê lãng phí. Để xử lý triệt để, kỹ thuật viên cần chuẩn hóa thao tác gán nhãn Grain (chiều vân) ngay khi tạo Component, đồng thời sử dụng công cụ kiểm tra trục tọa độ trước khi xuất lệnh nesting.</p>
<p style="text-align: center; margin: 25px 0;">
  <img src="IMAGE_PLACEHOLDER_1" alt="Kiểm tra cấu kiện và chiều vân gỗ trên giao diện phần mềm ABF SketchUp" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px;" />
  <br />
  <em style="color: #666; font-size: 14px;">Giao diện phần mềm ABF trên SketchUp hiển thị thông số kiểm tra hướng vân và khử mặt phẳng trùng trước khi chạy thuật toán nesting tự động.</em>
</p>

<h2>2. Khai Báo Sai Độ Dày Thực Tế Của Cốt Ván Gây Hở Hèm Âm Dương Và Rơ Mộng Cam Chốt</h2>
<p>Các dòng ván gỗ công nghiệp như cốt MDF lõi xanh chống ẩm HMR, HDF hay ván ép Plywood luôn có dung sai vật lý nhất định từ nhà máy sản xuất cốt. Một tấm ván trên danh nghĩa 17mm thực tế thường dao động từ 16.8mm đến 17.3mm tùy thuộc vào độ dày lớp phủ Melamine hoặc Laminate bề mặt. Khi thiết kế trong SketchUp, nếu người vẽ giữ nguyên kích thước tròn 17mm hoặc 18mm mà không đo kiểm phôi thực tế nhập xưởng, toàn bộ các rãnh soi hạ bậc hậu tủ 9mm và các liên kết ngàm mộng âm dương sẽ bị sai lệch hoàn toàn.</p>
<p>Nếu rãnh cắt quá hẹp, thợ ráp phải dùng búa cao su đóng cưỡng bức gây toác mép nẹp dán; nếu rãnh quá rộng, kết cấu thùng tủ sẽ bị rơ lắc và giảm khả năng chịu lực. Tại <a href="https://happyco.asia/gioi-thieu.html">xưởng gia công Happyco</a>, quy trình đo kiểm mẫu ván bằng thước kẹp điện tử được thực hiện nghiêm ngặt trên từng lô phôi, sau đó nhập chính xác chỉ số độ dày thực vào thông số Sheet Thickness để hệ thống CAM tự động bù trừ đường chạy dao.</p>
<p style="text-align: center; margin: 25px 0;">
  <img src="IMAGE_PLACEHOLDER_2" alt="Đo kiểm dung sai độ dày ván gỗ công nghiệp bằng thước kẹp điện tử cơ khí" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px;" />
  <br />
  <em style="color: #666; font-size: 14px;">Thao tác kiểm tra dung sai độ dày ván cốt xanh bằng thước kẹp cơ khí chính xác trước khi nạp dữ liệu vào máy cắt CNC trung tâm.</em>
</p>

<h2>3. Quên Kích Hoạt Tính Năng Trừ Chiều Dày Chỉ Nẹp Cạnh Khiến Sai Lệch Kích Thước Hệ Cánh Tủ</h2>
<p>Chỉ dán cạnh PVC và ABS chuyên dụng thường có độ dày từ 0.8mm, 1.0mm đến 2.0mm nhằm bảo vệ cốt ván kháng ẩm và tăng tính thẩm mỹ. Trong một module hệ tủ gồm 3 hoặc 4 cánh mở cạnh nhau, nếu file SketchUp không bật tính năng trừ nẹp tự động (Edge Banding Deduction) trong bảng thuộc tính ABF, kích thước mỗi tấm cánh sau công đoạn dán cạnh sẽ tăng thêm từ 1.6mm đến 4.0mm theo cả chiều cao lẫn chiều rộng.</p>
<p>Khi lắp đặt hoàn thiện, các mép cánh tủ sẽ va quẹt vào nhau, làm mất hoàn toàn khe hở tiêu chuẩn 2mm - 3mm giữa hai cánh và khiến thợ công trình mất hàng giờ đồng hồ để căn chỉnh ốc bản lề giảm chấn. Quy trình chuẩn đòi hỏi người lập trình phải gán đúng mã chỉ nẹp cho từng cạnh biên và đồng bộ dữ liệu trừ mép dao cắt. Điều này giúp các đơn vị sử dụng dịch vụ <a href="https://happyco.asia/dich-vu/gia-cong-van-hmr-phu-melamine-theo-file-abf-tai-bien-hoa.html">gia công ván theo file ABF</a> có thể lắp ráp nhanh chóng tại công trình mà không cần bào gọt chỉnh sửa thủ công.</p>
<p style="text-align: center; margin: 25px 0;">
  <img src="IMAGE_PLACEHOLDER_3" alt="Gia công dán chỉ nẹp cạnh bảo vệ mép ván gỗ công nghiệp trên dây chuyền tự động" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px;" />
  <br />
  <em style="color: #666; font-size: 14px;">Cánh tủ gỗ sau khi phay CNC được dán chỉ nẹp cạnh bảo vệ lõi đồng thời đảm bảo khe hở tiêu chuẩn kỹ thuật giữa các cánh tủ kề nhau.</em>
</p>

<h2>4. Đặt Khoảng Cách Phôi Và Lượng Dư Mép Ván Quá Nhỏ Dẫn Đến Trượt Bàn Hút Chân Không</h2>
<p>Nhằm tiết kiệm tối đa diện tích ván, một số người vận hành thường ép khoảng cách giữa các chi tiết (Part Gap) xuống dưới 6mm và đặt lề tấm ván (Sheet Margin) sát mép 5mm. Đây là một sai lầm kỹ thuật nghiêm trọng trên máy CNC Nesting. Khi mũi dao phay xoắn hai me chạy ở tốc độ trục chính 18.000 đến 24.000 vòng/phút, lực cắt tiếp tuyến kết hợp cùng luồng gió xoáy cực mạnh sẽ dễ dàng làm xê dịch những chi tiết có diện tích bề mặt nhỏ (dưới 150mm x 150mm) do lực giữ của bàn hút chân không tại khu vực mép ván bị suy giảm.</p>
<p>Hiện tượng trượt phôi không chỉ gây mẻ cạnh, cháy cạnh phủ Melamine mà còn tiềm ẩn rủi ro gãy mũi dao kim cương đắt tiền. Tiêu chuẩn vận hành an toàn khuyến cáo duy trì khoảng cách giữa các chi tiết tối thiểu 8mm - 10mm (tương thích đường kính mũi dao xoắn 6mm tiêu chuẩn) và mép tấm ván từ 12mm - 15mm. Đồng thời, kỹ thuật cắt phá hai lần (nesting onion skin) nên được áp dụng cho các mảng phôi nhỏ nhằm giữ nguyên màng da 1mm trước khi cắt đứt vòng cuối cùng.</p>
<p style="text-align: center; margin: 25px 0;">
  <img src="IMAGE_PLACEHOLDER_4" alt="Bàn máy CNC đa vùng hút chân không giữ chặt phôi ván trong suốt quá trình chạy dao" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px;" />
  <br />
  <em style="color: #666; font-size: 14px;">Bàn máy CNC đa vùng hút chân không giữ cố định từng chi tiết phôi ván phẳng phiu trong suốt chu trình chạy dao tốc độ cao.</em>
</p>"""

content_html = ensure_green_box(content_html)

image_prompts = [
    {
        "key": "thumb",
        "h2_ref": "Thumbnail - Title",
        "title_vi": title,
        "alt_vi": "Máy cắt CNC Nesting gia công ván công nghiệp theo bản vẽ file ABF chuẩn xác",
        "caption_vi": "Dây chuyền máy cắt CNC Nesting công nghiệp đang tự động gia công phôi ván theo file bản vẽ tại xưởng mộc.",
        "prompt_en": "Handheld wide documentary view of an active CNC nesting router cutting wood board in a bustling Vietnamese woodworking factory, heavy vacuum bed holding melamine MDF panels flat, sharp router bit carving precise cabinet parts, visible fine wooden dust near dust extraction hood, industrial workshop environment in Dong Nai, overhead white fluorescent tube lighting, realistic factory setting, shot on 35mm lens, 16:9 widescreen, no text, no watermark."
    },
    {
        "key": "h2_1",
        "h2_ref": "1. Lỗi Vẽ Trùng Mặt (Z-Fighting) Và Nhầm Chiều Vân Khiến Phần Mềm ABF Xoay Phôi Sai Khổ",
        "title_vi": "Lỗi Vẽ Trùng Mặt (Z-Fighting) Và Nhầm Chiều Vân Khiến Phần Mềm ABF Xoay Phôi Sai Khổ",
        "alt_vi": "Giao diện kiểm tra lỗi cấu kiện và hướng vân gỗ trên phần mềm ABF SketchUp",
        "caption_vi": "Kiểm tra hướng vân gỗ và các thành phần cấu kiện trên giao diện SketchUp ABF trước khi xuất lệnh gia công.",
        "prompt_en": "Close-up over-the-shoulder shot of a computer monitor displaying SketchUp ABF nesting layout inside a Vietnamese woodworking office, technical 3D wireframe wood joinery parts and cutting sheets visible on screen, drafting mouse on wooden desk with scattered blueprints, realistic ambient indoor workshop office lighting, authentic documentary feel, sharp focus, 16:9 widescreen, no watermark."
    },
    {
        "key": "h2_2",
        "h2_ref": "2. Khai Báo Sai Độ Dày Thực Tế Của Cốt Ván Gây Hở Hèm Âm Dương Và Rơ Mộng Cam Chốt",
        "title_vi": "Khai Báo Sai Độ Dày Thực Tế Của Cốt Ván Gây Hở Hèm Âm Dương Và Rơ Mộng Cam Chốt",
        "alt_vi": "Thợ kỹ thuật đo kiểm độ dày phôi ván bằng thước kẹp điện tử chính xác",
        "caption_vi": "Thao tác kiểm tra dung sai độ dày ván cốt xanh bằng thước kẹp cơ khí chính xác trước khi nạp dữ liệu vào máy cắt CNC trung tâm.",
        "prompt_en": "Macro eye-level focus on a stainless digital vernier caliper measuring the thickness of a moisture-resistant green core MDF board edge, clear LCD screen reading exact millimetres, weathered wooden workbench in a real Vietnamese woodcraft workshop, subtle sawdust dustings on timber surface, natural side lighting from open factory doors, 16:9 aspect ratio, no text."
    },
    {
        "key": "h2_3",
        "h2_ref": "3. Quên Kích Hoạt Tính Năng Trừ Chiều Dày Chỉ Nẹp Cạnh Khiến Sai Lệch Kích Thước Hệ Cánh Tủ",
        "title_vi": "Quên Kích Hoạt Tính Năng Trừ Chiều Dày Chỉ Nẹp Cạnh Khiến Sai Lệch Kích Thước Hệ Cánh Tủ",
        "alt_vi": "Máy dán cạnh tự động dán nẹp PVC bảo vệ cạnh ván công nghiệp",
        "caption_vi": "Cánh tủ gỗ sau khi phay CNC được dán chỉ nẹp cạnh bảo vệ lõi đồng thời đảm bảo khe hở tiêu chuẩn kỹ thuật giữa các cánh tủ kề nhau.",
        "prompt_en": "Medium horizontal shot of an industrial automatic edge banding machine in operation, pressing thin PVC edge tape onto green core MDF cabinet doors via pressure rollers, glossy wood edge trim exiting conveyor, authentic factory atmosphere in Vietnam, sawdust particles in air, bright tube ceiling lights, gritty industrial texture, 16:9 widescreen, no CGI."
    },
    {
        "key": "h2_4",
        "h2_ref": "4. Đặt Khoảng Cách Phôi Và Lượng Dư Mép Ván Quá Nhỏ Dẫn Đến Trượt Bàn Hút Chân Không",
        "title_vi": "Đặt Khoảng Cách Phôi Và Lượng Dư Mép Ván Quá Nhỏ Dẫn Đến Trượt Bàn Hút Chân Không",
        "alt_vi": "Phôi ván công nghiệp sau khi cắt CNC được phân loại và kiểm soát tem nhãn",
        "caption_vi": "Bàn máy CNC đa vùng hút chân không giữ cố định từng chi tiết phôi ván phẳng phiu trong suốt chu trình chạy dao tốc độ cao.",
        "prompt_en": "Wide floor-level documentary angle of neatly stacked cut melamine board panels on wooden pallets in a large fabrication workshop, each panel labeled with a clean barcode sticker, CNC router machine in blurred industrial background, smooth concrete floor with sawdust broom marks, authentic Vietnamese factory scene, 16:9 widescreen, documentary photo."
    }
]

article_dict = {
    "title": title,
    "slug": slug,
    "description": description,
    "meta_description": description,
    "keywords": keywords,
    "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
    "cat_id": "265",
    "pool": "b2b_abf_mistakes",
    "formula_id": "number_mistakes",
    "content_html": content_html,
    "image_prompts": image_prompts
}

# Run Chief QA Audit
qa = ChiefQAAgent()
audit_res = qa.audit(article_dict)
print("=" * 60)
print("QA AUDIT PASSED:", audit_res["passed"])
print("QA CHECKS:", json.dumps(audit_res["checks"], ensure_ascii=False, indent=2))
if audit_res["errors"]:
    print("QA ERRORS:", audit_res["errors"])
if audit_res["warnings"]:
    print("QA WARNINGS:", audit_res["warnings"])
print("=" * 60)

full_payload = {
    "schedule_time": "14-11-2026 09:00",
    "article": article_dict,
    "qa_audit": audit_res,
    "image_prompts": image_prompts
}

out_path = BASE_DIR / "output" / "b2b_9h_article.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(full_payload, f, ensure_ascii=False, indent=2)

print(f"[OK] Đã xuất file thành công: {out_path.resolve()}")
print(f"File size: {out_path.stat().st_size} bytes")
