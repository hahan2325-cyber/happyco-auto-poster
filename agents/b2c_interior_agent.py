"""
Sub-Agent: Chuyên Gia Thiết Kế & Thi Công Nội Thất (B2C Interior Specialist)
Chuyên trách chuyên mục BLOG NỘI THẤT (ID: 266)
Phục vụ 3 nhóm đối tượng mục tiêu:
1. CHỦ NHÀ: Quan tâm độ bền kết cấu, phong thủy vượng tài, chi phí trực tiếp tận xưởng, bảo hành dài hạn.
2. VỢ CHỒNG TRẺ: Thẩm mỹ hiện đại, giữ lửa tổ ấm, an toàn tuyệt đối cho con nhỏ (nội thất bo cong mềm mại), ván E1/E0 không mùi cay mắt.
3. KIẾN TRÚC SƯ: Hiện thực hóa bản vẽ 3D ra thực tế chuẩn xác, kỹ thuật mộc tinh xảo (bo cong, rãnh âm LED, khe bóng shadow gap, dán nẹp PUR noline).
"""

import os
import sys
import json
import random
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

B2C_CURATED_TOPICS = [
    {
        "keyword": "thiết kế vách tivi phòng khách tủ rượu hiện đại",
        "title": "Thiết Kế Vách Tivi Phòng Khách Kết Hợp Tủ Rượu Cánh Kính Hiện Đại: Đẳng Cấp Sang Trọng Từ Xưởng Happyco",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_living",
        "target_audience": "Chủ nhà & Kiến trúc sư",
        "themes": "Vách ốp lam sóng than tre phủ vân đá, hệ tủ rượu cánh kính Slim tràn viền gắn đèn LED âm rãnh 4000K, dán nẹp PUR noline tinh tế, bàn trà bo cong an toàn."
    },
    {
        "keyword": "thiết kế nội thất phòng ngủ master vợ chồng trẻ",
        "title": "Thiết Kế Nội Thất Phòng Ngủ Master Cho Vợ Chồng Trẻ: Không Gian Giữ Lửa Tổ Ấm & Tiêu Chuẩn Xanh E1/E0",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_bedroom",
        "target_audience": "Vợ chồng trẻ",
        "themes": "Giường bọc nệm nỉ êm ái bo cong góc chống va đập cho con nhỏ, tủ áo kịch trần cánh kính Slim, bàn phấn treo gương LED cảm ứng, cốt ván E1/E0 an toàn đường hô hấp."
    }
]

