"""
Chief QA Agent - Tổng Biên Tập Kiểm Duyệt Chất Lượng Xuất Bản Happyco
Kiểm duyệt nghiêm ngặt tiêu chuẩn SEO, chống trùng lặp tiêu đề, cấm chèn chân trang trùng với web,
và đảm bảo văn phong chuyên nghiệp trước khi xuất bản.
"""

import re
import hashlib
from typing import Dict, Any, List
from core.topic_memory import check_title_freshness, check_keywords_seo

BANNED_BRANDS = ["an cường", "an cuong", "ba thanh", "mộc phát", "moc phat", "panel plus"]

class ChiefQAAgent:
    def __init__(self):
        self.name = "Chief QA Agent (Tổng Biên Tập)"

    def audit(self, article: Dict[str, Any], image_files: List[str] = None) -> Dict[str, Any]:
        """Kiểm duyệt toàn diện bài viết và bộ ảnh trước khi cho phép xuất bản"""
        report = {
            "passed": True,
            "checks": {},
            "warnings": [],
            "errors": []
        }

        title = article.get("title", "")
        content_html = article.get("content_html", "")
        full_text = f"{title} {article.get('description', '')} {content_html}".lower()

        # 1. Kiểm tra thương hiệu cấm (100% chỉ tôn vinh thương hiệu Happyco)
        found_banned = [b for b in BANNED_BRANDS if b in full_text]
        if found_banned:
            report["passed"] = False
            report["errors"].append(f"Vi phạm thương hiệu: Tìm thấy đối thủ/nhà phân phối ({found_banned}). Phải dùng từ ngữ kỹ thuật chung!")
            report["checks"]["no_banned_brands"] = "FAIL"
        else:
            report["checks"]["no_banned_brands"] = "PASS"

        # 2. BẮT BUỘC PHẢI CÓ KHỐI VIỀN XANH NÉT ĐỨT CỐ ĐỊNH ĐI LIỀN VỚI BANNER WEB (CHỈ 1 KHỐI DUY NHẤT)
        has_green_box = bool(
            re.search(r'Chúng Tôi Nhận Thiết Kế Nội Thất Ngành Mộc', content_html)
            and re.search(r'0946\s*272\s*286', content_html)
            and re.search(r'526/2', content_html)
        )
        has_custom_extra = bool(re.search(r'happyco-footer', content_html, re.I))
        if not has_green_box:
            report["passed"] = False
            report["errors"].append("Thiếu khối viền xanh nét đứt cố định ('Chúng Tôi Nhận Thiết Kế Nội Thất Ngành Mộc... 526/2... 0946 272 286 Đức Anh') để đi liền với Banner web!")
            report["checks"]["mandatory_green_box"] = "FAIL"
        elif has_custom_extra:
            report["passed"] = False
            report["errors"].append("Phát hiện khối chân trang tự chế (happyco-footer) bị trùng lặp với khối xanh chuẩn!")
            report["checks"]["mandatory_green_box"] = "FAIL"
        else:
            report["checks"]["mandatory_green_box"] = "PASS (Đủ khối xanh nét đứt chuẩn đi liền Banner)"

        # Cấm địa chỉ cũ sai lệch
        has_wrong_address = bool(re.search(r'0947\.888\.306|chiêu\s*liêu|dĩ\s*an', content_html, re.I))
        if has_wrong_address:
            report["passed"] = False
            report["errors"].append("Phát hiện chèn địa chỉ cũ sai lệch (Dĩ An, Chiêu Liêu)!")
            report["checks"]["no_wrong_address"] = "FAIL"
        else:
            report["checks"]["no_wrong_address"] = "PASS"

        # 3. Kiểm tra ĐỘ MỚI & CHỐNG LẶP TIÊU ĐỀ
        is_fresh, fresh_msg = check_title_freshness(title, article.get("category", ""))
        if not is_fresh:
            report["passed"] = False
            report["errors"].append(f"Tiêu đề bị lặp/sáo rỗng: {fresh_msg}")
            report["checks"]["title_freshness"] = f"FAIL ({fresh_msg})"
        else:
            report["checks"]["title_freshness"] = "PASS (Tiêu đề mới hoàn toàn, chuẩn SEO 45-65 ký tự)"

        # 3b. Kiểm tra TỪ KHÓA CHUẨN SEO (2-3 cụm từ, tổng dưới 70 ký tự)
        kw = article.get("keywords", "")
        kw_ok, kw_msg = check_keywords_seo(kw)
        if not kw_ok:
            report["passed"] = False
            report["errors"].append(f"Từ khóa chưa chuẩn SEO: {kw_msg}")
            report["checks"]["keywords_seo"] = f"FAIL ({kw_msg})"
        else:
            report["checks"]["keywords_seo"] = "PASS (2-3 cụm từ ngắn gọn)"

        # 4. Kiểm tra số lượng mục Heading <h2>
        h2_count = content_html.lower().count("<h2")
        report["checks"]["h2_count"] = h2_count
        if h2_count < 3:
            report["warnings"].append(f"Bài viết chỉ có {h2_count} mục <h2>. Khuyến nghị chuẩn 4 mục <h2> chuyên sâu.")

        # 5. Kiểm tra liên kết nội bộ (Internal Links: tối thiểu 2 link)
        internal_links = re.findall(r'href=[\'"]https?://happyco\.asia[^\'"]*[\'"]', content_html)
        report["checks"]["internal_links_count"] = len(internal_links)
        if len(internal_links) < 2:
            report["warnings"].append(f"Chỉ có {len(internal_links)} liên kết nội bộ. Chuẩn SEO yêu cầu 2-3 links.")

        # 6. Kiểm tra chú thích ảnh (CẤM ghi 'Hình 1, Hình 2...')
        has_numbered_captions = bool(re.search(r'hình\s*[0-9]+', full_text))
        if has_numbered_captions:
            report["passed"] = False
            report["errors"].append("Phát hiện chú thích có chữ 'Hình 1, Hình 2,...' - Cấm theo quy chuẩn thẩm mỹ.")
            report["checks"]["clean_captions"] = "FAIL"
        else:
            report["checks"]["clean_captions"] = "PASS"

        # 7. Kiểm tra chuẩn văn phong Web
        desc = article.get("description", "").strip()
        if re.search(r'^(?:bài viết|bài viết này|bài viết chia sẻ)', desc, re.I):
            report["passed"] = False
            report["errors"].append("Mô tả bài viết (description) vi phạm: Bắt đầu bằng 'Bài viết...' - Viết web phải tóm tắt trực diện giải pháp!")
            report["checks"]["clean_description"] = "FAIL"
        else:
            report["checks"]["clean_description"] = "PASS"

        banned_fb_phrases = [
            "chào anh em", "xin chào anh em", "chào các bạn", "anh em thợ mộc",
            "với tư cách", "tôi là giám đốc", "tôi là kiến trúc sư",
            "chúng tôi là đội ngũ kỹ sư", "chúng tôi là kỹ sư trưởng"
        ]
        found_fb = [p for p in banned_fb_phrases if p in full_text]
        if found_fb:
            report["passed"] = False
            report["errors"].append(f"Vi phạm văn phong Web: Phát hiện chào hỏi/xưng danh cá nhân kiểu Facebook ({found_fb})!")
            report["checks"]["professional_web_tone"] = "FAIL"
        else:
            report["checks"]["professional_web_tone"] = "PASS"

        # 8. Kiểm tra trùng lặp ảnh
        if image_files:
            hashes = set()
            for f in image_files:
                try:
                    with open(f, "rb") as fp:
                        h = hashlib.md5(fp.read()).hexdigest()
                    if h in hashes:
                        report["passed"] = False
                        report["errors"].append(f"Ảnh {f} bị trùng mã hash trong cùng bài viết!")
                    hashes.add(h)
                except Exception:
                    pass

        return report
