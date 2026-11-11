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
import re
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

B2C_CURATED_TOPICS = [
    {
        "keyword": "thiết kế nội thất nhà phố tối ưu diện tích gỗ công nghiệp",
        "title": "Giải Pháp Thiết Kế Nội Thất Gỗ May Đo Tối Ưu Diện Tích: Biến Nhà Phố Nhỏ Thành Không Gian Sống Rộng Rãi",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_smart_living",
        "target_audience": "Chủ nhà & Vợ chồng trẻ",
        "themes": "Hệ tủ âm tường kịch trần giấu đồ thông minh, giường bục đa năng tích hợp ngăn kéo, vách ngăn nan gỗ thoáng khí, cốt ván chống ẩm lõi xanh E1/E0."
    },
    {
        "keyword": "nội thất phong cách japandi gỗ sồi ấm cúng",
        "title": "Nội Thất Phong Cách Japandi Tinh Tế: Nghệ Thuật Phối Vân Gỗ Tự Nhiên & Đường Bo Cong Mềm Mại Mang Lại Bình Yên",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_japandi_warm",
        "target_audience": "Chủ nhà yêu thẩm mỹ & Kiến trúc sư",
        "themes": "Sự kết hợp giữa nét mộc mạc Nhật Bản và tối giản Bắc Âu, kỹ thuật uốn cong phôi ván CNC, tone màu gỗ sồi ấm áp kết hợp vải nỉ dệt thô mộc."
    },
    {
        "keyword": "tiêu chuẩn ván e0 e1 an toàn sức khỏe trẻ nhỏ",
        "title": "Tiêu Chuẩn Ván Xanh E0/E1 Trong Nội Thất Nhà Ở: Bảo Vệ Hệ Hô Hấp Trẻ Nhỏ & Lựa Chọn Cốt Ván Không Mùi Độc Hại",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_health_eco",
        "target_audience": "Gia đình có con nhỏ & Phụ nữ mang thai",
        "themes": "Tác hại của formaldehyde trong ván trôi nổi, chứng nhận phát thải E0/E1, công nghệ nẹp cạnh PUR noline khóa kín cốt ván, bo tròn góc cạnh chống va đập."
    },
    {
        "keyword": "thiết kế phòng khách sum vầy đa thế hệ",
        "title": "Thiết Kế Phòng Khách Hiện Đại Gắn Kết Đa Thế Hệ: Nghệ Thuật Sắp Đặt Ánh Sáng & Hệ Tủ Kệ Treo Tinh Gọn",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_family_living",
        "target_audience": "Gia đình đa thế hệ & Chủ nhà",
        "themes": "Bố cục ghế sofa quây quần, kệ tivi treo tường giấu dây điện thông minh, hệ rãnh âm LED 3000K ấm cúng, bàn trà tròn bo cạnh an toàn cho ông bà và cháu nhỏ."
    },
    {
        "keyword": "thiết kế phòng ngủ trẻ em thông minh sáng tạo",
        "title": "Thiết Kế Phòng Ngủ Trẻ Em Sáng Tạo: Bố Trí Bàn Học Công Thái Học & Giường Tầng Gỗ Công Nghiệp Chắc Chắn",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_kids_room",
        "target_audience": "Cha mẹ trẻ có con trong độ tuổi đi học",
        "themes": "Góc học tập lấy sáng tự nhiên chống cận thị, giường tầng liên hoàn tủ áo bo tròn góc cạnh, thang bước hộp lưu trữ đồ chơi rèn tính tự lập cho bé."
    },
    {
        "keyword": "phong thủy phòng ngủ master vợ chồng hòa thuận",
        "title": "Phong Thủy Nội Thất Phòng Ngủ Master: Bố Trí Hướng Giường & Luồng Khí Sinh Tài Rước Vượng Khí Cho Gia Chủ",
        "category": "BLOG NỘI THẤT",
        "cat_id": "266",
        "pool": "b2c_fengshui_master",
        "target_audience": "Chủ nhà & Vợ chồng trung niên",
        "themes": "Nguyên tắc đặt giường ngủ tránh xung sát, hệ tủ quần áo phẳng giấu gương soi, phối màu sắc hợp mệnh tương sinh, ánh sáng dịu nhẹ bồi dưỡng năng lượng."
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
        Bạn là Chuyên gia Biên tập Nội dung Kiến trúc & Nội thất của CÔNG TY CỔ PHẦN HAPPYCO (Biên Hòa, Đồng Nai).
        Hãy viết 1 bài viết chuẩn SEO đẳng cấp, sâu sắc xuất bản trên website happyco.asia:

        Tiêu đề: {topic_title}
        Chuyên mục: BLOG NỘI THẤT (ID: 266)
        Từ khóa chính: {keyword}
        Đối tượng độc giả chính: {audience}
        Chủ đề cốt lõi: {themes}

        QUY CHUẨN VĂN PHONG WEB CAO CẤP (ĐÂY LÀ BÀI VIẾT WEBSITE, TUYỆT ĐỐI KHÔNG PHẢI BÀI ĐĂNG FACEBOOK):
        - TUYỆT ĐỐI CẤM chào hỏi kiểu mạng xã hội: Không viết 'Chào anh em', 'Xin chào các bạn', 'Chào quý độc giả', 'Anh em thân mến'...
        - TUYỆT ĐỐI CẤM xưng hô cá nhân hay tự giới thiệu chức danh: Không viết 'Tôi là...', 'Với tư cách là Kiến trúc sư trưởng kiêm Giám đốc...', 'Chúng tôi là đội ngũ kỹ sư...'. Văn phong phải mang tính chuyên gia khách quan, sang trọng, tập trung hoàn toàn vào giải pháp không gian, công năng, phong thủy và trải nghiệm sống của gia chủ.
        - MÔ TẢ BÀI VIẾT (description): TUYỆT ĐỐI CẤM bắt đầu bằng 'Bài viết...', 'Bài viết này...', 'Bài viết chia sẻ...'. Mô tả phải đi thẳng vào tóm lược giải pháp thiết kế, công năng và giá trị thẩm mỹ cho căn hộ/nhà phố (140-160 ký tự chuẩn SEO).
        - Đoạn mở đầu (Sapo): Đi thẳng vào thực trạng xu hướng nội thất hiện đại và giải pháp kiến trúc đột phá, không rào đón dài dòng.

        TIÊU CHUẨN NỘI DUNG 3 NHÓM ĐỐI TƯỢNG:
        1. Với Chủ nhà: Phân tích sâu về độ bền cốt ván chống ẩm, phong thủy vượng khí tài lộc, lợi ích tiết kiệm 20-30% chi phí khi làm việc trực tiếp tại xưởng sản xuất quy mô lớn Happyco không qua trung gian.
        2. Với Vợ chồng trẻ: Không gian lãng mạn giữ lửa tổ ấm, bố trí góc bo cong tinh tế an toàn cho trẻ nhỏ chạy nhảy, cam kết vật liệu ván chuẩn phát thải E1/E0 an toàn cho sức khỏe hô hấp của bé.
        3. Với Kiến trúc sư: Tôn trọng 100% ngôn ngữ thiết kế 3D, độ chính xác sắc nét từng chi tiết mộc (rãnh âm LED, khe bóng shadow gap, dán nẹp PUR noline không lộ vết dán keo lem nhem).

        QUY TẮC CỐT LÕI - CHỐNG TRÙNG LẶP & NHÀM CHÁN (LỆNH ĐẶC BIỆT CỦA TỔNG GIÁM ĐỐC):
        - HẠN CHẾ TỐI ĐA NHÔM, KÍNH, MẶT ĐÁ: Tuyệt đối không lấy nhôm, cánh kính, hay mặt đá làm chủ đề chính của bài viết! Các vật liệu này chỉ được nhắc đến như một chi tiết bổ trợ nhỏ (chiếm dưới 10% nội dung).
        - TRỌNG TÂM BẮT BUỘC XOÁY VÀO KỸ THUẬT MỘC & GIẢI PHÁP KHÔNG GIAN NỘI THẤT GỖ MAY ĐO:
          + Giải pháp công năng: Tối ưu không gian nhà phố/căn hộ, tủ âm tường kịch trần, giường bục thông minh giấu đồ, vách ngăn thoáng.
          + Thẩm mỹ mộc tinh xảo: Đường nét bo cong góc mềm mại (curved/fluted corners) an toàn cho trẻ nhỏ, rãnh âm LED trang trí 3000K ấm cúng, khe bóng shadow gap, dán nẹp PUR noline không lộ đường keo.
          + Tiêu chuẩn cốt ván xanh: Cốt ván chống ẩm lõi xanh HMR đạt chuẩn phát thải formaldehyde E0/E1, không mùi hăng cay mắt, bảo vệ hệ hô hấp cho trẻ sơ sinh và người lớn tuổi.
          + Cảm xúc & Phong thủy gia đình: Giữ lửa hạnh phúc vợ chồng, góc học tập sáng tạo cho con, phòng khách gắn kết sum vầy các thế hệ, hướng đón gió và ánh sáng tự nhiên.
          + Giá trị tận xưởng Happyco: Máy móc tự động hóa CNC chính xác từng milimet, báo giá trực tiếp từ xưởng sản xuất không qua đại lý trung gian.
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
            "description": "Tóm tắt súc tích giải pháp thiết kế nội thất chuẩn SEO (CẤM chữ 'Bài viết...')",
            "keywords": "{keyword}, nội thất happyco, thiết kế thi công nội thất biên hòa đồng nai",
            "category": "BLOG NỘI THẤT",
            "cat_id": 266,
            "pool": "{pool}",
            "content_html": "<p>Đoạn sapo đi thẳng vào xu hướng...</p> ... <h2>1. ...</h2> ... <h2>2. ...</h2> ... <h2>3. ...</h2> ... <h2>4. ...</h2> ..."
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

        # Chuẩn hóa văn phong web: Xóa sạch chào hỏi FB hoặc tự xưng danh cá nhân
        desc = data.get("description", "").strip()
        desc = re.sub(r'^(?:Bài viết|Bài viết này|Bài viết chia sẻ|Bài viết nhằm)\s*(?:này\s*)?(?:chia sẻ|giới thiệu|phân tích|cung cấp)?\s*[:,-]?\s*', '', desc, flags=re.IGNORECASE)
        data["description"] = desc.strip()

        html = data.get("content_html", "")
        html = re.sub(r'(?:Chào anh em|Xin chào anh em|Chào các bạn|Xin chào các bạn|Anh em thân mến)[!,\.]?\s*', '', html, flags=re.IGNORECASE)
        html = re.sub(r'Với tư cách là[^,\.\n]+,\s*(?:tôi\s*)?', '', html, flags=re.IGNORECASE)
        html = re.sub(r'Tôi là[^,\.\n]+(?:kiêm|của)[^,\.\n]+,\s*', '', html, flags=re.IGNORECASE)
        html = re.sub(r'Chúng tôi là đội ngũ kỹ sư[^,\.\n]+,\s*', '', html, flags=re.IGNORECASE)

        # Remove any accidental footer/address blocks
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

    def plan_outline_and_prompts(self, topic_title: Optional[str] = None) -> Dict[str, Any]:
        """Tạo dàn ý nhanh & 5 prompts ảnh chất lượng 2K để bơm sang Flow ngay lập tức"""
        api_key = os.getenv("GEMINI_API_KEY")
        from google import genai
        client = genai.Client(api_key=api_key)

        chosen = random.choice(B2C_CURATED_TOPICS)
        title = topic_title if topic_title else chosen["title"]
        prompt = f"""
        Lên dàn bài H2 và 5 prompt ảnh Google Flow (tiếng Anh) cho bài viết nội thất:
        Tiêu đề: {title}
        Chuyên mục: BLOG NỘI THẤT (ID: 266)

        YÊU CẦU:
        - 4 tiêu đề <h2> thiết kế nội thất đẳng cấp.
        - 5 câu Prompt tiếng Anh chi tiết cho Imagen/Flow (1 ảnh thumbnail tổng quan, 4 ảnh chi tiết ứng với từng H2). Phong cách kiến trúc hiện đại, chụp thực tế documentary, ánh sáng ấm 3000K, tỉ lệ 16:9, không người, không hoa văn kỳ quái.

        Trả về JSON duy nhất:
        {{
            "title": "{title}",
            "slug": "...",
            "h2_list": ["h2 1", "h2 2", "h2 3", "h2 4"],
            "prompts": [
                "prompt thumb...",
                "prompt h2_1...",
                "prompt h2_2...",
                "prompt h2_3...",
                "prompt h2_4..."
            ]
        }}
        """
        resp = None
        for m in ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash-lite"]:
            try:
                resp = client.models.generate_content(model=m, contents=prompt)
                if resp and resp.text: break
            except Exception:
                continue

        text = resp.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        plan = json.loads(text.strip())
        plan["category"] = "BLOG NỘI THẤT"
        plan["cat_id"] = 266
        return plan

    def write_full_article_from_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Viết toàn văn bài viết chi tiết chuẩn SEO từ dàn bài đã có trong lúc Flow vẽ ảnh"""
        return self.produce_article(topic_title=plan["title"])
