"""
Bộ sinh nội dung bài viết chuẩn SEO cho Happyco
Chia rõ 2 chuyên mục trọng điểm:
1. GIA CÔNG VÁN CÔNG NGHIỆP: Kỹ thuật mộc chuyên sâu, xưởng sản xuất, chia sẻ hạ tầng gia công, máy CNC Nesting, dán cạnh PUR Noline, phay vát tay nắm J-K, khoan cam chốt tự động.
2. BLOG NỘI THẤT: Thiết kế không gian sống cho Chủ nhà, Vợ chồng trẻ, Kiến trúc sư (Vách tivi kịch trần, tủ rượu cánh kính, phòng ngủ master, tủ bếp Acrylic).

Tuân thủ nghiêm ngặt:
- KHÔNG tự tiện chèn ô liên hệ / hotline / chân trang (Hệ thống web đã có sẵn 2 khối cố định).
- Ảnh chèn đầy đủ kích thước lớn, chuẩn 16:9, có chú thích chi tiết.
"""

import os
import sys
import re
import json
import random
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

B2B_TOPICS = [
    {
        "keyword": "gia công ván mdf chống ẩm cnc nesting",
        "title": "Gia Công Ván MDF Chống Ẩm Phủ Melamine: Dây Chuyền CNC Nesting & Khoan Cam Chốt Tự Động Tại Xưởng Happyco",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "target_audience": "Xưởng mộc, Thầu thợ, Đơn vị thi công nội thất",
        "core_themes": "Giải quyết bài toán tối ưu phôi ván, triệt tiêu mẻ cạnh Melamine, cam chốt ăn khớp 100%, chia sẻ hạ tầng máy móc cho xưởng mộc vừa và nhỏ."
    },
    {
        "keyword": "gia công dán cạnh pur noline vát tay nắm j k",
        "title": "Gia Công Dán Cạnh PUR Noline & Vát Tay Nắm J-K Cánh Tủ: Đột Phá Không Đường Keo Cho Xưởng Mộc – Happyco",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "target_audience": "Xưởng mộc, Thợ mộc tự do, Kiến trúc sư",
        "core_themes": "Khắc phục nhược điểm đường keo đen lem nhem của keo EVA truyền thống, công nghệ dán nẹp keo PUR chống nước 100%, phay vát tay nắm âm cánh J-K liền khối tự động."
    },
    {
        "keyword": "gia công cắt phôi ván ép plywood phủ melamine",
        "title": "Gia Công Cắt Phôi Ván Ép Plywood Phủ Melamine Chống Nước Tuyệt Đối Cho Tủ Bếp & Lavabo",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "target_audience": "Xưởng mộc & Nhà thầu dự án cao cấp",
        "core_themes": "Cốt ván Plywood nhiều lớp ép keo WBP chống nước, cắt CNC dao carbide không xơ xước, dán cạnh PUR noline bảo vệ mép ván bền bỉ."
    }
]

