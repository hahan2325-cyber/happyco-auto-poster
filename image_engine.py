"""
Bộ máy tạo ảnh AI độc bản 16:9 chuyên nghiệp cho Happyco
Đảm bảo 100% không trùng lặp hash (MD5 + dHash), tự động gắn Watermark Duo Happyco
"""

import os
import sys
import time
import random
import hashlib
import requests
from pathlib import Path
from PIL import Image

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
        print(f"  [ImageEngine] Không tìm thấy watermark tại {WATERMARK_PATH}, bỏ qua bước gắn logo.")
        return

    im = Image.open(image_path).convert("RGBA")
    wm = Image.open(WATERMARK_PATH).convert("RGBA")

    # Resize watermark proportionally to ~22% of image width
    wm_w = int(im.width * 0.22)
    wm_h = int(wm.height * (wm_w / wm.width))
    wm_resized = wm.resize((wm_w, wm_h), Image.Resampling.LANCZOS)

    # Position at top-left with padding (35px)
    padding = 35
    im.paste(wm_resized, (padding, padding), wm_resized)

    # Save back to RGB JPEG
    rgb_im = im.convert("RGB")
    rgb_im.save(image_path, "JPEG", quality=92, optimize=True)

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

def generate_single_image(prompt: str, out_path: Path, max_retries: int = 3) -> bool:
    # Append high quality parameters
    clean_prompt = prompt.strip()
    if "16:9" not in clean_prompt:
        clean_prompt += ", 16:9 widescreen, photorealistic architectural photograph, 8k resolution"

    for attempt in range(1, max_retries + 1):
        seed = random.randint(100000, 9999999)
        # 1. Try Pollinations AI (fast, 1280x720 16:9, highly reliable on cloud)
        encoded_prompt = requests.utils.quote(clean_prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&seed={seed}&nologo=true&model=flux"
        
        try:
            r = requests.get(pollinations_url, timeout=35)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                apply_watermark(out_path)
                return True
        except Exception as e:
            print(f"  [ImageEngine] Lần thử {attempt} qua Pollinations gặp lỗi: {e}")

        # 2. Fallback to standard pollinations endpoint
        try:
            fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&seed={seed}&nologo=true"
            r = requests.get(fallback_url, timeout=35)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                apply_watermark(out_path)
                return True
        except Exception as e:
            print(f"  [ImageEngine] Lần thử {attempt} qua fallback gặp lỗi: {e}")

        time.sleep(2)

    return False

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

        print(f"  [ImageEngine] ({idx+1}/5) Đang tạo ảnh cho '{key}'...")
        success = False

        for roll in range(4): # Re-roll up to 4 times if hash collision occurs
            ok = generate_single_image(prompt, out_file)
            if not ok:
                continue

            md5, dhash = calculate_hashes(out_file)
            if md5 in seen_md5s or (dhash and dhash in seen_dhashes):
                print(f"  [ImageEngine] Phát hiện ảnh trùng lặp ({md5[:8]}), đang tạo lại ảnh mới...")
                continue

            seen_md5s.add(md5)
            if dhash:
                seen_dhashes.add(dhash)
            generated_files[key] = out_file
            print(f"    -> Đã tạo xong: {out_file.name} (MD5: {md5[:8]}..., Size: {out_file.stat().st_size:,} bytes)")
            success = True
            break

        if not success:
            raise RuntimeError(f"Failed to generate unique image for {key} after multiple attempts.")

    print(f"  [ImageEngine] Hoàn thành 5/5 ảnh độc bản với 0 duplicate hashes!")
    return generated_files
