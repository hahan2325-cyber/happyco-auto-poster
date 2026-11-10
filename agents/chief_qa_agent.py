"""
Chief QA Agent - Tổng Biên Tập Kiểm Duyệt Chất Lượng Xuất Bản Happyco
Kiểm duyệt nghiêm ngặt 6 tiêu chuẩn cốt lõi trước khi xuất bản
"""

import re
import hashlib
from typing import Dict, Any, List

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

        full_text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content_html', '')}".lower()

        # 1. Kiểm tra thương hiệu cấm (100% chỉ tôn vinh thương hiệu Happyco)
        found_banned = [b for b in BANNED_BRANDS if b in full_text]
        if found_banned:
            report["passed"] = False
            report["errors"].append(f"Vi phạm thương hiệu: Tìm thấy đối thủ/nhà phân phối ({found_banned}). Phải dùng từ ngữ kỹ thuật chung!")
            report["checks"]["no_banned_brands"] = "FAIL"
        else:
            report["checks"]["no_banned_brands"] = "PASS"

        # 2. Kiểm tra ô thông tin hệ thống cố định (BẮT BUỘC PHẢI CÓ 526/2 LONG BÌNH & 0946 272 286 ĐỨC ANH)
        content_html = article.get("content_html", "")
        has_mandatory_footer = bool(re.search(r'0946\s*272\s*286', content_html) and re.search(r'long\s*bình', content_html, re.I))
        if not has_mandatory_footer:
            report["passed"] = False
            report["errors"].append("Thiếu ô thông tin cố định bắt buộc của hệ thống (526/2 Long Bình, Hotline 0946 272 286 Đức Anh).")
            report["checks"]["mandatory_footer"] = "FAIL"
        else:
            report["checks"]["mandatory_footer"] = "PASS (Đầy đủ ô hệ thống cố định xưởng Long Bình & Hotline 0946 272 286)"

        # Cấm chèn số điện thoại lạ hoặc địa chỉ cũ sai lệch (Dĩ An / Chiêu Liêu)
        has_wrong_address = bool(re.search(r'0947\.888\.306|chiêu\s*liêu|dĩ\s*an', content_html, re.I))
        if has_wrong_address:
            report["passed"] = False
            report["errors"].append("Phát hiện chèn địa chỉ cũ sai lệch (Dĩ An, Chiêu Liêu). Phải là 526/2 Long Bình Đồng Nai!")
            report["checks"]["no_wrong_address"] = "FAIL"
        else:
            report["checks"]["no_wrong_address"] = "PASS"

        # 3. Kiểm tra số lượng mục Heading <h2> và ảnh minh họa
        h2_count = content_html.lower().count("<h2")
        report["checks"]["h2_count"] = h2_count
        if h2_count < 3:
            report["warnings"].append(f"Bài viết chỉ có {h2_count} mục <h2>. Khuyến nghị chuẩn 4 mục <h2> chuyên sâu.")

        # 4. Kiểm tra liên kết nội bộ (Internal Links: tối thiểu 2 link)
        internal_links = re.findall(r'href=[\'"]https?://happyco\.asia[^\'"]*[\'"]', content_html)
        report["checks"]["internal_links_count"] = len(internal_links)
        if len(internal_links) < 2:
            report["warnings"].append(f"Chỉ có {len(internal_links)} liên kết nội bộ. Chuẩn SEO yêu cầu 2-3 links.")

        # 5. Kiểm tra chú thích ảnh (CẤM ghi 'Hình 1, Hình 2...')
        has_numbered_captions = bool(re.search(r'hình\s*[0-9]+', full_text))
        if has_numbered_captions:
            report["passed"] = False
            report["errors"].append("Phát hiện chú thích có chữ 'Hình 1, Hình 2,...' - Cấm theo quy chuẩn thẩm mỹ.")
            report["checks"]["clean_captions"] = "FAIL"
        else:
            report["checks"]["clean_captions"] = "PASS"

        # 6. Kiểm tra tính khớp nối nội dung và hình ảnh (Visual Logic)
        category = article.get("category", "").upper()
        if "GIA CÔNG" in category:
            # Bài B2B: cấm ảnh phòng khách hoặc TV lạc quẻ
            if "tivi" in article.get("title", "").lower() and "phòng khách" in article.get("title", "").lower():
                report["warnings"].append("Tiêu đề mang hơi hướng phòng khách nhưng danh mục là Gia công ván.")

        # 7. Kiểm tra trùng lặp ảnh nếu có danh sách file
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