B2C_TOPICS = [
    {
        "keyword": "thiết kế vách tivi phòng khách kịch trần tủ rượu cánh kính",
        "title": "Thiết Kế Vách Tivi Phòng Khách Hiện Đại: Xu Hướng Hệ Tủ Kệ Kịch Trần Kết Hợp Tủ Rượu Cánh Kính Đèn LED Sang Trọng – Happyco",
        "category": "BLOG NỘI THẤT",
        "target_audience": "Chủ nhà, Vợ chồng trẻ, Kiến trúc sư",
        "core_themes": "Tối ưu không gian phòng khách, hệ vách lam sóng than tre vân đá, tủ rượu cánh kính khung nhôm slim đèn LED 3000K, tối ưu 20-30% chi phí trực tiếp từ xưởng mộc."
    },
    {
        "keyword": "thiết kế phòng ngủ master sang trọng giường bọc nệm tủ áo cánh kính",
        "title": "Thiết Kế Phòng Ngủ Master Sang Trọng: Giải Pháp Bố Trí Giường Ngủ Bọc Nệm Kết Hợp Bàn Phấn Treo & Hệ Tủ Quần Áo Kịch Trần Tối Giản – Happyco",
        "category": "BLOG NỘI THẤT",
        "target_audience": "Vợ chồng trẻ & Chủ nhà",
        "core_themes": "Không gian nghỉ dưỡng ấm cúng, giường bọc nệm nỉ êm ái, tủ áo kịch trần cánh kính xám khói, bàn phấn treo gương LED cảm biến thông minh."
    },
    {
        "keyword": "thiết kế tủ bếp chữ L acrylic bóng gương",
        "title": "Xu Hướng Tủ Bếp Hiện Đại Cánh Phủ Acrylic Bóng Gương: Tối Ưu Công Năng Tam Giác Vàng Cho Căn Hộ Cao Cấp",
        "category": "BLOG NỘI THẤT",
        "target_audience": "Gia đình & Người nội trợ hiện đại",
        "core_themes": "Bố trí công năng chuẩn công thái học, thùng chống ẩm dán cạnh PUR kháng nước, mặt cánh phẳng gương tạo cảm giác không gian rộng mở."
    }
]

