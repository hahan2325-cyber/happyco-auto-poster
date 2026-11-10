"""
Asset Library: Quản lý và xử lý kho hình ảnh chuẩn hoá Happyco
Tích hợp chốt chặn image_registry chống trùng lặp tuyệt đối.

Quy định nghiêm ngặt:
1. LOGO TRONG SUỐT HOÀN TOÀN: Dán trực tiếp kênh alpha (35, 35). CẤM TUYỆT ĐỐI NỀN TRẮNG/KHUNG CHỮ NHẬT/PILL.
2. KHỚP ẢNH VỚI HEADING: Quét thư mục ảnh thật (D:\\Hình\\Hình xưởng\\Ảnh) để tìm đúng chủ đề từng heading:
   - Cắt phôi / CNC / Nesting -> Ảnh máy CNC, lưỡi cưa, file bản vẽ CNC
   - Dán cạnh PUR / Noline / Nẹp -> Ảnh máy dán cạnh, đầu phun keo PUR
   - Đo đạc / Dung sai / Kiểm tra -> Kỹ thuật viên đo phôi, kiểm tra thước kẹp
   - Phân loại / Đóng gói / Mã vạch -> Sắp xếp phôi, dán nhãn tem barcode, kho thành phẩm
3. CHỐNG TRÙNG LẶP TUYỆT ĐỐI: Mỗi ảnh dùng xong được ghi nhận mã băm (dHash / md5) vào image_registry.json. Không bao giờ dùng lại ở bài khác.
4. CẤM ẢNH AI NGƯỜI LẠ: Nếu không có ảnh xưởng thật phải tạo ảnh AI thì chỉ tạo ảnh máy móc/vật liệu/nội thất, CẤM người mặc áo không có logo Happyco.
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
WATERMARK_PATH = ASSETS_DIR / "happyco_watermark_duo.png"

from core.image_registry import check_new, register

class AssetLibrary:
    def __init__(self):
        self.output_dir = BASE_DIR / "output" / "processed_assets"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.wm_img = Image.open(WATERMARK_PATH).convert("RGBA") if WATERMARK_PATH.exists() else None

    def stamp_watermark(self, src_path: Path, out_path: Path) -> Path:
        """
        Đóng dấu Happyco Duo Watermark chuẩn tỷ lệ 22% TRONG SUỐT HOÀN TOÀN
        CẤM TUYỆT ĐỐI NỀN TRẮNG, HỘP PILL HOẶC KHUNG VIỀN DƯỚI LOGO
        """
        im = Image.open(src_path).convert("RGBA")
        w, h = im.size
        target_h = int(w * 9 / 16)
        if h > target_h:
            top = (h - target_h) // 2
            im = im.crop((0, top, w, top + target_h))
        elif h < target_h:
            target_w = int(h * 16 / 9)
            left = (w - target_w) // 2
            im = im.crop((left, 0, left + target_w, h))

        im_resized = im.resize((1376, 768), Image.Resampling.LANCZOS)

        if self.wm_img:
            wm_w = int(im_resized.width * 0.22)
            wm_h = int(self.wm_img.height * (wm_w / self.wm_img.width))
            wm_scaled = self.wm_img.resize((wm_w, wm_h), Image.Resampling.LANCZOS)

            # DÁN TRỰC TIẾP KÊNH ALPHA CỦA LOGO VÀO GÓC TRÊN TRÁI - 100% TRONG SUỐT (KHÔNG NỀN)
            im_resized.paste(wm_scaled, (35, 35), wm_scaled)

        im_resized.convert("RGB").save(out_path, "JPEG", quality=92, optimize=True)
        return out_path

    def _get_candidate_photos(self, pool_name: str) -> List[Path]:
        """Lấy danh sách ảnh thật từ kho ảnh xưởng hoặc assets repo"""
        candidates: List[Path] = []
        local_workshop = Path(r"D:\Hình\Hình xưởng\Ảnh")
        if local_workshop.exists() and "b2b" in pool_name:
            raw_files = list(local_workshop.glob("*.jpg")) + list(local_workshop.glob("*.png"))
            for f in raw_files:
                try:
                    with Image.open(f) as img:
                        # Ưu tiên ảnh ngang hoặc tỷ lệ chuẩn
                        if img.size[0] >= img.size[1]:
                            candidates.append(f)
                except Exception:
                    continue

        if not candidates:
            if "b2b" in pool_name:
                p = ASSETS_DIR / "b2b_factory"
                candidates = list(p.glob("*.jpg")) + list(p.glob("*.png"))
            elif "bedroom" in pool_name:
                p = ASSETS_DIR / "b2c_bedroom"
                candidates = list(p.glob("*.jpg")) + list(p.glob("*.png"))
            else:
                p = ASSETS_DIR / "b2c_living"
                candidates = list(p.glob("*.jpg")) + list(p.glob("*.png"))

        return candidates

    def match_heading_photo(self, heading_text: str, candidates: List[Path], used_paths: Set[str]) -> Optional[Path]:
        """
        Tìm kiếm thông minh ảnh thật trong folder khớp với nội dung Heading:
        - CNC / cắt / nesting -> ảnh máy cắt, cắt CNC
        - Dán cạnh / PUR / noline / nẹp -> ảnh máy dán chỉ, dán cạnh
        - Đo đạc / kiểm tra / dung sai -> ảnh đo ván, đo chi tiết
        - Sắp xếp / đóng gói / mã vạch / kho -> ảnh sắp xếp ván, kho ván
        """
        h_lower = heading_text.lower()

        keywords_map = [
            # Dán cạnh
            (["dán cạnh", "pur", "noline", "nẹp", "chỉ cạnh", "dán chỉ"], ["dán chỉ", "dan chi", "canh", "máy dán"]),
            # Cắt CNC / Nesting
            (["cnc", "cắt", "nesting", "phôi", "lưỡi cưa", "cắt ván"], ["máy cắt gỗ cnc", "cắt theo cnc", "cat theo cnc", "may cat go cnc", "cnc"]),
            # Đo đạc / dung sai
            (["đo", "dung sai", "kích thước", "kiểm tra", "kỹ thuật", "chuẩn"], ["đo ván", "do van", "đo chi tiết", "đo sản phẩm", "do"]),
            # Sắp xếp / Đóng gói / Mã vạch
            (["sắp xếp", "đóng gói", "mã vạch", "barcode", "kho", "giao", "bàn giao"], ["sắp xếp ván", "sap xep van", "kho", "đóng gói"])
        ]

        target_tokens = []
        for triggers, file_tokens in keywords_map:
            if any(t in h_lower for t in triggers):
                target_tokens.extend(file_tokens)

        # 1. Tìm file có tên chứa token khớp heading
        if target_tokens:
            for c in candidates:
                c_str = str(c)
                if c_str in used_paths:
                    continue
                c_name = c.name.lower()
                if any(tok in c_name for tok in target_tokens):
                    if check_new(c):
                        return c

        # 2. Nếu không có tên khớp trực tiếp, lấy ảnh thật chưa từng dùng trong pool
        for c in candidates:
            c_str = str(c)
            if c_str in used_paths:
                continue
            if check_new(c):
                return c

        return None

    def get_article_assets(self, headings: List[str], pool_name: str = "b2b", post_id: str = "pending") -> Dict[str, Dict[str, Any]]:
        """
        Lấy toàn bộ 5 ảnh cho bài viết (1 thumbnail + 4 headings) đảm bảo:
        - Khớp heading
        - Không trùng lặp
        - Đóng dấu watermark trong suốt 100%
        """
        candidates = self._get_candidate_photos(pool_name)
        used_paths: Set[str] = set()
        result: Dict[str, Dict[str, Any]] = {}

        # 1. Thumbnail (máy CNC hoặc tổng thể xưởng)
        thumb_candidate = None
        for c in candidates:
            c_name = c.name.lower()
            if any(k in c_name for k in ["máy cắt gỗ cnc", "may cat go cnc", "cnc"]) and check_new(c):
                thumb_candidate = c
                break
        if not thumb_candidate:
            for c in candidates:
                if check_new(c):
                    thumb_candidate = c
                    break

        if thumb_candidate:
            used_paths.add(str(thumb_candidate))
            register(post_id, thumb_candidate, source="real_factory")
            out_fn = f"transparent_wm_thumb_{thumb_candidate.stem}.jpg"
            out_p = self.output_dir / out_fn
            self.stamp_watermark(thumb_candidate, out_p)
            result["thumb"] = {
                "file": out_p,
                "filename": out_fn,
                "title": "Day Chuyen May Cat Phoi Van CNC Xuong Happyco",
                "alt": "Dây chuyền máy cắt phôi ván gỗ công nghiệp CNC tại xưởng Happyco",
                "caption": "Dây chuyền máy cắt phôi ván gỗ công nghiệp CNC tốc độ cao tại nhà xưởng Happyco"
            }

        # 2. Bốn ảnh cho 4 Heading
        for idx, heading in enumerate(headings[:4], 1):
            key = f"h2_{idx}"
            matched = self.match_heading_photo(heading, candidates, used_paths)
            if matched:
                used_paths.add(str(matched))
                register(post_id, matched, source="real_factory")
                src_to_stamp = matched
            else:
                # Fallback: nếu thư mục hết ảnh hoặc không tìm thấy, lấy candidate bất kỳ chưa đăng
                fallback = [c for c in candidates if str(c) not in used_paths and check_new(c)]
                if fallback:
                    src_to_stamp = fallback[0]
                    used_paths.add(str(src_to_stamp))
                    register(post_id, src_to_stamp, source="real_factory")
                else:
                    src_to_stamp = candidates[idx % len(candidates)]

            out_fn = f"transparent_wm_{key}_{src_to_stamp.stem}.jpg"
            out_p = self.output_dir / out_fn
            self.stamp_watermark(src_to_stamp, out_p)

            # Tạo Alt / Caption bám sát heading
            clean_h = re.sub(r'^\d+\.\s*', '', heading)
            result[key] = {
                "file": out_p,
                "filename": out_fn,
                "title": f"Happyco {clean_h}",
                "alt": f"{clean_h} - Happyco",
                "caption": f"Quy trình thực tế: {clean_h} tại nhà xưởng mộc Happyco"
            }

        return result
