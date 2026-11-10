"""
Sổ đăng ký ảnh Happyco (Image Registry) - CHỐT CHẶN CHỐNG DÙNG LẠI ẢNH.
Mọi ảnh đưa vào bài viết BẮT BUỘC phải qua check_new() trước khi dùng và register() sau khi dùng.
So khớp bằng perceptual hash (dHash) nên ảnh đã crop nhẹ/đóng watermark/đổi tên vẫn bị phát hiện.

CLI:
  python image_registry.py seed            # nạp toàn bộ ảnh đã dùng trước đây
  python image_registry.py check <file>... # kiểm tra ảnh có trùng ảnh cũ không
  python image_registry.py register <post_id> <file>...
  python image_registry.py list
  python image_registry.py sheet <folder> <out.jpg> [start] [count]  # contact sheet để chọn ảnh trong kho D:
"""
import glob
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
REGISTRY_FILE = BASE_DIR / "image_registry.json"
BRAIN_DIR = Path(r"C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64")
WORKSHOP_PHOTO_DIR = Path(r"D:\Hình\Hình xưởng\Ảnh")
HAMMING_LIMIT = 10  # <=10/256 bit khác nhau => coi là cùng một ảnh


def dhash(path, size=16):
    im = Image.open(path).convert("L")
    # bỏ vùng góc trên-trái (nơi đóng logo kép) để watermark không làm lệch hash
    w, h = im.size
    im = im.crop((int(w * 0.28), 0, w, h)) if w > 400 else im
    im = im.resize((size + 1, size), Image.Resampling.LANCZOS)
    px = list(im.getdata())
    bits = 0
    for r in range(size):
        for c in range(size):
            bits = (bits << 1) | (1 if px[r * (size + 1) + c] > px[r * (size + 1) + c + 1] else 0)
    return bits


def _load():
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    return {"images": []}


def _save(data):
    REGISTRY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def _dist(a, b):
    return bin(a ^ b).count("1")


def find_duplicate(path, data=None):
    data = data or _load()
    h = dhash(path)
    best = None
    for it in data["images"]:
        d = _dist(h, int(it["hash"], 16))
        if d <= HAMMING_LIMIT and (best is None or d < best[0]):
            best = (d, it)
    return best


def check_new(path):
    """True nếu ảnh CHƯA từng dùng. Gọi trước khi đưa ảnh vào bài."""
    dup = find_duplicate(path)
    if dup:
        print(f"  ❌ TRÙNG ẢNH CŨ: {os.path.basename(path)} ~ {dup[1]['file']} (post {dup[1]['post']}, d={dup[0]})")
        return False
    print(f"  ✅ ẢNH MỚI: {os.path.basename(path)}")
    return True


def register(post_id, path, source="ai"):
    data = _load()
    data["images"].append({"file": os.path.basename(path), "post": str(post_id),
                           "hash": format(dhash(path), "x"), "source": source})
    _save(data)


def seed():
    data = {"images": []}
    pats = [str(BRAIN_DIR / "*.jpg")] + [str(BASE_DIR / d / "*.jpg") for d in
            ["blog_images", "blog_images_b2b", "blog_images_bedroom", "blog_images_11h",
             "blog_images_17h", "b2b_art1_images", "b2b_art2_images"]]
    seen = set()
    for pat in pats:
        for p in glob.glob(pat):
            try:
                h = format(dhash(p), "x")
            except Exception:
                continue
            if h in seen:
                continue
            seen.add(h)
            data["images"].append({"file": os.path.basename(p), "post": "legacy", "hash": h, "source": "legacy"})
    _save(data)
    print(f"Đã nạp {len(data['images'])} ảnh cũ vào sổ đăng ký.")


def sheet(folder, out, start=0, count=40):
    files = sorted(f for f in glob.glob(os.path.join(folder, "**", "*.*"), recursive=True)
                   if f.lower().endswith((".jpg", ".jpeg", ".png")))[int(start):int(start) + int(count)]
    cols, tw, th = 8, 240, 180
    rows = (len(files) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tw, rows * (th + 16)), "white")
    d = ImageDraw.Draw(canvas)
    for i, f in enumerate(files):
        try:
            im = Image.open(f).convert("RGB")
            im.thumbnail((tw, th))
            x, y = (i % cols) * tw, (i // cols) * (th + 16)
            canvas.paste(im, (x, y))
            d.text((x + 2, y + th + 2), f"{int(start) + i}", fill="black")
        except Exception:
            pass
    canvas.save(out, quality=85)
    with open(out + ".txt", "w", encoding="utf-8") as fh:
        for i, f in enumerate(files):
            fh.write(f"{int(start) + i}\t{f}\n")
    print(f"Contact sheet: {out} ({len(files)} ảnh), bảng tên file: {out}.txt")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "seed":
        seed()
    elif cmd == "check":
        sys.exit(0 if all([check_new(p) for p in sys.argv[2:]]) else 1)
    elif cmd == "register":
        for p in sys.argv[3:]:
            register(sys.argv[2], p)
        print("Đã đăng ký.")
    elif cmd == "list":
        for it in _load()["images"]:
            print(it["post"], it["source"], it["file"])
    elif cmd == "sheet":
        sheet(*sys.argv[2:])
    else:
        print(__doc__)