def generate_article(topic_title: Optional[str] = None, category: str = "BLOG NỘI THẤT") -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment!")

    from google import genai
    client = genai.Client(api_key=api_key)

    is_b2b = "GIA CÔNG" in category.upper() or "VÁN" in category.upper()
    pool = B2B_TOPICS if is_b2b else B2C_TOPICS

    if not topic_title:
        chosen = random.choice(pool)
        topic_title = chosen["title"]
        category = chosen["category"]
        keyword = chosen["keyword"]
        themes = chosen["core_themes"]
    else:
        keyword = topic_title.lower()
        themes = "Kỹ thuật mộc chuyên nghiệp, vật liệu cao cấp, độ chính xác xưởng Happyco."

    if is_b2b:
        audience_prompt = """
        CHUYÊN MỤC: GIA CÔNG VÁN CÔNG NGHIỆP (B2B XƯỞNG MỘC & THẦU THỢ)
        - Độc giả mục tiêu: Chủ xưởng mộc vừa và nhỏ, anh em thợ mộc tự do nhận công trình, nhà thầu nội thất, KTS kỹ thuật.
        - Giọng văn: Đậm chất kỹ thuật mộc chuyên sâu, thấu hiểu khó khăn của thợ mộc (mẻ cạnh khi cưa bàn trượt, dán keo EVA lộ đường viền đen bám bụi, chi phí đầu tư máy móc quá lớn).
        - Thuật ngữ bắt buộc: Cốt ván chống ẩm lõi xanh tỷ trọng cao (720–780 kg/m³, độ trương nở < 8%), máy CNC Nesting bàn hút chân không đa vùng dao phay xoắn carbide, công nghệ dán cạnh keo PUR Noline màng keo dưới 0.05mm chống nước 100%, khoan liên kết cam chốt tự động ăn khớp 100%, phay rãnh hậu âm dương, soi hèm nhôm LED, đóng gói dán tem mã vạch Barcode từng cấu kiện kèm sơ đồ lắp ráp 3D.
        - Bắt buộc chèn 1 Callout box dạng:
          <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 14px 18px; margin: 20px 0; border-radius: 0 8px 8px 0; font-size: 15px; color: #166534; line-height: 1.6;">
            💡 <em>Xem thêm:</em> Quý xưởng và đối tác có thể tham khảo thêm giải pháp <a href="https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-plywood-phu-melamine.html" style="color: #15803d; font-weight: bold; text-decoration: underline;">gia công Plywood phủ Melamine dán nẹp PUR</a> siêu chịu nước để hoàn thiện các hạng mục tủ bếp, tủ lavabo cao cấp.
          </div>
        - Image Prompts yêu cầu: Ảnh xưởng công nghiệp thực tế, máy CNC Nesting đang phay cắt ván, cận cảnh máy dán cạnh PUR noline với vòi keo nhiệt, thước kẹp điện tử đo dung sai phôi ván, kỹ thuật viên xưởng mộc quét mã barcode trên kiện hàng ván thành phẩm.
        """
    else:
        audience_prompt = """
        CHUYÊN MỤC: BLOG NỘI THẤT (B2C CHỦ NHÀ & KIẾN TRÚC SƯ)
        - Độc giả mục tiêu: Chủ nhà, Vợ chồng trẻ, Kiến trúc sư tìm kiếm giải pháp thi công thực tế chuẩn bản vẽ 3D.
        - Giọng văn: Tinh tế, ấm áp, sang trọng, tập trung vào trải nghiệm sống tiện nghi, an toàn cho trẻ nhỏ (bo cong góc cạnh), bảo vệ sức khỏe (chuẩn phát thải E1/E0), tối ưu 20-30% chi phí nhờ đặt đóng trực tiếp tại xưởng mộc không qua trung gian.
        - Thuật ngữ bắt buộc: Vách tivi kịch trần, lam sóng than tre, tấm ốp vân đá đối xứng, tủ rượu cánh kính khung nhôm slim đèn LED 3000K, giường ngủ bọc nệm nỉ, tủ áo kịch trần, ray trượt giảm chấn, phụ kiện thông minh.
        - Image Prompts yêu cầu: Ảnh không gian nội thất đời thực (Photorealism), góc chụp rộng 16:9 widescreen, ánh sáng tự nhiên dịu nhẹ kết hợp đèn hắt LED vàng ấm, vật liệu gỗ tinh xảo, không gian gọn gàng cao cấp.
        """

    prompt = f"""
    Bạn là kỹ sư trưởng kiêm chuyên gia nội thất kỳ cựu của CÔNG TY CỔ PHẦN HAPPYCO (Biên Hòa, Đồng Nai).
    Hãy viết bài viết chuẩn SEO chuyên sâu cho website happyco.asia:

    Tiêu đề: {topic_title}
    Chuyên mục: {category}
    Từ khóa chính: {keyword}
    Ý tưởng nòng cốt: {themes}

    {audience_prompt}

    QUY TẮC BẮT BUỘC KHÔNG ĐƯỢC VI PHẠM:
    1. TUYỆT ĐỐI KHÔNG nhắc đến các thương hiệu đối thủ hay nhà phân phối (An Cường, Ba Thanh, Mộc Phát...). Chỉ dùng tên kỹ thuật chuẩn: Cốt ván chống ẩm lõi xanh tỷ trọng cao, chuẩn xuất khẩu E1/E0, bề mặt Melamine/Acrylic/Laminate cao cấp, dán cạnh keo PUR chống ẩm. Tôn vinh thương hiệu CÔNG TY CỔ PHẦN HAPPYCO.
    2. CẤU TRÚC BÀI VIẾT:
       - Tiêu đề hấp dẫn, chuẩn SEO.
       - Sapo mở đầu: 1 đoạn văn lôi cuốn (~160 ký tự) đánh trúng nhu cầu độc giả.
       - Thân bài gồm đúng 4 mục <h2> được đánh số thứ tự (1., 2., 3., 4.).
       - Dưới mỗi mục <h2>, BẮT BUỘC chèn 1 hình ảnh minh họa bằng đúng cấu trúc HTML sau (khổ ảnh lớn, căn giữa đẹp mắt):
         <p style="text-align: center; margin: 25px 0;">
           <img src="IMAGE_PLACEHOLDER_1" alt="[Mô tả ảnh chuẩn SEO không dấu ngoặc]" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />
           <br />
           <em style="color: #666; font-size: 14px; margin-top: 8px; display: inline-block;">[Chú thích ảnh tự nhiên, TUYỆT ĐỐI KHÔNG ghi 'Hình 1, Hình 2']</em>
         </p>
         (Tương ứng IMAGE_PLACEHOLDER_1 đến IMAGE_PLACEHOLDER_4 cho 4 mục <h2>).
       - Chèn 2 liên kết nội bộ tự nhiên:
         + Link 1: https://happyco.asia/tin-tuc
         + Link 2: https://happyco.asia/dich-vu
    3. CẤM TUYỆT ĐỐI CHÈN KHỐI LIÊN HỆ / HOTLINE / ĐỊA CHỈ Ở CUỐI BÀI:
       - Website đã có sẵn 2 khối hệ thống cố định ở chân trang. Bài viết chỉ viết trọn vẹn nội dung chuyên môn và kết bài tự nhiên sau mục 4, KHÔNG thêm bất kỳ khung viền, hotline 0946/0947 hay địa chỉ công ty nào!
    4. IMAGE PROMPTS (5 ẢNH):
       - Tạo 5 prompt tiếng Anh chi tiết: 1 thumbnail + 4 ảnh mục <h2>.
       - Bắt buộc: 16:9 widescreen, photorealistic architectural/workshop photography, no text, no watermarks, no people face distortion.

    TRẢ VỀ DUY NHẤT 1 ĐỐI TƯỢNG JSON HỢP LỆ (KHÔNG DÙNG BACKTICKS NGOÀI JSON):
    {{
        "title": "Tiêu đề chuẩn SEO",
        "description": "Đoạn sapo mở đầu",
        "content_html": "Mã HTML thân bài",
        "meta_title": "Tiêu đề Meta SEO",
        "meta_description": "Mô tả Meta SEO",
        "tags": "Từ khóa phân cách bằng dấu phẩy",
        "image_prompts": [
            {{
                "key": "thumb",
                "title_vi": "Tiêu đề SEO ảnh bìa",
                "alt_vi": "Mô tả alt ảnh bìa",
                "caption_vi": "Chú thích ảnh bìa",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic thumbnail"
            }},
            {{
                "key": "h2_1",
                "title_vi": "Tiêu đề SEO ảnh 1",
                "alt_vi": "Mô tả alt ảnh 1",
                "caption_vi": "Chú thích ảnh 1",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image 1"
            }},
            {{
                "key": "h2_2",
                "title_vi": "Tiêu đề SEO ảnh 2",
                "alt_vi": "Mô tả alt ảnh 2",
                "caption_vi": "Chú thích ảnh 2",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image 2"
            }},
            {{
                "key": "h2_3",
                "title_vi": "Tiêu đề SEO ảnh 3",
                "alt_vi": "Mô tả alt ảnh 3",
                "caption_vi": "Chú thích ảnh 3",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image 3"
            }},
            {{
                "key": "h2_4",
                "title_vi": "Tiêu đề SEO ảnh 4",
                "alt_vi": "Mô tả alt ảnh 4",
                "caption_vi": "Chú thích ảnh 4",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image 4"
            }}
        ]
    }}
    """

    candidate_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]
    last_err = None

    for model_name in candidate_models:
        try:
            print(f"  [Generator] Đang gọi Gemini model '{model_name}'...", flush=True)
            res = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw = res.text.strip()
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]

            data = json.loads(raw.strip())
            data["category"] = category

            # Strip any accidental footer box
            content_html = data.get("content_html", "")
            cleaned_html = re.sub(r'<div[^>]*style="[^"]*border[^"]*"[^>]*>.*?</div>', '', content_html, flags=re.DOTALL | re.IGNORECASE)
            cleaned_html = re.sub(r'<p[^>]*>.*?Hotline.*?0946.*?272.*?286.*?</p>', '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
            cleaned_html = re.sub(r'<p[^>]*>.*?Địa chỉ công ty.*?</p>', '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
            cleaned_html = re.sub(r'<p[^>]*>.*?Hotline tư vấn thiết kế.*?</p>', '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
            data["content_html"] = cleaned_html.strip()

            return data
        except Exception as e:
            print(f"  [Generator] Model '{model_name}' gặp lỗi: {e}", flush=True)
            last_err = e
            continue

    raise RuntimeError(f"All Gemini models failed: {last_err}")