class B2CInteriorAgent:
    def __init__(self):
        self.name = "B2C Interior Specialist (Chuyên gia Nội Thất Nhà Ở)"

    def produce_article(self, topic_title: Optional[str] = None) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set!")

        from google import genai
        client = genai.Client(api_key=api_key)

        chosen = random.choice(B2C_CURATED_TOPICS)
        if not topic_title:
            topic_title = chosen["title"]
            keyword = chosen["keyword"]
            pool = chosen["pool"]
            audience = chosen["target_audience"]
            themes = chosen["themes"]
        else:
            keyword = topic_title.lower()
            pool = "b2c_bedroom" if "phòng ngủ" in keyword or "giường" in keyword or "tủ áo" in keyword else "b2c_living"
            audience = "Chủ nhà, Vợ chồng trẻ, Kiến trúc sư"
            themes = "Thiết kế thi công nội thất cao cấp xưởng Happyco."

        prompt = f"""
        Bạn là Kiến trúc sư trưởng kiêm Giám đốc Thiết kế & Thi công của CÔNG TY CỔ PHẦN HAPPYCO (Biên Hòa, Đồng Nai).
        Hãy viết 1 bài viết chuẩn SEO đẳng cấp, sâu sắc xuất bản trên website happyco.asia:

        Tiêu đề: {topic_title}
        Chuyên mục: BLOG NỘI THẤT (ID: 266)
        Từ khóa chính: {keyword}
        Đối tượng độc giả chính: {audience}
        Chủ đề cốt lõi: {themes}

        TIÊU CHUẨN NỘI DUNG 3 NHÓM ĐỐI TƯỢNG:
        1. Với Chủ nhà: Phân tích sâu về độ bền cốt ván chống ẩm, phong thủy phòng khách/phòng ngủ vượng khí tài lộc, lợi ích tiết kiệm 20-30% chi phí khi làm việc trực tiếp tại xưởng sản xuất quy mô lớn Happyco không qua trung gian.
        2. Với Vợ chồng trẻ: Không gian lãng mạn giữ lửa hôn nhân, bố trí góc bo cong tinh tế an toàn cho trẻ nhỏ chạy nhảy, cam kết vật liệu ván chuẩn phát thải E1/E0 an toàn cho sức khỏe hô hấp của bé.
        3. Với Kiến trúc sư: Tôn trọng 100% ngôn ngữ thiết kế 3D, độ chính xác sắc nét từng chi tiết mộc (rãnh âm LED, khe bóng shadow gap, dán nẹp PUR noline không lộ vết dán keo lem nhem).

        QUY TẮC BẮT BUỘC:
        - TUYỆT ĐỐI CẤM nhắc đến thương hiệu đối thủ/nhà phân phối (An Cường, Ba Thanh, Mộc Phát...). Chỉ dùng thuật ngữ chung: Cốt ván chống ẩm lõi xanh cao cấp, ván đạt chuẩn E1/E0, nẹp dán keo PUR Noline, phụ kiện inox 304 giảm chấn.
        - TUYỆT ĐỐI CẤM tự ý chèn các khung viền chữ ký, hotline hay địa chỉ ở cuối bài (Hệ thống website đã tích hợp cố định 2 khối chân trang).
        - Chèn tối thiểu 2 link nội bộ (Internal Links) tự nhiên:
          + 1 link dịch vụ: https://happyco.asia/gioi-thieu.html hoặc https://happyco.asia/dich-vu/gia-cong-van-hmr-phu-melamine-theo-file-abf-tai-bien-hoa.html
          + 1 link liên quan: https://happyco.asia/blog.html

        CẤU TRÚC 4 MỤC <h2> BẮT BUỘC:
        Mỗi mục <h2> phải có đoạn văn chuyên sâu và 1 khối chèn ảnh khổ lớn, căn giữa:
        <p style="text-align: center; margin: 25px 0;">
          <img src="IMAGE_PLACEHOLDER_1" alt="[Mô tả ảnh nội thất thực tế chuẩn SEO]" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);" />
          <br />
          <em style="color: #666; font-size: 14px; margin-top: 8px; display: inline-block;">[Chú thích không gian sống tự nhiên, CẤM chữ 'Hình 1, Hình 2']</em>
        </p>

        TRẢ VỀ DUY NHẤT 1 ĐỐI TƯỢNG JSON HỢP LỆ:
        {{
            "title": "{topic_title}",
            "slug": "...",
            "description": "...",
            "keywords": "{keyword}, nội thất happyco, thiết kế thi công nội thất biên hòa đồng nai",
            "category": "BLOG NỘI THẤT",
            "cat_id": 266,
            "pool": "{pool}",
            "content_html": "<p>Đoạn sapo dẫn nhập lôi cuốn...</p> ... <h2>1. ...</h2> ... <h2>2. ...</h2> ... <h2>3. ...</h2> ... <h2>4. ...</h2> ..."
        }}
        """

        response = None
        for model_name in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash-lite"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    break
            except Exception as e:
                print(f"Warning: Model {model_name} failed: {e}. Trying next model...")
                continue

        if not response or not response.text:
            raise RuntimeError("Failed to generate content with available Gemini models!")

        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        data = json.loads(text.strip())
        data["pool"] = pool
        data["cat_id"] = 266
        data["category"] = "BLOG NỘI THẤT"

        # Remove any accidental footer/address blocks
        import re
        html = data.get("content_html", "")
        html = re.sub(r'<div[^>]*>(?:(?!<\/div>).)*(?:094[67]|Chúng Tôi Nhận Thiết Kế|Khu vực phục vụ|Địa chỉ nhà xưởng).*?<\/div>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<p[^>]*>.*?(?:094[67]|Hotline tư vấn|Địa chỉ công ty).*?</p>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Đảm bảo có tối thiểu 2 link nội bộ
        if "gioi-thieu" not in html and "blog" not in html:
            html += """
<div style="background: #f8fafc; border-left: 4px solid #008848; padding: 14px 18px; margin: 20px 0; border-radius: 0 8px 8px 0; font-size: 15px; color: #334155; line-height: 1.6;">
  🏡 <em>Tham khảo:</em> Quý gia chủ có thể tìm hiểu thêm về năng lực <a href="https://happyco.asia/gioi-thieu.html" style="color: #008848; font-weight: bold; text-decoration: underline;">sản xuất trực tiếp tại xưởng Happyco</a> hoặc chuyên mục <a href="https://happyco.asia/blog.html" style="color: #008848; font-weight: bold; text-decoration: underline;">cẩm nang thiết kế nội thất</a> để lựa chọn phương án tối ưu.
</div>"""

        # BẮT BUỘC: CÀI ĐẶT CHẾT Ô THÔNG TIN HỆ THỐNG CỐ ĐỊNH Ở CUỐI BÀI VIẾT
        FIXED_FOOTER = """
<div style="border: 2px dashed #008848; background: #f6fff9; border-radius: 8px; padding: 18px 22px; margin: 28px 0;">
  <p style="color: #008848; font-weight: bold; margin: 0 0 8px 0; font-size: 16px;">Chúng Tôi Nhận Thiết Kế Nội Thất Ngành Mộc Tại Các Khu Vực Sau:</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">- Miền Nam: Thành phố Hồ Chí Minh, Đồng Nai, Tây Ninh, Thành phố Cần Thơ, Vĩnh Long, Đồng Tháp, Cà Mau, An Giang.</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">📍 <strong>Địa chỉ công ty:</strong> 526/2, Khu phố 8A, Phường Long Bình, thành phố Đồng Nai.</p>
  <p style="margin: 6px 0; color: #d32f2f; font-weight: bold; font-size: 16px;">📞 Liên hệ: 0946 272 286 (Đức Anh)</p>
</div>
"""
        if "Chúng Tôi Nhận Thiết Kế Nội Thất Ngành Mộc Tại Các Khu Vực Sau" not in html:
            html += "\n" + FIXED_FOOTER

        data["content_html"] = html.strip()
        return data
