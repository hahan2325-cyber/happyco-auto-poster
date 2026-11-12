"""
Sub-Agent: Chuyên Gia Gia Công Ván Công Nghiệp (B2B Woodworking Specialist)
Chuyên trách chuyên mục GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265)
- Xoay tua 12 trục đề tài kỹ thuật xưởng B2B (không bao giờ lặp lại).
- Tự động đổi kiểu đặt tiêu đề qua 6 cấu trúc (hỏi đáp, con số, so sánh, hướng dẫn, câu chuyện xưởng, phản biện).
- Chặn từ khóa sáo rỗng lặp đi lặp lại ("Chống Nước Tuyệt Đối", "Đột Phá", "Tại Xưởng Happyco"...).
- Luôn giữ duy nhất 1 khối viền xanh nét đứt chuẩn ở cuối bài (đi liền Banner web).
"""

import os
import sys
import re
import json
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from core.topic_memory import (
    load_history,
    pick_least_used_topic,
    pick_next_formula,
    check_title_freshness,
    ensure_green_box,
    BANNED_TITLE_CLICHES,
)

B2B_TOPIC_ANGLES = [
    {
        "pool": "b2b_abf_mistakes",
        "keyword": "lỗi xuất file abf sketchup cắt cnc",
        "angle": "Những lỗi kỹ thuật thường gặp khi xuất file SketchUp ABF đi cắt CNC (trùng mặt, ngược chiều vân gỗ, sai độ dày ván, thiếu kích thước cạnh dán) khiến xưởng hao phôi 15-20%",
    },
    {
        "pool": "b2b_nesting_opt",
        "keyword": "tối ưu sơ đồ cắt nesting tấm 1220x2440",
        "angle": "Kỹ thuật xếp sơ đồ cắt Nesting thông minh trên khổ ván 1220x2440mm để gom tối đa chi tiết tủ áo, giảm đề xê vụn gỗ và tận dụng tấm nguyên còn dư",
    },
    {
        "pool": "b2b_plywood_vs_mdf",
        "keyword": "so sánh plywood và mdf lõi xanh làm thùng bếp",
        "angle": "So sánh thực tế độ bám vít, độ trương nở khi ngâm nước và chi phí gia công giữa cốt ván ép Plywood và MDF lõi xanh HMR cho thùng tủ bếp, lavabo",
    },
    {
        "pool": "b2b_6side_drilling",
        "keyword": "khoan cam chốt tự động 6 mặt cnc",
        "angle": "Gia công khoan liên kết cam chốt 6 mặt tự động cho dự án chung cư/khách sạn số lượng lớn: kiểm soát dung sai 0.2mm giúp thợ lắp ráp nhanh gấp đôi tại công trình",
    },
    {
        "pool": "b2b_carbide_chipping",
        "keyword": "chống mẻ dăm cạnh melamine laminate khi cắt cnc",
        "angle": "Nguyên nhân cạnh ván Melamine và Laminate hay bị mẻ dăm li ti sau cắt: cách chọn dao phay xoắn carbide kim cương và hiệu chỉnh tốc độ bàn hút chân không",
    },
    {
        "pool": "b2b_outsource_vs_capex",
        "keyword": "thuê gia công cnc hay đầu tư dàn máy xưởng mộc",
        "angle": "Bài toán tài chính cho xưởng mộc quy mô 5-12 thợ: nên tự vay đầu tư dàn máy CNC + dán cạnh PUR gần 2 tỷ hay thuê gia công theo file để giải phóng mặt bằng và dòng vốn?",
    },
    {
        "pool": "b2b_curved_cnc",
        "keyword": "gia công uốn cong phôi gỗ cnc quầy lễ tân vách",
        "angle": "Kỹ thuật cắt rãnh kerfing và ghép phay CNC tạo phôi ván uốn cong R nhỏ dùng cho quầy bar, quầy lễ tân, bàn đảo và vách ngăn bo tròn",
    },
    {
        "pool": "b2b_acoustic_cnc",
        "keyword": "gia công vách tiêu âm đục lỗ soi rãnh cnc",
        "angle": "Gia công vách gỗ tiêu âm đục lỗ và soi rãnh sáo cho hội trường, phòng họp, rạp hát gia đình bằng trung tâm CNC tốc độ cao",
    },
    {
        "pool": "b2b_fluted_shaker",
        "keyword": "phay cánh huỳnh tân cổ điển cnc soi lam sóng",
        "angle": "Gia công cánh tủ phay huỳnh pano Tân Cổ Điển và vách lam sóng 3D sắc nét trên cốt MDF tỷ trọng cao sẵn sàng sơn bệt hoặc ép màng",
    },
    {
        "pool": "b2b_led_shadowgap",
        "keyword": "phay rãnh âm led nhôm định hình shadow gap",
        "angle": "Gia công sẵn rãnh âm gắn thanh nhôm đèn LED và đường khe bóng shadow gap chính xác bằng máy CNC ngay tại xưởng trước khi bàn giao kiện phôi",
    },
    {
        "pool": "b2b_barcode_flatpack",
        "keyword": "đóng gói dán tem mã vạch barcode giao công trình",
        "angle": "Quy trình quản lý hàng trăm chi tiết tủ không thất lạc nhờ phần mềm in tem mã vạch Barcode định danh từng tấm và đóng kiện pallet flat-pack giao công trình tỉnh",
    },
    {
        "pool": "b2b_pur_maintenance",
        "keyword": "kiểm soát keo dán cạnh pur chịu nhiệt độ ẩm",
        "angle": "Tại sao đường dán cạnh keo PUR bám dính gấp 3 lần keo EVA? Tìm hiểu nhiệt độ nồi keo chuẩn và kiểm soát độ dày màng keo dưới 0.05mm tại xưởng công nghiệp",
    },
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

        chosen = pick_least_used_topic(B2B_TOPIC_ANGLES, "GIA CÔNG VÁN")
        formula = pick_next_formula("GIA CÔNG VÁN")
        history = load_history()
        recent_titles_str = "\n".join(f"- {h['title']}" for h in history[:10])

        angle_desc = topic_title if topic_title else chosen["angle"]
        keyword = chosen["keyword"]
        pool = chosen["pool"]

        extra_feedback = ""
        final_data = None

        for attempt in range(2):
            title_instruction = (
                f'Sử dụng đúng tiêu đề được chỉ định: "{topic_title}"'
                if topic_title else
                f"""TỰ SÁNG TÁC 1 TIÊU ĐỀ HOÀN TOÀN MỚI THEO KIỂU: [{formula['name']}]
                - Quy tắc kiểu này: {formula['rule']}
                - Ví dụ tham khảo phong cách (KHÔNG copy): "{formula['b2b_example']}"
                - CẤM TUYỆT ĐỐI lặp cấu trúc "Gia Công X: Y Cho Xưởng Mộc Tại Happyco" hay lặp các từ sáo rỗng: {', '.join(BANNED_TITLE_CLICHES)}!
                {extra_feedback}"""
            )

            prompt = f"""
            Bạn là Kỹ sư Cơ Khí Chế Biến Gỗ Công Nghiệp & Quản Lý Sản Xuất của XƯỞNG GIA CÔNG HAPPYCO (Biên Hòa, Đồng Nai).
            Hãy viết 1 bài viết kỹ thuật B2B thực chiến xuất bản trên website happyco.asia:

            CHUYÊN MỤC: GIA CÔNG VÁN CÔNG NGHIỆP (cat_id: 265)
            TRỤC CHỦ ĐỀ BẮT BUỘC: {angle_desc}
            TỪ KHÓA CHÍNH: {keyword}

            DANH SÁCH CÁC TIÊU ĐỀ ĐÃ ĐĂNG GẦN ĐÂY (TUYỆT ĐỐI KHÔNG TRÙNG Ý TƯỞNG HAY CÁCH ĐẶT TÊN):
            {recent_titles_str}

            YÊU CẦU ĐẶT TIÊU ĐỀ:
            {title_instruction}

            QUY CHUẨN VĂN PHONG KỸ THUẬT B2B TRÊN WEBSITE:
            - Độc giả: Chủ xưởng mộc vừa & nhỏ, thợ thi công công trình, kiến trúc sư dự án.
            - TUYỆT ĐỐI CẤM chào hỏi kiểu Facebook ('Chào anh em', 'Xin chào các bác thợ'...), CẤM tự xưng ('Tôi là kỹ sư...', 'Với tư cách là...').
            - Mô tả (description): 140-160 ký tự tóm tắt thẳng thông số/bài toán kỹ thuật, CẤM bắt đầu bằng 'Bài viết...'.
            - CẤM nhắc thương hiệu đối thủ/nhà phân phối (An Cường, Ba Thanh, Mộc Phát...).
            - CẤM tự ý chèn khung địa chỉ/hotline cuối bài (hậu kiểm sẽ tự ghép duy nhất 1 khối viền xanh chuẩn ở cuối).

            BẮT BUỘC CHÈN 2-3 LINK NỘI BỘ TỰ NHIÊN:
            - <a href="https://happyco.asia/gioi-thieu.html">xưởng gia công Happyco</a>
            - <a href="https://happyco.asia/dich-vu/gia-cong-van-hmr-phu-melamine-theo-file-abf-tai-bien-hoa.html">gia công ván theo file ABF</a>

            CẤU TRÚC 4 MỤC <h2> CHUYÊN SÂU KÈM ẢNH:
            Mỗi mục <h2> có khối ảnh căn giữa (img src="IMAGE_PLACEHOLDER_1" .. _4, CẤM ghi Hình 1, Hình 2 trong chú thích).

            BỘ 5 IMAGE PROMPTS (THỰC TẾ XƯỞNG MỘC VIỆT NAM - DOCUMENTARY PHOTOGRAPHY):
            - Tất cả phải là ảnh phóng sự chụp máy cầm tay ngang tầm mắt trong xưởng gỗ Việt Nam thực tế, ánh sáng đèn tuýp LED nhà xưởng, sàn bê tông có mùn cưa mịn, 16:9 widescreen, zero CGI gloss, zero 3D render look.

            TRẢ VỀ DUY NHẤT 1 JSON HỢP LỆ (KHÔNG MARKDOWN THỪA):
            {{
                "title": "...",
                "slug": "...",
                "description": "...",
                "meta_description": "...",
                "keywords": "{keyword}, gia công ván công nghiệp đồng nai, cắt cnc dán cạnh pur",
                "category": "GIA CÔNG VÁN CÔNG NGHIỆP",
                "cat_id": "265",
                "pool": "{pool}",
                "formula_id": "{formula['id']}",
                "content_html": "<p>...</p><h2>1. ...</h2>...<h2>2. ...</h2>...<h2>3. ...</h2>...<h2>4. ...</h2>...",
                "image_prompts": [
                    {{"key": "thumb", "caption_vi": "...", "prompt_en": "Documentary photography, handheld eye-level wide shot in a real Vietnamese industrial woodworking workshop... zero CGI gloss, 16:9 widescreen"}},
                    {{"key": "h2_1", "caption_vi": "...", "prompt_en": "Documentary photography, handheld close-up... zero CGI gloss, 16:9 widescreen"}},
                    {{"key": "h2_2", "caption_vi": "...", "prompt_en": "Documentary photography, handheld medium shot... zero CGI gloss, 16:9 widescreen"}},
                    {{"key": "h2_3", "caption_vi": "...", "prompt_en": "Documentary photography, handheld eye-level... zero CGI gloss, 16:9 widescreen"}},
                    {{"key": "h2_4", "caption_vi": "...", "prompt_en": "Documentary photography, handheld candid shot... zero CGI gloss, 16:9 widescreen"}}
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
                    print(f"Warning: Model {model_name} failed: {e}")

            if not res or not res.text:
                raise RuntimeError("Failed to generate B2B content!")

            raw = res.text.strip()
            if raw.startswith("```json"): raw = raw[7:]
            elif raw.startswith("```"): raw = raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            data = json.loads(raw.strip())

            data["category"] = "GIA CÔNG VÁN CÔNG NGHIỆP"
            data["cat_id"] = "265"
            data["pool"] = pool
            data["formula_id"] = formula["id"]

            desc = re.sub(r'^(?:Bài viết|Bài viết này|Bài viết chia sẻ)\s*[:,-]?\s*', '', data.get("description", ""), flags=re.I).strip()
            data["description"] = desc
            data["meta_description"] = desc
            data["content_html"] = ensure_green_box(data.get("content_html", ""))

            if topic_title:
                final_data = data
                break

            ok, reason = check_title_freshness(data["title"], "GIA CÔNG VÁN CÔNG NGHIỆP")
            if ok:
                final_data = data
                break
            extra_feedback = f"\n⚠️ LẦN TRƯỚC TIÊU ĐỀ '{data['title']}' BỊ TỪ CHỐI VÌ: {reason}. BẮT BUỘC VIẾT TIÊU ĐỀ HOÀN TOÀN MỚI!"
            final_data = data

        return final_data
