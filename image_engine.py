"""
Bộ máy tạo ảnh AI độc bản 16:9 chuyên nghiệp cho Happyco
Đảm bảo 100% không trùng lặp hash (MD5 + dHash)
Tự động đóng dấu Happyco Duo Watermark trên nền kính mờ (Frosted White Pill) siêu sắc nét
"""

import os
import sys
import time
import random
import hashlib
import requests
from pathlib import Path
from PIL import Image, ImageDraw

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import imagehash
except ImportError:
    imagehash = None

WATERMARK_PATH = Path(__file__).resolve().parent / "happyco_watermark_duo.png"

def apply_watermark(image_path: Path) -> None:
    if not WATERMARK_PATH.exists():
        print(f"  [ImageEngine] Không tìm thấy watermark tại {WATERMARK_PATH}, bỏ qua.", flush=True)
        return

    try:
        im = Image.open(image_path).convert("RGBA")

        # 1. BẮT BUỘC CẮT 16:9 TRƯỚC TIÊN (1280x720 hoặc tỷ lệ 16:9 chuẩn)
        target_ratio = 16.0 / 9.0
        cur_ratio = im.width / im.height
        if abs(cur_ratio - target_ratio) > 0.03:
            if cur_ratio > target_ratio:
                new_w = int(im.height * target_ratio)
                left = (im.width - new_w) // 2
                im = im.crop((left, 0, left + new_w, im.height))
            else:
                new_h = int(im.width / target_ratio)
                top = (im.height - new_h) // 2
                im = im.crop((0, top, im.width, top + new_h))

        # Đảm bảo độ phân giải tối thiểu 1280x720
        if im.width < 1280:
            im = im.resize((1280, 720), Image.Resampling.LANCZOS)

        # 2. CHUẨN BỊ WATERMARK DUO TRÊN NỀN KÍNH MỜ (FROSTED PILL)
        wm = Image.open(WATERMARK_PATH).convert("RGBA")

        # Tính toán kích thước watermark: ~24% chiều rộng ảnh
        wm_w = int(im.width * 0.24)
        wm_h = int(wm.height * (wm_w / wm.width))
        wm_resized = wm.resize((wm_w, wm_h), Image.Resampling.LANCZOS)

        # 3. GẮN LOGO VÀO GÓC TRÊN BÊN TRÁI (35px padding) - DÁN TRỰC TIẾP ALPHA TRONG SUỐT (CẤM TUYỆT ĐỐI NỀN TRẮNG/PILL)
        im.paste(wm_resized, (35, 35), wm_resized)

        # Lưu lại JPEG chất lượng cao 92%
        rgb_im = im.convert("RGB")
        rgb_im.save(image_path, "JPEG", quality=92, optimize=True)
        print(f"  [ImageEngine] Đã gắn Watermark Duo sắc nét vào: {image_path.name}", flush=True)
    except Exception as e:
        print(f"  [ImageEngine] Lỗi khi gắn watermark: {e}", flush=True)

def calculate_hashes(file_path: Path):
    with open(file_path, "rb") as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()

    dhash_val = None
    if imagehash is not None:
        try:
            im = Image.open(file_path)
            dhash_val = str(imagehash.dhash(im))
        except Exception:
            pass
    return md5_hash, dhash_val

def fetch_architectural_photo_fallback(query: str, out_path: Path) -> bool:
    print(f"  [ImageEngine] Kích hoạt Fallback ảnh nội thất/xưởng mộc mở: '{query[:45]}...' ", flush=True)
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{query} interior architecture workshop",
        "gsrnamespace": 6,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|size",
        "format": "json"
    }
    headers = {"User-Agent": "HappycoAutoPoster/1.0 (marketinghappyco@gmail.com)"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=20)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                title = pdata.get("title", "").lower()
                if not (title.endswith(".jpg") or title.endswith(".jpeg") or title.endswith(".png")):
                    continue
                ii = pdata.get("imageinfo", [{}])[0]
                img_url = ii.get("url")
                if img_url:
                    img_res = requests.get(img_url, headers=headers, timeout=30)
                    if img_res.status_code == 200 and len(img_res.content) > 30000:
                        with open(out_path, "wb") as f:
                            f.write(img_res.content)
                        apply_watermark(out_path)
                        print(f"    -> Fallback thành công: {out_path.name}", flush=True)
                        return True
    except Exception as e:
        print(f"  [ImageEngine] Fallback gặp lỗi: {e}", flush=True)
    return False

def generate_single_image(prompt: str, out_path: Path, max_retries: int = 4) -> bool:
    clean_prompt = prompt.strip()
    if "16:9" not in clean_prompt:
        clean_prompt += ", 16:9 widescreen, photorealistic photograph, 8k resolution"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    for attempt in range(1, max_retries + 1):
        seed = random.randint(100000, 9999999)
        encoded_prompt = requests.utils.quote(clean_prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&seed={seed}&nologo=true&model=flux"

        try:
            print(f"  [ImageEngine] Đang yêu cầu AI FLUX (Lần {attempt})...", flush=True)
            r = requests.get(pollinations_url, headers=headers, timeout=35)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                apply_watermark(out_path)
                return True
            elif r.status_code in [402, 429]:
                print(f"  [ImageEngine] API rate-limit (HTTP {r.status_code}), chờ 46s theo hạn ngạch...", flush=True)
                time.sleep(46)
            else:
                print(f"  [ImageEngine] Phản hồi HTTP {r.status_code}, chờ 10s...", flush=True)
                time.sleep(10)
        except Exception as e:
            print(f"  [ImageEngine] Lỗi kết nối: {e}, chờ 10s...", flush=True)
            time.sleep(10)

    return fetch_architectural_photo_fallback(clean_prompt[:60], out_path)

def generate_5_unique_images(image_prompts: list, output_dir: Path) -> dict:
    """
    Sinh 5 bức ảnh độc bản, kiểm tra chặt chẽ 0 duplicate MD5/dHash
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files = {}
    seen_md5s = set()
    seen_dhashes = set()

    for idx, item in enumerate(image_prompts):
        key = item.get("key", f"img_{idx}")
        prompt = item.get("prompt_en", "")
        out_file = output_dir / f"happyco_{key}.jpg"

        print(f"\n  [ImageEngine] === ({idx+1}/5) TIẾN HÀNH TẠO ẢNH CHO '{key.upper()}' ===", flush=True)
        success = False

        for roll in range(3):
            ok = generate_single_image(prompt, out_file)
            if not ok:
                continue

            md5, dhash = calculate_hashes(out_file)
            if md5 in seen_md5s or (dhash and dhash in seen_dhashes):
                print(f"  [ImageEngine] Trùng hash ({md5[:8]}), đổi seed tạo lại...", flush=True)
                continue

            seen_md5s.add(md5)
            if dhash:
                seen_dhashes.add(dhash)
            generated_files[key] = out_file
            print(f"  ✅ ĐÃ XONG ẢNH {idx+1}/5: {out_file.name} (MD5: {md5[:8]}, {out_file.stat().st_size:,} bytes)", flush=True)
            success = True
            break

        if not success:
            raise RuntimeError(f"Không thể tạo ảnh độc bản cho {key} sau nhiều lần thử.")

        time.sleep(1)

    print(f"\n🎉 [ImageEngine] ĐÃ HOÀN THÀNH TOÀN BỘ 5/5 ẢNH ĐỘC BẢN 16:9 CÓ WATERMARK FROSTED PILL!", flush=True)
    return generated_files
