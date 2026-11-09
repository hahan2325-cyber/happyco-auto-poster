"""
Sub-Agent: Chuyên Gia Gia Công Ván Công Nghiệp (B2B Woodworking Specialist)
Chuyên trách chuyên mục GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265)
Đối tượng: Xưởng mộc, Thầu thợ, Đơn vị thi công nội thất, Kiến trúc sư công trình
"""

import os
import sys
import re
import json
import random
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

B2B_CURATED_TOPICS = [
    {
        "keyword": "gia công ván mdf chống ẩm cnc nesting",
        "title": "Gia Công Ván MDF Chống Ẩm Phủ Melamine: Dây Chuyền CNC Nesting & Khoan Cam Chốt Tự Động Tại Xưởng Happyco",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "cat_id": "265",
        "pool": "b2b_cnc",
        "core_themes": "Giải quyết bài toán tối ưu phôi ván, triệt tiêu mẻ cạnh Melamine, liên kết cam chốt ăn khớp 100%, chia sẻ hạ tầng máy móc xưởng công nghiệp nặng cho anh em thợ mộc."
    },
    {
        "keyword": "gia công dán cạnh pur noline vát tay nắm j k",
        "title": "Gia Công Dán Cạnh PUR Noline & Vát Tay Nắm J-K Cánh Tủ: Đột Phá Không Đường Keo Cho Xưởng Mộc – Happyco",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "cat_id": "265",
        "pool": "b2b_pur",
        "core_themes": "Khắc phục triệt để đường chỉ đen lem nhem của keo EVA truyền thống, công nghệ dán nẹp keo PUR chống nước 100%, phay vát tay nắm âm cánh J-K liền khối tự động."
    },
    {
        "keyword": "gia công cắt phôi ván ép plywood phủ melamine",
        "title": "Gia Công Cắt Phôi Ván Ép Plywood Phủ Melamine Chống Nước Tuyệt Đối Cho Tủ Bếp & Lavabo",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "cat_id": "265",
        "pool": "b2b_cnc",
        "core_themes": "Cốt ván Plywood nhiều lớp ép keo WBP chống nước, cắt CNC dao carbide không xơ xước, dán cạnh PUR noline bảo vệ mép ván bền bỉ."
    }
]

