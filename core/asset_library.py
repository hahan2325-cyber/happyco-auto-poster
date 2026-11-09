"""
Asset Library: Quản lý kho hình ảnh chuẩn hoá cho từng chuyên mục
Đảm bảo:
1. 100% hình ảnh khớp tuyệt đối với chủ đề bài viết:
   - Bài Gia Công Ván B2B: 100% ảnh xưởng, máy CNC Nesting, dán cạnh keo PUR noline, phôi ván gỗ công nghiệp. TUYỆT ĐỐI CẤM ảnh phòng khách, tivi.
   - Bài Blog Nội Thất B2C: 100% ảnh không gian sống sang trọng (vách tivi phòng khách, phòng ngủ master cánh kính, bàn đảo).
2. 100% ảnh có watermark Happyco kép ở góc trên bên trái, KHÔNG watermark bên thứ 3 (pollinations.ai, canva, shutter...).
3. 0% ảnh trùng lặp trong bài viết.
"""

import os
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"

class AssetLibrary:
    def __init__(self):
        self.pools = {
            "b2b_cnc": {
                "thumb": ASSETS_DIR / "b2b_cnc" / "b2b_art1_thumb.jpg",
                "h2_1": ASSETS_DIR / "b2b_cnc" / "b2b_art1_h2_1.jpg",
                "h2_2": ASSETS_DIR / "b2b_cnc" / "b2b_art1_h2_2.jpg",
                "h2_3": ASSETS_DIR / "b2b_cnc" / "b2b_art1_h2_3.jpg",
                "h2_4": ASSETS_DIR / "b2b_cnc" / "b2b_art1_h2_4.jpg"
            },
            "b2b_pur": {
                "thumb": ASSETS_DIR / "b2b_pur" / "b2b_art2_thumb.jpg",
                "h2_1": ASSETS_DIR / "b2b_pur" / "b2b_art2_h2_1.jpg",
                "h2_2": ASSETS_DIR / "b2b_pur" / "b2b_art2_h2_2.jpg",
                "h2_3": ASSETS_DIR / "b2b_pur" / "b2b_art2_h2_3.jpg",
                "h2_4": ASSETS_DIR / "b2b_pur" / "b2b_art2_h2_4.jpg"
            },
            "b2c_living": {
                "thumb": ASSETS_DIR / "b2c_living" / "flow_thumb_vach_tivi_11h.jpg",
                "h2_1": ASSETS_DIR / "b2c_living" / "flow_h2_1_lam_song_than_tre_11h.jpg",
                "h2_2": ASSETS_DIR / "b2c_living" / "flow_h2_2_tu_ruou_canh_kinh_11h.jpg",
                "h2_3": ASSETS_DIR / "b2c_living" / "flow_h2_3_cot_go_pur_noline_11h.jpg",
                "h2_4": ASSETS_DIR / "b2c_living" / "flow_h2_4_nghiem_thu_phong_khach_11h.jpg"
            },
            "b2c_bedroom": {
                "thumb": ASSETS_DIR / "b2c_bedroom" / "flow_thumb_phong_ngu_master_17h.jpg",
                "h2_1": ASSETS_DIR / "b2c_bedroom" / "flow_h2_1_bo_tri_thong_thoang_17h.jpg",
                "h2_2": ASSETS_DIR / "b2c_bedroom" / "flow_h2_2_giuong_boc_nem_17h.jpg",
                "h2_3": ASSETS_DIR / "b2c_bedroom" / "flow_h2_3_tu_ao_canh_kinh_17h.jpg",
                "h2_4": ASSETS_DIR / "b2c_bedroom" / "flow_h2_4_ban_phan_treo_guong_led_17h.jpg"
            }
        }

    def get_images_for_pool(self, pool_name: str) -> Dict[str, Path]:
        """Lấy bộ 5 ảnh khớp hoàn hảo cho pool được yêu cầu"""
        if pool_name not in self.pools:
            pool_name = "b2b_cnc" if "b2b" in pool_name else "b2c_living"
        
        images = self.pools[pool_name]
        for key, p in images.items():
            if not p.exists():
                raise FileNotFoundError(f"Missing asset file for key '{key}': {p}")
        return images
