"""
Topic Memory & Anti-Repetition Engine cho toàn bộ hệ thống Sub-Agent Happyco.
- Lưu trữ lịch sử các bài đã đăng để tuyệt đối không trùng ý tưởng, không lặp lại cấu trúc tiêu đề.
- Xoay vòng 6 kiểu đặt tiêu đề (Title Formulas) khác nhau hoàn toàn qua từng bài.
- Chặn các từ khóa sáo rỗng lặp đi lặp lại ("Chống Nước Tuyệt Đối", "Đẳng Cấp Sang Trọng", "Tại Xưởng Happyco"...).
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Any

HISTORY_FILE = Path(__file__).resolve().parent / "published_history.json"

BANNED_TITLE_CLICHES = [
    "chống nước tuyệt đối",
    "đẳng cấp sang trọng",
    "đột phá",
    "tại xưởng happyco",
    "từ xưởng happyco",
    "cho xưởng mộc",
    "bền bỉ vượt thời gian",
    "hoàn hảo cho mọi nhà",
    "vẻ đẹp vĩnh cửu",
]

TITLE_FORMULAS = [
    {
        "id": "question_pain",
        "name": "Kiểu 1: Câu hỏi thực chiến / Nỗi đau thường gặp",
        "rule": "Đặt câu hỏi trực diện vào 1 vấn đề cụ thể người đọc đang đau đầu + gợi mở giải pháp. CẤM dùng dấu hai chấm ':'.",
        "b2b_example": "Vì Sao Cạnh Ván Melamine Hay Bị Mẻ Dăm Khi Chạy Tốc Độ Cao? Cách Chọn Dao Phay Và Căn Tốc Độ Trục",
        "b2c_example": "Nhà Phố Mặt Tiền 4m Có Nên Làm Tủ Áo Kịch Trần? Cách Chia Khoang Để Phòng Không Bị Ngợp"
    },
    {
        "id": "number_mistakes",
        "name": "Kiểu 2: Con số cụ thể / Sai lầm / Kinh nghiệm đúc kết",
        "rule": "Bắt đầu bằng con số (3, 4, 5, 7...) về sai lầm, tiêu chí hoặc bí quyết thực tế. CẤM viết kiểu 'A: B & C'.",
        "b2b_example": "5 Lỗi Xuất File SketchUp ABF Khiến Xưởng Mộc Hao Phôi Tới 18% Trước Khi Đưa Lên Máy CNC",
        "b2c_example": "4 Điểm Khác Biệt Giữa Nội Thất Japandi Và Bắc Âu Khi Ứng Dụng Vào Căn Hộ Chung Cư Việt"
    },
    {
        "id": "direct_comparison",
        "name": "Kiểu 3: So sánh trực diện / Lựa chọn A hay B",
        "rule": "So sánh hai vật liệu, công nghệ hoặc phương án thi công trong tình huống thực tế. Ngắn gọn, súc tích.",
        "b2b_example": "Đóng Thùng Bếp Bằng Plywood Hay MDF Lõi Xanh? Bảng Đo Độ Trương Nở Sau 72 Giờ Ngâm Nước",
        "b2c_example": "Chọn Cánh Tủ Phủ Laminate Hay Melamine Cho Nhà Có Trẻ Nhỏ Hiếu Động?"
    },
    {
        "id": "practical_guide",
        "name": "Kiểu 4: Bí quyết / Giải pháp xử lý bài toán khó",
        "rule": "Tập trung vào 'Cách làm / Bí quyết xử lý' 1 bài toán hóc búa (cột dầm lộ, ẩm tầng trệt, lệch 3D, tối ưu đề xê...).",
        "b2b_example": "Cách Xếp Phôi Nesting Trên Tấm 1220x2440 Để Gom Đủ Bộ Tủ Áo Mà Vẫn Dư Tấm Nguyên",
        "b2c_example": "Cách Giấu Trọn Cột Bê Tông Và Dầm Ngang Nhà Ống Bằng Hệ Tủ Gỗ May Đo Phẳng Mịn"
    },
    {
        "id": "story_process",
        "name": "Kiểu 5: Hành trình quy trình / Hậu trường thực tế",
        "rule": "Kể góc nhìn từ bên trong xưởng hoặc hành trình từ bản vẽ ra thực tế công trình. Tự nhiên như báo chí.",
        "b2b_example": "Từ File Bản Vẽ 3D Đến Kiện Phôi Dán Tem Mã Vạch Giao Công Trình Trong 48 Giờ",
        "b2c_example": "Sống Chậm Giữa Nhịp Đô Thị Với Phòng Ngủ Gỗ Sồi Bo Cong Phong Cách Organic Modern"
    },
    {
        "id": "myth_buster",
        "name": "Kiểu 6: Góc nhìn phản biện / Đập tan hiểu lầm",
        "rule": "Đặt lại vấn đề ngược tư duy số đông (làm rõ cái giá rẻ vs đắt, sai lầm chọn vật liệu theo cảm tính).",
        "b2b_example": "Tự Mua Dàn Máy 2 Tỷ Hay Thuê Cắt CNC Theo File? Bài Toán Khấu Hao Cho Xưởng Mộc Dưới 10 Thợ",
        "b2c_example": "Đừng Chỉ Nhìn Bảng Giá Rẻ Khi Đóng Tủ Gỗ: Cách Nhận Biết Cốt Ván E1 An Toàn Cho Hệ Hô Hấp Trẻ Nhỏ"
    }
]


def load_history() -> List[Dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def record_published(title: str, cat: str, formula_id: str = "custom", pool: str = "") -> None:
    history = load_history()
    # Avoid exact duplicates in log
    if not any(h.get("title", "").strip().lower() == title.strip().lower() for h in history):
        history.insert(0, {
            "title": title.strip(),
            "cat": cat.strip(),
            "formula": formula_id,
            "pool": pool
        })
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[:60], f, ensure_ascii=False, indent=2)


def _normalize_tokens(text: str) -> set:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    stop = {"và", "cho", "của", "tại", "với", "trong", "khi", "để", "các", "một", "những", "từ", "đến", "hay", "bằng", "theo", "là", "gì", "cách"}
    return {w for w in cleaned.split() if len(w) > 1 and w not in stop}


def check_title_freshness(new_title: str, category: str = "") -> Tuple[bool, str]:
    """Kiểm tra tiêu đề mới có chuẩn SEO (45-65 ký tự), không sáo rỗng, không lặp từ và không trùng bài cũ."""
    title_len = len(new_title.strip())
    if title_len > 65:
        return False, f"Tiêu đề quá dài ({title_len} ký tự). Chuẩn SEO Google bắt buộc độ dài từ 45 đến 65 ký tự để không bị cắt trên SERP!"
    if title_len < 40:
        return False, f"Tiêu đề quá ngắn ({title_len} ký tự). Chuẩn SEO cần từ 45 đến 65 ký tự chứa từ khóa trọng tâm!"

    low = new_title.lower().strip()
    for cliche in BANNED_TITLE_CLICHES:
        if cliche in low:
            return False, f"Tiêu đề chứa cụm từ sáo rỗng lặp lại nhiều lần ('{cliche}'). Phải viết tự nhiên, mới mẻ hơn!"

    history = load_history()
    new_tokens = _normalize_tokens(new_title)
    if len(new_tokens) < 4:
        return False, "Tiêu đề quá ngắn, thiếu nội dung cụ thể."

    for item in history[:20]:
        old_title = item.get("title", "")
        old_tokens = _normalize_tokens(old_title)
        if not old_tokens:
            continue
        overlap = len(new_tokens & old_tokens) / max(1, min(len(new_tokens), len(old_tokens)))
        if overlap >= 0.58:
            return False, f"Tiêu đề trùng ý/từ khóa ({int(overlap*100)}%) với bài đã đăng: '{old_title}'"

    return True, "PASS"


def check_keywords_seo(keywords: str) -> Tuple[bool, str]:
    """Kiểm tra từ khóa có chuẩn SEO (2-3 cụm từ ngắn gọn, tổng dưới 70 ký tự)."""
    parts = [k.strip() for k in keywords.split(",") if k.strip()]
    if len(parts) > 3:
        return False, f"Quá nhiều từ khóa ({len(parts)} cụm). Chuẩn SEO chỉ nên có 2-3 cụm từ khóa ngắn gọn!"
    if len(keywords.strip()) > 70:
        return False, f"Từ khóa quá dài ({len(keywords.strip())} ký tự). Chuẩn SEO cần súc tích dưới 70 ký tự!"
    return True, "PASS"


def pick_next_formula(category_prefix: str = "") -> Dict[str, str]:
    """Chọn kiểu tiêu đề tiếp theo khác với 3 bài gần nhất của chuyên mục (xoay tua ngẫu nhiên trong tập chưa dùng)."""
    import random
    history = load_history()
    cat_items = [
        h for h in history
        if not category_prefix or category_prefix.upper() in h.get("cat", "").upper()
    ]
    recent_formulas = [h.get("formula") for h in cat_items[:3]]

    candidates = [f for f in TITLE_FORMULAS if f["id"] not in recent_formulas]
    if not candidates:
        candidates = TITLE_FORMULAS
    return random.choice(candidates)


def pick_least_used_topic(topics: List[Dict[str, Any]], category_prefix: str = "") -> Dict[str, Any]:
    """Xoay tua chủ đề chưa dùng gần đây (ưu tiên tuyệt đối pool & keyword chưa xuất hiện trong 10 bài gần nhất)."""
    history = load_history()
    recent_items = [
        h for h in history
        if not category_prefix or category_prefix.upper() in h.get("cat", "").upper()
    ][:12]
    recent_text = " ".join(h.get("title", "").lower() for h in recent_items)
    recent_pools = {h.get("pool") for h in recent_items if h.get("pool")}

    scored = []
    for i, topic in enumerate(topics):
        pool = topic.get("pool", "")
        kw_tokens = _normalize_tokens(topic.get("keyword", "") + " " + topic.get("angle", ""))
        hit_count = sum(1 for t in kw_tokens if t in recent_text)
        pool_penalty = 50 if pool in recent_pools else 0
        scored.append((pool_penalty + hit_count, i, topic))

    scored.sort(key=lambda x: x[0])
    return scored[0][2]


MANDATORY_GREEN_BOX = """<div style="border: 2px dashed #008848; background: #f6fff9; border-radius: 8px; padding: 18px 22px; margin: 28px 0;">
  <p style="color: #008848; font-weight: bold; margin: 0 0 8px 0; font-size: 16px;">Chúng Tôi Nhận Thiết Kế Nội Thất Ngành Mộc Tại Các Khu Vực Sau:</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">- Miền Nam: Thành phố Hồ Chí Minh, Đồng Nai, Tây Ninh, Thành phố Cần Thơ, Vĩnh Long, Đồng Tháp, Cà Mau, An Giang.</p>
  <p style="margin: 6px 0; color: #333; line-height: 1.6;">📍 <strong>Địa chỉ công ty:</strong> 526/2, Khu phố 8A, Phường Long Bình, thành phố Đồng Nai.</p>
  <p style="margin: 6px 0; color: #d32f2f; font-weight: bold; font-size: 16px;">📞 Liên hệ: 0946 272 286 (Đức Anh)</p>
</div>"""


def ensure_green_box(content_html: str) -> str:
    """Làm sạch mọi khung chân trang tự chế và gắn duy nhất 1 khối viền xanh nét đứt chuẩn ở cuối bài (đi liền với Banner web)."""
    cleaned = re.sub(r'(?:<hr[^>]*>\s*)?<div[^>]*class=["\'][^"\']*happyco-footer[^"\']*["\'][^>]*>[\s\S]*?</div>', '', content_html, flags=re.I)
    cleaned = re.sub(r'(?:<hr[^>]*>\s*)?<div[^>]*>[\s\S]*?526/2[\s\S]*?0946\s*272\s*286[\s\S]*?</div>', '', cleaned, flags=re.I)
    return cleaned.strip() + "\n" + MANDATORY_GREEN_BOX