class B2BWoodworkingAgent:
    def __init__(self):
        self.name = "B2B Woodworking Specialist (Chuyên gia Gia Công Ván)"

    def produce_article(self, topic_title: Optional[str] = None) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set!")

        from google import genai
        client = genai.Client(api_key=api_key)

        chosen = random.choice(B2B_CURATED_TOPICS)
        if not topic_title:
            topic_title = chosen["title"]
            keyword = chosen["keyword"]
            pool = chosen["pool"]
            themes = chosen["core_themes"]
        else:
            keyword = topic_title.lower()
            pool = "b2b_pur" if "pur" in keyword or "dán cạnh" in keyword else "b2b_cnc"
            themes = "Gia công mộc công nghiệp, cắt CNC nesting, dán cạnh PUR noline, khoan cam chốt tự động."

        prompt = f"""
        Bạn là Kỹ sư trưởng xưởng gia công mộc công nghiệp của CÔNG TY CỔ PHẦN HAPPYCO (Đồng Nai).
        Hãy viết 1 bài viết kỹ thuật chuyên sâu xuất bản trên website happyco.asia:

        Tiêu đề: {topic_title}
        Chuyên mục: GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265)
        Từ khóa chính: {keyword}
        Nội dung cốt lõi: {themes}

        ĐỘC GIẢ MỤC TIÊU:
        - Chủ xưởng mộc vừa và nhỏ, anh em thợ mộc nhận công trình tự do, nhà thầu thi công nội thất.
        - Giọng văn: Đậm chất kỹ thuật mộc thực chiến, thấu hiểu nỗi đau nghề mộc: cắt cưa bàn trượt bị mẻ cạnh Melamine, dán keo EVA lộ đường viền đen lem nhem sau vài tháng bám bụi ngấm nước, chi phí đầu tư dàn máy tiền tỷ quá tầm với.
        - Thuật ngữ kỹ thuật bắt buộc:
          + Cốt ván chống ẩm lõi xanh tỷ trọng cao (720–780 kg/m³, độ trương nở ngâm nước < 8%).
          + Máy cắt CNC Nesting bàn hút chân không đa vùng dao phay xoắn carbide triệt tiêu mẻ cạnh.
          + Công nghệ dán cạnh keo PUR Noline (Polyurethane Reactive) màng keo dưới 0.05mm, kháng nước 100%, chịu nhiệt -40°C đến 140°C, lực bám dính cơ học gấp 3-4 lần keo EVA.
          + Khoan cam chốt tự động ăn khớp 100%, phay rãnh hậu âm dương, soi hèm đèn LED nhôm định hình.
          + Đóng gói dán tem mã vạch Barcode từng cấu kiện theo sơ đồ lắp ráp 3D.

        BẮT BUỘC CHÈN 2-3 LIÊN KẾT NỘI BỘ (INTERNAL LINKS) TỰ NHIÊN:
        - 1 link giới thiệu hoặc xưởng mộc: <a href="https://happyco.asia/gioi-thieu.html" style="color: #008848; font-weight: bold; text-decoration: underline;">Happyco</a>
        - 1 link gia công ván: <a href="https://happyco.asia/dich-vu/gia-cong-van-hmr-phu-melamine-theo-file-abf-tai-bien-hoa.html" style="color: #008848; font-weight: bold; text-decoration: underline;">gia công ván HMR phủ Melamine theo file ABF</a>
        - Callout box tham khảo:
        <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 14px 18px; margin: 20px 0; border-radius: 0 8px 8px 0; font-size: 15px; color: #166534; line-height: 1.6;">
          💡 <em>Xem thêm:</em> Quý đối tác xưởng có thể tham khảo thêm giải pháp <a href="https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-plywood-phu-melamine.html" style="color: #15803d; font-weight: bold; text-decoration: underline;">gia công Plywood phủ Melamine dán nẹp PUR</a> siêu chịu nước cho các hạng mục tủ bếp, tủ lavabo cao cấp.
        </div>

        CẤU TRÚC 4 MỤC <h2> BẮT BUỘC KÈM ẢNH:
        Mỗi mục <h2> phải có cấu trúc chèn ảnh khổ lớn, căn giữa:
        <p style="text-align: center; margin: 25px 0;">
          <img src="IMAGE_PLACEHOLDER_1" alt="[Mô tả ảnh kỹ thuật xưởng chuẩn SEO]" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />
          <br />
          <em style="color: #666; font-size: 14px; margin-top: 8px; display: inline-block;">[Chú thích ảnh kỹ thuật mộc thực tế, CẤM chữ 'Hình 1, Hình 2']</em>
        </p>

        TUYỆT ĐỐI KHÔNG:
        - CẤM nhắc thương hiệu đối thủ/nhà phân phối (An Cường, Ba Thanh, Mộc Phát...).
        - CẤM chèn bất kỳ khung viền địa chỉ, hotline hay chữ ký nào ở cuối bài viết (Website đã có sẵn 2 khối chân trang cố định).

        TRẢ VỀ DUY NHẤT 1 ĐỐI TƯỢNG JSON HỢP LỆ:
        {{
            "title": "...",
            "description": "...",
            "content_html": "...",
            "meta_title": "...",
            "meta_description": "...",
            "tags": "...",
            "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
            "cat_id": "265",
            "pool": "{pool}",
            "image_prompts": [
                {{"key": "thumb", "title_vi": "Ảnh bìa gia công mộc Happyco", "alt_vi": "Ảnh bìa xưởng gia công mộc", "caption_vi": "Dây chuyền gia công ván Happyco", "prompt_en": "Photorealistic horizontal 16:9 industrial woodworking factory photograph..."}},
                {{"key": "h2_1", "title_vi": "Ảnh tiêu chuẩn cốt ván", "alt_vi": "Cốt ván chống ẩm tỷ trọng cao", "caption_vi": "Kiểm tra dung sai cốt ván chống ẩm", "prompt_en": "Photorealistic horizontal 16:9 workshop photograph of moisture-resistant green core MDF..."}},
                {{"key": "h2_2", "title_vi": "Ảnh máy CNC Nesting", "alt_vi": "Máy cắt phay CNC bàn hút chân không", "caption_vi": "Gia công cắt CNC Nesting không mẻ cạnh", "prompt_en": "Photorealistic horizontal 16:9 photograph of a modern high-speed CNC nesting machine cutting wood panels..."}},
                {{"key": "h2_3", "title_vi": "Ảnh máy dán cạnh PUR Noline", "alt_vi": "Công nghệ dán cạnh keo PUR noline", "caption_vi": "Cận cảnh mép dán cạnh PUR không đường keo", "prompt_en": "Photorealistic horizontal 16:9 macro close-up of industrial PUR edge banding machine..."}},
                {{"key": "h2_4", "title_vi": "Ảnh đóng gói mã vạch", "alt_vi": "Đóng gói dán tem barcode theo kiện", "caption_vi": "Thành phẩm dán mã barcode xuất xưởng", "prompt_en": "Photorealistic horizontal 16:9 warehouse photograph of finished flat-pack furniture components with barcode labels..."}}
            ]
        }}
        """

        res = None
        for model_name in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash-lite"]:
            try:
                res = client.models.generate_content(model=model_name, contents=prompt)
                if res and res.text:
                    break
            except Exception as e:
                print(f"Warning: Model {model_name} failed: {e}. Trying next model...")
                continue

        if not res or not res.text:
            raise RuntimeError("Failed to generate content with available Gemini models!")
        raw = res.text.strip()
        if raw.startswith("```json"): raw = raw[7:]
        elif raw.startswith("```"): raw = raw[3:]
        if raw.endswith("```"): raw = raw[:-3]

        data = json.loads(raw.strip())
        data["category"] = "GIA CÔNG VÁN CÔNG NGHIỆP"
        data["cat_id"] = "265"
        data["pool"] = pool

        # Remove any accidental footer/address blocks (website template renders them)
        html = data.get("content_html", "")
        html = re.sub(r'<div[^>]*>(?:(?!<\/div>).)*(?:094[67]|Chúng Tôi Nhận Thiết Kế|Khu vực phục vụ|Địa chỉ nhà xưởng).*?<\/div>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<p[^>]*>.*?(?:094[67]|Hotline tư vấn|Địa chỉ công ty).*?</p>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Đảm bảo có callout box và link nội bộ
        if "gia-cong-plywood" not in html:
            html += """
<div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 14px 18px; margin: 20px 0; border-radius: 0 8px 8px 0; font-size: 15px; color: #166534; line-height: 1.6;">
  💡 <em>Xem thêm:</em> Quý đối tác xưởng có thể tham khảo thêm giải pháp <a href="https://happyco.asia/dich-vu/gia-cong-van-cong-nghiep/gia-cong-plywood-phu-melamine.html" style="color: #15803d; font-weight: bold; text-decoration: underline;">gia công Plywood phủ Melamine dán nẹp PUR</a> | <a href="https://happyco.asia/dich-vu/gia-cong-van-hmr-phu-melamine-theo-file-abf-tai-bien-hoa.html" style="color: #15803d; font-weight: bold; text-decoration: underline;">gia công ván HMR theo file ABF</a> tại xưởng Happyco.
</div>"""
        data["content_html"] = html.strip()

        return data
