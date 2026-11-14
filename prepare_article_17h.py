import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from agents.chief_qa_agent import ChiefQAAgent
from agents.b2c_interior_agent import B2CInteriorAgent

print("=== CON TỔNG ĐIỀU PHỐI B2C INTERIOR AGENT SOẠN BÀI ĐĂNG 17H ===")
b2c = B2CInteriorAgent()
topic = "Thiết Kế Tủ Bếp Cánh Kính Khung Nhôm Anode Kết Hợp Bàn Đảo Bếp Thông Minh: Đẳng Cấp Sang Trọng & Bền Bỉ Chống Nước Tuyệt Đối Từ Xưởng Happyco"
article = b2c.produce_article(topic_title=topic)

# Unique slug
ts = int(time.time())
article["slug"] = f"thiet-ke-tu-bep-canh-kinh-khung-nhom-anode-ban-dao-thong-minh-happyco-{ts}"

# Chief QA Audit
qa = ChiefQAAgent()
audit_res = qa.audit(article)
print(f"Kết quả kiểm duyệt Con Tổng: {'PASS ✅' if audit_res['passed'] else 'FAIL ❌'}")
print("Chi tiết checks:", json.dumps(audit_res["checks"], ensure_ascii=False))

if not audit_res["passed"]:
    raise ValueError(f"Audit failed: {audit_res['errors']}")

# Save article json
out_file = BASE_DIR / "output" / "article_17h.json"
out_file.parent.mkdir(parents=True, exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(article, f, ensure_ascii=False, indent=2)

print(f"Đã lưu bài viết chuẩn bị cho 17h: {out_file.name}")
