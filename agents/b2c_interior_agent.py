"""
Sub-Agent: Chuyên Gia Thiết Kế & Thi Công Nội Thất (B2C Interior Specialist)
Chuyên trách chuyên mục BLOG NỘI THẤT (ID: 266)
- Xoay tua liên tục 16 trục đề tài: Phong cách nội thất thế giới, Bài toán thi công thực tế, Sức khỏe & Không gian sống.
- Hạn chế tối đa nhôm, kính, mặt đá (chỉ làm điểm xuyết phụ <10%).
- Sinh tiêu đề mới hoàn toàn qua từng bài bằng bộ nhớ chống lặp & 6 kiểu tiêu đề xoay vòng.
- Luôn đi kèm duy nhất 1 khối viền xanh nét đứt chuẩn ở cuối bài (đi liền Banner web).
"""

import os
import sys
import json
import re
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

B2C_TOPIC_ANGLES = [
    # NHÓM 1: CÁC PHONG CÁCH NỘI THẤT ĐẸP TRÊN TOÀN THẾ GIỚI
    {
        "pool": "b2c_japandi",
        "keyword": "nội thất phong cách japandi gỗ sồi",
        "angle": "Giao thoa tối giản Nhật Bản và Bắc Âu (Japandi): phối vân gỗ sồi tự nhiên, chi tiết nan gỗ thanh thoát và khoảng thở tĩnh lặng cho nhà phố",
        "audience": "Chủ nhà yêu sự tinh tế & Kiến trúc sư",
    },
    {
        "pool": "b2c_wabisabi",
        "keyword": "phong cách wabi sabi mộc mạc tự nhiên",
        "angle": "Triết lý Wabi-Sabi trong nội thất gỗ công nghiệp vân sần sâu tự nhiên, gam màu đất ấm áp giúp giải tỏa áp lực sau giờ làm",
        "audience": "Người trẻ thành đạt tìm sự cân bằng",
    },
    {
        "pool": "b2c_scandinavian",
        "keyword": "nội thất scandinavian bắc âu sáng thoáng",
        "angle": "Phong cách Scandinavian Bắc Âu: nghệ thuật đón sáng tự nhiên, phối gỗ sáng màu với hệ tủ treo chân thoáng cho căn hộ vừa và nhỏ",
        "audience": "Vợ chồng trẻ mua căn hộ đầu tiên",
    },
    {
        "pool": "b2c_indochine",
        "keyword": "nội thất indochine đông dương gỗ trầm mây đan",
        "angle": "Hơi thở Indochine Đông Dương đương đại qua cánh tủ phay chỉ pano gỗ óc chó kết hợp lưới mây tự nhiên đan thủ công",
        "audience": "Gia chủ trung niên & người yêu nét Á Đông",
    },
    {
        "pool": "b2c_organic_modern",
        "keyword": "nội thất organic modern bo cong mềm mại",
        "angle": "Xu hướng Organic Modern: ứng dụng kỹ thuật uốn cong phôi gỗ CNC tạo đường bo tròn mềm mại, triệt tiêu góc nhọn trong nhà có trẻ nhỏ",
        "audience": "Gia đình có con nhỏ & Kiến trúc sư",
    },
    {
        "pool": "b2c_taiwanese",
        "keyword": "phong cách nội thất đài loan gỗ ấm tối giản",
        "angle": "Phong cách Đài Loan (Taiwanese Modern): phối gỗ màu óc chó/xám khói cùng rãnh âm đèn LED 3000K tạo chiều sâu cho phòng khách hiện đại",
        "audience": "Chủ nhà phố & căn hộ cao cấp",
    },

    # NHÓM 2: BÀI TOÁN THI CÔNG NỘI THẤT THỰC TẾ
    {
        "pool": "b2c_fix_columns",
        "keyword": "cách đóng tủ âm tường che cột dầm nhà ống",
        "angle": "Bài toán nhà phố lộ cột bê tông và dầm ngang thô kệch: kỹ thuật đóng tủ gỗ may đo ôm khít tường và biến góc chết thành hộc kệ trưng bày",
        "audience": "Chủ nhà đang hoàn thiện phần thô nhà ống",
    },
    {
        "pool": "b2c_fix_moisture",
        "keyword": "chống ẩm mốc chân tủ tầng trệt",
        "angle": "Bài toán ẩm nồm tầng trệt và tường giáp nhà vệ sinh: kỹ thuật đôn chân nhựa kháng ẩm ngầm, cốt ván xanh HMR và nẹp PUR khóa ẩm mép gỗ",
        "audience": "Chủ nhà khu vực ẩm thấp / tầng trệt",
    },
    {
        "pool": "b2c_fix_3d_reality",
        "keyword": "thi công nội thất giống bản vẽ 3d đo laser",
        "angle": "Vì sao nhiều nhà nhận bàn giao nội thất thực tế khác xa bản vẽ 3D? Quy trình bắn tia laser hiện trạng và bóc file CNC dung sai 0.2mm",
        "audience": "Gia chủ chuẩn bị ký hợp đồng thi công",
    },
    {
        "pool": "b2c_fix_budget",
        "keyword": "kinh nghiệm dự toán chi phí nội thất tránh phát sinh",
        "angle": "Bài toán phân bổ ngân sách hoàn thiện nội thất trọn gói: khu vực nào cần dùng ván chịu ẩm cao cấp, chỗ nào tối ưu để tiết kiệm 20% chi phí",
        "audience": "Vợ chồng trẻ cân đối tài chính làm nhà",
    },
    {
        "pool": "b2c_fix_acoustic",
        "keyword": "vách ốp gỗ tiêu âm phòng làm việc phòng ngủ",
        "angle": "Giải pháp giảm tiếng ồn đường phố cho nhà mặt tiền bằng vách ốp lam gỗ tiêu âm kết hợp nỉ acoustic trong phòng ngủ và phòng làm việc",
        "audience": "Nhà mặt tiền đường lớn / người làm việc từ xa",
    },

    # NHÓM 3: KHÔNG GIAN SỐNG, CÔNG NĂNG & SỨC KHỎE GIA ĐÌNH
    {
        "pool": "b2c_health_e0",
        "keyword": "cốt ván e0 e1 không mùi an toàn trẻ nhỏ",
        "angle": "Mùi hăng cay mắt từ nội thất mới đóng đến từ đâu? Cách nhận biết ván công nghiệp đạt chuẩn phát thải E0/E1 bảo vệ hô hấp cho bé",
        "audience": "Gia đình có trẻ sơ sinh & mẹ bầu",
    },
    {
        "pool": "b2c_tatami_small",
        "keyword": "giường bục tatami tủ âm tường phòng nhỏ",
        "angle": "Biến phòng ngủ nhỏ 9m2 thành không gian đa năng với giường bục Tatami ngăn kéo ngầm kết hợp tủ áo và bàn làm việc liền khối",
        "audience": "Căn hộ chung cư 1-2 phòng ngủ & nhà phố nhỏ",
    },
    {
        "pool": "b2c_kids_ergonomic",
        "keyword": "phòng ngủ trẻ em bàn học công thái học",
        "angle": "Thiết kế phòng ngủ giúp con tự lập: bố trí giường tầng gỗ chắc chắn bo tròn cạnh, thang hộp chứa đồ chơi và bàn học lấy sáng chuẩn chống gù",
        "audience": "Cha mẹ có con từ 4-12 tuổi",
    },
    {
        "pool": "b2c_home_office",
        "keyword": "thiết kế góc làm việc tại nhà home office",
        "angle": "Thiết kế góc Home Office ngay trong phòng ngủ hoặc gầm cầu thang: bàn gỗ giấu dây điện âm, hệ kệ sách treo chịu lực gọn gàng",
        "audience": "Người làm việc từ xa / freelancer / quản lý",
    },
    {
        "pool": "b2c_multigen_living",
        "keyword": "phòng khách gỗ ấm gắn kết đa thế hệ",
        "angle": "Thiết kế phòng khách gắn kết 3 thế hệ: lối đi rộng cho ông bà, bàn trà bo tròn an toàn cho cháu nhỏ và hệ kệ tivi giấu dây gọn gàng",
        "audience": "Gia đình 3 thế hệ sống chung",
    },
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

        chosen = pick_least_used_topic(B2C_TOPIC_ANGLES, "BLOG NỘI THẤT")
        formula = pick_next_formula("BLOG NỘI THẤT")
        history = load_history()
        recent_titles_str = "\n".join(f"- {h['title']}" for h in history[:10])

        angle_desc = topic_title if topic_title else chosen["angle"]
        keyword = chosen["keyword"]
        pool = chosen["pool"]
        audience = chosen["audience"]

        extra_feedback = ""
        final_data = None

        for attempt in range(2):
            title_instruction = (
                f'Sử dụng đúng tiêu đề được chỉ định: "{topic_title}"'
                if topic_title else
                f"""TỰ SÁNG TÁC 1 TIÊU ĐỀ HOÀN TOÀN MỚI THEO KIỂU: [{formula['name']}]
                - Quy tắc kiểu này: {formula['rule']}
                - Ví dụ tham khảo phong cách (KHÔNG copy): "{formula['b2c_example']}"
                - CẤM TUYỆT ĐỐI lặp cấu trúc "Thiết Kế X: Y Tại Happyco" hay lặp các từ sáo rỗng: {', '.join(BANNED_TITLE_CLICHES)}!
                {extra_feedback}"""
            )

            prompt = f"""
            Bạn là Chuyên gia Kiến trúc & Thi công Nội thất gỗ của CÔNG TY CỔ PHẦN HAPPYCO (Biên Hòa, Đồng Nai).
            Hãy viết 1 bài viết chuyên sâu, giàu góc nhìn thực tế để đăng lên website happyco.asia:

            CHUYÊN MỤC: BLOG NỘI THẤT (cat_id: 266)
            TRỤC CHỦ ĐỀ BẮT BUỘC: {angle_desc}
            TỪ KHÓA TRỌNG TÂM: {keyword}
            ĐỐI TƯỢNG ĐỘC GIẢ: {audience}

            DANH SÁCH CÁC TIÊU ĐỀ ĐÃ ĐĂNG GẦN ĐÂY (TUYỆT ĐỐI KHÔNG TRÙNG Ý TƯỞNG HAY CÁCH ĐẶT TÊN):
            {recent_titles_str}

            YÊU CẦU ĐẶT TIÊU ĐỀ:
            {title_instruction}

            LỆNH ĐẶC BIỆT VỀ NỘI DUNG (PHẢI TUÂN THỦ 100%):
            1. HẠN CHẾ TỐI ĐA NHÔM, KÍNH, MẶT ĐÁ: Những vật liệu này chỉ nhắc thoáng qua như điểm xuyết nhỏ (dưới 10% bài), KHÔNG lấy làm chủ đề chính!
            2. XOÁY SÂU VÀO NGHỀ MỘC & KHÔNG GIAN SỐNG: Giải pháp gỗ may đo, kết cấu mộc tinh xảo (bo cong CNC an toàn, rãnh âm LED 3000K, khe shadow gap, nẹp PUR noline không vết keo), cốt ván xanh HMR chuẩn E0/E1 bảo vệ sức khỏe, phong thủy/luồng sáng, câu chuyện thực tế khi thi công tại công trình.
            3. VĂN PHONG WEBSITE CHUYÊN NGHIỆP:
               - CẤM chào hỏi mạng xã hội ('Chào các bạn', 'Chào anh em'...), CẤM xưng tôi ('Tôi là...').
               - Mô tả (description): 140-160 ký tự tóm tắt thẳng vấn đề/giải pháp, CẤM mở đầu bằng 'Bài viết...'.
               - CẤM nhắc thương hiệu đối thủ (An Cường, Ba Thanh, Mộc Phát...).
               - CẤM tự ý viết thêm khối địa chỉ hay hotline ở cuối bài (code hậu kiểm sẽ tự ghép duy nhất 1 khối viền xanh chuẩn ở cuối).
            4. CHÈN 2-3 LINK NỘI BỘ TỰ NHIÊN:
               - <a href="https://happyco.asia/gioi-thieu.html">Happyco</a>
               - <a href="https://happyco.asia/blog.html">kinh nghiệm thiết kế nội thất</a>
            5. CẤU TRÚC 4 MỤC <h2> CHUYÊN SÂU, mỗi mục có 1 ảnh:
               <p style="text-align: center; margin: 25px 0;">
                 <img src="IMAGE_PLACEHOLDER_1" alt="[Mô tả ảnh nội thất thực tế]" style="width: 100%; max-width: 800px; height: auto; border-radius: 8px;" />
                 <br />
                 <em style="color: #666; font-size: 14px;">[Chú thích tự nhiên, CẤM ghi Hình 1, Hình 2]</em>
               </p>

            TRẢ VỀ DUY NHẤT 1 JSON HỢP LỆ (KHÔNG MARKDOWN DƯ THỪA):
            {{
                "title": "...",
                "slug": "...",
                "description": "...",
                "keywords": "{keyword}, nội thất gỗ may đo, xưởng mộc biên hòa đồng nai",
                "category": "BLOG NỘI THẤT",
                "cat_id": 266,
                "pool": "{pool}",
                "formula_id": "{formula['id']}",
                "content_html": "<p>...</p><h2>1. ...</h2>...<h2>2. ...</h2>...<h2>3. ...</h2>...<h2>4. ...</h2>..."
            }}
            """

            response = None
            for model_name in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash-lite"]:
                try:
                    response = client.models.generate_content(model=model_name, contents=prompt)
                    if response and response.text:
                        break
                except Exception as e:
                    print(f"Warning: Model {model_name} failed: {e}")

            if not response or not response.text:
                raise RuntimeError("Failed to generate B2C content!")

            raw = response.text.strip()
            if raw.startswith("```json"): raw = raw[7:]
            elif raw.startswith("```"): raw = raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            data = json.loads(raw.strip())

            # Clean web tone
            desc = re.sub(r'^(?:Bài viết|Bài viết này|Bài viết chia sẻ)\s*[:,-]?\s*', '', data.get("description", ""), flags=re.I).strip()
            data["description"] = desc
            data["category"] = "BLOG NỘI THẤT"
            data["cat_id"] = "266"
            data["pool"] = pool
            data["formula_id"] = formula["id"]
            data["content_html"] = ensure_green_box(data.get("content_html", ""))

            if topic_title:
                final_data = data
                break

            ok, reason = check_title_freshness(data["title"], "BLOG NỘI THẤT")
            if ok:
                final_data = data
                break
            extra_feedback = f"\n⚠️ LẦN TRƯỚC TIÊU ĐỀ '{data['title']}' BỊ TỪ CHỐI VÌ: {reason}. BẮT BUỘC ĐỔI CÁCH DIỄN ĐẠT KHÁC HOÀN TOÀN!"
            final_data = data

        return final_data
