"""
Happyco Autonomous Cloud Poster - Multi-Agent System
Kiến trúc Đa Tác tử (Multi-Agent System) vận hành tự động trên GitHub Actions:
- Chief QA Agent (Tổng Biên Tập): Kiểm duyệt 6 tiêu chuẩn khắt khe, chặn từ khóa cấm, cấm can thiệp chân trang hệ thống.
- Sub-Agent 1 (B2B Woodworking Specialist): Chuyên mục GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265).
- Sub-Agent 2 (B2C Interior Specialist): Chuyên mục BLOG NỘI THẤT (ID: 266) cho Chủ nhà, Vợ chồng trẻ, Kiến trúc sư.
- Asset Library: 100% ảnh chuẩn phân giải cao (1376x768), khớp 100% nội dung, gắn Happyco Duo Watermark, 0 watermark bên thứ 3.
- Publisher Bot: Playwright Headless, upload CDN Full HD, thiết lập thumbnail chuẩn xác.
"""

import os
import sys
import argparse
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from agents.chief_qa_agent import ChiefQAAgent
from agents.b2b_woodworking_agent import B2BWoodworkingAgent
from agents.b2c_interior_agent import B2CInteriorAgent
from core.asset_library import AssetLibrary
from publisher import publish_post

def post_github_issue_comment(issue_number: int, comment_text: str):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo:
        return
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    try:
        requests.post(url, headers=headers, json={"body": comment_text})
    except Exception as e:
        print(f"Warning: Failed to comment on GitHub Issue #{issue_number}: {e}")

