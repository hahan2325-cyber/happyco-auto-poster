"""
Bộ sinh nội dung bài viết chuẩn SEO cho Happyco
Sử dụng Google Gemini API
Tuân thủ nghiêm ngặt quy tắc: KHÔNG CHÈN KHỐI CHỮ KÝ / KHỐI LIÊN HỆ VÀO NỘI DUNG (Khối hệ thống của website đã cố định)
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

DEFAULT_TOPICS = [
    {
        "keyword": "vách tivi phòng khách kịch trần hiện đại",
        "title": "Thiết Kế Vách Tivi Phòng Khách Kịch Trần Đẳng Cấp Kết Hợp Tủ Rượu Cánh Kính",
        "category": "BLOG NỘI THẤT",
        "target_audience": "Chủ nhà & Vợ chồng trẻ"
    },
    {
        "keyword": "thiết kế phòng ngủ master bo cong tinh tế",
        "title": "Xu Hướng Thiết Kế Phòng Ngủ Master Bo Cong: Không Gian Nghỉ Dưỡng Ấm Cúng Cho Gia Đình",
        "category": "BLOG NỘI THẤT",
        "target_audience": "Vợ chồng trẻ & Kiến trúc sư"
    },
    {
        "keyword": "tủ bếp acrylic bóng gương chống ẩm",
        "title": "Giải Pháp Tủ Bếp Thùng Chống Ẩm Cánh Phủ Acrylic Bóng Gương Đẳng Cấp Sang Trọng",
        "category": "BLOG NỘI THẤT",
        "target_audience": "Chủ nhà & Gia đình"
    },
    {
        "keyword": "gia công cắt cnc ván mdf theo file",
        "title": "Dịch Vụ Cắt CNC Ván Gỗ Công Nghiệp Theo File Chuẩn Xác Tuyệt Đối Tại Happyco",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "target_audience": "Xưởng mộc & Thầu thợ"
    },
    {
        "keyword": "công nghệ dán cạnh nẹp pur không đường line",
        "title": "Đột Phá Kỹ Thuật Dán Cạnh PUR Noline: Kháng Nước Tuyệt Đối Cho Nội Thất Cao Cấp",
        "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
        "target_audience": "Kiến trúc sư & Xưởng mộc"
    }
]

def generate_article(topic_title: Optional[str] = None, category: str = "BLOG NỘI THẤT") -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment!")

    from google import genai
    client = genai.Client(api_key=api_key)

    if not topic_title:
        chosen = random.choice([t for t in DEFAULT_TOPICS if category.lower() in t["category"].lower()] or DEFAULT_TOPICS)
        topic_title = chosen["title"]
        category = chosen["category"]
        keyword = chosen["keyword"]
    else:
        keyword = topic_title.lower()

    prompt = f"""
    Bạn là chuyên gia kỹ thuật mộc và nhà thiết kế nội thất cao cấp của HAPPYCO.
    Hãy viết một bài viết chuẩn SEO chuyên sâu cho website happyco.asia:

    Tiêu đề yêu cầu: {topic_title}
    Chuyên mục: {category}
    Từ khóa chính: {keyword}

    QUY TẮC CỐT LÕI (BẮT BUỘC TUÂN THỦ 100%):
    1. ĐỐI TƯỢNG ĐỘC GIẢ:
       - Nếu là "BLOG NỘI THẤT": Hướng tới Chủ nhà, Vợ chồng trẻ, hoặc Kiến trúc sư. Nhấn mạnh sự tinh tế, độ bền, thẩm mỹ hiện đại, tối ưu ngân sách xưởng sản xuất trực tiếp.
       - Nếu là "GIA CÔNG VÁN CÔNG NGHIỆP": Hướng tới Xưởng mộc, Thầu thợ, KTS. Nhấn mạnh độ chính xác máy CNC, dán cạnh PUR noline, chất lượng cốt ván xuất khẩu.
    2. NỘI DUNG VÀ VẬT LIỆU:
       - TUYỆT ĐỐI KHÔNG nhắc đến bất kỳ tên thương hiệu nhà phân phối hay đối thủ nào như An Cường, Ba Thanh, Mộc Phát, Panel Plus. Chỉ dùng từ ngữ kỹ thuật chung và cao cấp: "Cốt ván chống ẩm lõi xanh tỷ trọng cao", "Ván đạt chuẩn xuất khẩu E1/E0 an toàn sức khỏe", "Phủ Melamine / Laminate / Acrylic cao cấp", "Dán cạnh nẹp keo PUR chống ẩm". Chỉ tôn vinh thương hiệu HAPPYCO.
    3. CẤU TRÚC BÀI VIẾT:
       - Tiêu đề hấp dẫn, chuẩn SEO.
       - Đoạn mở đầu (Sapo): 2-3 câu ngắn gọn (~150 ký tự), nêu bật giá trị và giải pháp.
       - Thân bài: Đúng 4 mục <h2> được đánh số thứ tự (1., 2., 3., 4.).
       - Tại mỗi mục <h2>, BẮT BUỘC chèn đúng 1 thẻ <figure> giữ chỗ cho ảnh:
         <figure style="text-align: center; margin: 25px 0;">
             <img src="IMAGE_PLACEHOLDER_1" alt="[Mô tả chi tiết chuẩn SEO của ảnh 1]" style="max-width: 100%; height: auto; border-radius: 8px;" />
             <figcaption style="font-style: italic; color: #555; margin-top: 8px; font-size: 0.95em;">[Chú thích ảnh tự nhiên, tuyệt đối KHÔNG ghi 'Hình 1, Hình 2']</figcaption>
         </figure>
         (Tương ứng IMAGE_PLACEHOLDER_1 đến IMAGE_PLACEHOLDER_4 cho 4 mục).
       - Chèn 2 link nội bộ (internal link) tự nhiên vào từ khóa phù hợp:
         + Link 1: https://happyco.asia/tin-tuc
         + Link 2: https://happyco.asia/dich-vu
    4. CẤM TUYỆT ĐỐI:
       - KHÔNG ĐƯỢC CHÈN BẤT KỲ KHỐI LIÊN HỆ, ĐỊA CHỈ, HOTLINE, HOẶC CHỮ KÝ Ở CUỐI BÀI VIẾT! Website đã có sẵn 2 khối footer hệ thống cố định. Bài viết kết thúc tự nhiên ở phần kết bài của mục 4.
    5. IMAGE PROMPTS (5 ẢNH):
       - Tạo 5 prompt bằng tiếng Anh chi tiết để sinh ảnh AI (1 thumbnail + 4 ảnh minh họa cho 4 mục <h2>).
       - Yêu cầu ảnh: Photorealistic horizontal 16:9 widescreen, architectural and interior photography, luxury residential, warm natural lighting, pristine craftsmanship, no people face deformation, no watermarks, no text, no brand logos.

    TRẢ VỀ DUY NHẤT ĐỊNH DẠNG JSON HỢP LỆ VỚI CÁC TRƯỜNG SAU (KHÔNG DÙNG BACKTICKS HAY TEXT KHÁC NGOÀI JSON):
    {{
        "title": "Tiêu đề bài viết",
        "description": "Đoạn sapo mở đầu ngắn gọn",
        "content_html": "Toàn bộ mã HTML của thân bài (chứa 4 mục <h2> và 4 thẻ <figure> với placeholder)",
        "meta_title": "Tiêu đề SEO (dưới 70 ký tự)",
        "meta_description": "Mô tả SEO (dưới 160 ký tự)",
        "tags": "Từ khóa phân cách bằng dấu phẩy",
        "image_prompts": [
            {{
                "key": "thumb",
                "title_vi": "Tiêu đề SEO ảnh thumbnail",
                "alt_vi": "Mô tả alt ảnh thumbnail",
                "caption_vi": "Chú thích thumbnail",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic thumbnail image"
            }},
            {{
                "key": "h2_1",
                "title_vi": "Tiêu đề SEO ảnh mục 1",
                "alt_vi": "Mô tả alt ảnh mục 1",
                "caption_vi": "Chú thích ảnh mục 1",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image for heading 1"
            }},
            {{
                "key": "h2_2",
                "title_vi": "Tiêu đề SEO ảnh mục 2",
                "alt_vi": "Mô tả alt ảnh mục 2",
                "caption_vi": "Chú thích ảnh mục 2",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image for heading 2"
            }},
            {{
                "key": "h2_3",
                "title_vi": "Tiêu đề SEO ảnh mục 3",
                "alt_vi": "Mô tả alt ảnh mục 3",
                "caption_vi": "Chú thích ảnh mục 3",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image for heading 3"
            }},
            {{
                "key": "h2_4",
                "title_vi": "Tiêu đề SEO ảnh mục 4",
                "alt_vi": "Mô tả alt ảnh mục 4",
                "caption_vi": "Chú thích ảnh mục 4",
                "prompt_en": "Detailed English prompt for 16:9 photorealistic image for heading 4"
            }}
        ]
    }}
    """

    candidate_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]
    last_err = None

    for model_name in candidate_models:
        try:
            print(f"  [Generator] Đang gọi Gemini model '{model_name}'...")
            res = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            raw = res.text.strip()
            # Clean JSON formatting
            if raw.startswith("```json"):
                raw = raw[7:]
            elif raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            
            data = json.loads(raw.strip())
            
            # Post-processing verification: Remove any footer/signature box if accidentally generated
            content_html = data.get("content_html", "")
            cleaned_html = re.sub(r'<div[^>]*style="[^"]*border[^"]*"[^>]*>.*?</div>', '', content_html, flags=re.DOTALL | re.IGNORECASE)
            cleaned_html = re.sub(r'<p[^>]*>.*?Hotline.*?0946.*?272.*?286.*?</p>', '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
            cleaned_html = re.sub(r'<p[^>]*>.*?Địa chỉ công ty.*?</p>', '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
            data["content_html"] = cleaned_html.strip()

            return data
        except Exception as e:
            print(f"  [Generator] Model '{model_name}' gặp lỗi: {e}")
            last_err = e
            continue

    raise RuntimeError(f"All Gemini models failed: {last_err}")