def close_github_issue(issue_number: int):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo:
        return
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    try:
        requests.patch(url, headers=headers, json={"state": "closed"})
    except Exception as e:
        print(f"Warning: Failed to close GitHub Issue #{issue_number}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Happyco Autonomous Cloud Poster - Multi-Agent System")
    parser.add_argument("--topic", type=str, default="", help="Chủ đề bài viết muốn đăng")
    parser.add_argument("--category", type=str, default="", help="Chuyên mục bài viết (GIA CÔNG VÁN CÔNG NGHIỆP hoặc BLOG NỘI THẤT)")
    parser.add_argument("--publish-mode", type=str, default="publish", choices=["publish", "draft"], help="Trạng thái đăng")
    parser.add_argument("--issue-number", type=int, default=0, help="GitHub Issue Number nếu trigger từ Issue")
    args = parser.parse_args()

    topic = args.topic.strip()
    category = args.category.strip()
    publish_mode = args.publish_mode.strip()
    issue_num = args.issue_number

    # Xác định Sub-Agent phụ trách dựa trên yêu cầu
    is_b2b = False
    if "GIA CÔNG" in category.upper() or "265" in category:
        is_b2b = True
    elif "pur" in topic.lower() or "cnc" in topic.lower() or "dán cạnh" in topic.lower() or "gia công" in topic.lower() or "tay nắm" in topic.lower() or "ván ép" in topic.lower():
        is_b2b = True

    print("==================================================================")
    print("🚀 KHỞI ĐỘNG HỆ THỐNG ĐA TÁC TỬ (MULTI-AGENT SYSTEM) HAPPYCO")
    print(f"📌 Yêu cầu chủ đề: {topic if topic else '(Tự động chọn đề tài chuyên sâu)'}")
    print(f"📂 Phân loại chuyên mục: {'GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265)' if is_b2b else 'BLOG NỘI THẤT (ID: 266)'}")
    print(f"⚙️ Chế độ xuất bản: {publish_mode}")
    print("==================================================================")

    # 1. Khởi tạo các Agent chuyên biệt
    chief_qa = ChiefQAAgent()
    asset_lib = AssetLibrary()

    # 2. Sub-Agent sản xuất nội dung
    if is_b2b:
        print("\n[Sub-Agent] Kích hoạt Sub-Agent B2B Woodworking Specialist...")
        b2b_agent = B2BWoodworkingAgent()
        article = b2b_agent.produce_article(topic_title=topic if topic else None)
    else:
        print("\n[Sub-Agent] Kích hoạt Sub-Agent B2C Interior Specialist...")
        b2c_agent = B2CInteriorAgent()
        article = b2c_agent.produce_article(topic_title=topic if topic else None)

    print(f"  ✅ Tiêu đề bài viết: {article['title']}")
    print(f"  ✅ Chuyên mục gán: {article.get('category')} (ID: {article.get('cat_id')})")
    print(f"  ✅ Sapo tóm tắt: {article.get('description', '')[:120]}...")

    # 3. Lấy 5 ảnh chuẩn từ Asset Library (100% khớp đề tài, 0% ảnh phòng khách trong bài B2B)
    pool = article.get("pool", "b2b_pur" if is_b2b else "b2c_living")
    print(f"\n[Asset Library] Truy xuất 5 hình ảnh Full HD 1376x768 từ pool '{pool}'...")
    image_files = asset_lib.get_images_for_pool(pool)
    for k, p in image_files.items():
        print(f"  + [{k}]: {p.name}")

    # 4. Tổng Biên Tập (Chief QA Agent) kiểm duyệt chất lượng gắt gao
    print("\n[Chief QA] Tổng Biên Tập thực hiện kiểm duyệt 6 tiêu chuẩn xuất bản...")
    audit_report = chief_qa.audit(article, image_files=list(image_files.values()))
    
    print(f"  + Kiểm tra đối thủ cấm: {audit_report['checks'].get('no_banned_brands')}")
    print(f"  + Kiểm tra chân trang: {audit_report['checks'].get('clean_footer')}")
    print(f"  + Số lượng Heading <h2>: {audit_report['checks'].get('h2_count')}")
    print(f"  + Số liên kết nội bộ: {audit_report['checks'].get('internal_links_count')}")
    print(f"  + Chú thích ảnh tự nhiên: {audit_report['checks'].get('clean_captions')}")

    if not audit_report["passed"]:
        print(f"❌ CHIEF QA TỪ CHỐI XUẤT BẢN: {audit_report['errors']}")
        sys.exit(1)
    print("  ✅ CHIEF QA: PHÊ DUYỆT BÀI VIẾT ĐẠT 100% CHUẨN XUẤT BẢN!")

    # 5. Publisher Bot đăng bài lên CMS
    print("\n[Publisher] Khởi động Publisher Bot đăng tải lên CMS Happyco...")
    output_dir = BASE_DIR / "output"
    result = publish_post(article, image_files, publish_mode=publish_mode, artifacts_dir=output_dir)

    post_info = result.get("post_info", {})
    post_id = post_info.get("id", "N/A")
    post_title = post_info.get("title", article["title"])

    print("\n==================================================================")
    print("🎉 BÀI VIẾT ĐÃ ĐƯỢC XUẤT BẢN THÀNH CÔNG VÀO CMS HAPPYCO!")
    print(f"🆔 Post ID: {post_id}")
    print(f"📝 Tiêu đề: {post_title}")
    print(f"🌐 Trang quản trị: https://happyco.asia/admin/post")
    print("==================================================================")

    # 6. Nếu trigger từ GitHub Issue: phản hồi và đóng issue
    if issue_num > 0:
        comment_md = f"""### ✅ Bài viết đã được tự động đăng thành công lên Happyco.asia!

- **Tiêu đề**: **{post_title}**
- **Mã bài viết (CMS ID)**: `{post_id}`
- **Chuyên mục**: `{article.get('category')} (ID: {article.get('cat_id')})`
- **Sub-Agent phụ trách**: `{b2b_agent.name if is_b2b else b2c_agent.name}`
- **Bộ ảnh minh họa**: 5/5 ảnh Full HD độc quyền từ xưởng (1376x768, gắn logo kép Happyco Duo, 0 watermark bên thứ 3)
- **Kiểm duyệt Chief QA**: 100% PASS (Không nhắc đối thủ, giữ nguyên chân trang hệ thống, 2-3 links nội bộ)
- **Trạng thái**: Đã xuất bản ({publish_mode})
- **Xem trong trang quản trị**: [Happyco Admin Posts](https://happyco.asia/admin/post)
"""
        post_github_issue_comment(issue_num, comment_md)
        close_github_issue(issue_num)
        print(f"  [GitHub Issue #{issue_num}] Đã gửi phản hồi và đóng Issue tự động!")

if __name__ == "__main__":
    main()
