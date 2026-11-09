"""
Happyco Autonomous Cloud Poster - CLI Entrypoint
Tự động sinh bài viết SEO, tạo 5 ảnh độc bản 16:9 gắn logo, và đăng lên Happyco CMS
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

from generator import generate_article
from image_engine import generate_5_unique_images
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
    requests.post(url, headers=headers, json={"body": comment_text})

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
    requests.patch(url, headers=headers, json={"state": "closed"})

def main():
    parser = argparse.ArgumentParser(description="Happyco Autonomous Cloud Poster")
    parser.add_argument("--topic", type=str, default="", help="Chủ đề bài viết muốn đăng")
    parser.add_argument("--category", type=str, default="BLOG NỘI THẤT", help="Chuyên mục bài viết")
    parser.add_argument("--publish-mode", type=str, default="publish", choices=["publish", "draft"], help="Trạng thái đăng")
    parser.add_argument("--issue-number", type=int, default=0, help="GitHub Issue Number nếu trigger từ Issue")
    args = parser.parse_args()

    topic = args.topic.strip()
    category = args.category.strip()
    publish_mode = args.publish_mode.strip()
    issue_num = args.issue_number

    print("==================================================================")
    print("🚀 KHỞI ĐỘNG HỆ THỐNG HAPPYCO AUTONOMOUS CLOUD POSTER")
    print(f"📌 Chủ đề: {topic if topic else '(Tự động chọn chủ đề xu hướng)'}")
    print(f"📂 Chuyên mục: {category}")
    print(f"⚙️ Chế độ: {publish_mode}")
    print("==================================================================")

    # 1. Sinh bài viết
    print("\n[Bước 1/3] Đang gọi Gemini AI sinh bài viết chuẩn SEO...")
    article = generate_article(topic_title=topic if topic else None, category=category)
    print(f"  ✅ Tiêu đề: {article['title']}")
    print(f"  ✅ Mô tả (sapo): {article['description']}")
    print(f"  ✅ Thẻ tags: {article.get('tags', '')}")

    # 2. Sinh 5 ảnh độc bản
    print("\n[Bước 2/3] Đang sinh 5 ảnh độc bản 16:9 gắn Duo Watermark...")
    output_dir = BASE_DIR / "output" / "images"
    image_files = generate_5_unique_images(article.get("image_prompts", []), output_dir)

    # 3. Đăng bài lên CMS
    print("\n[Bước 3/3] Đang tải ảnh lên CDN và xuất bản bài viết vào CMS...")
    result = publish_post(article, image_files, publish_mode=publish_mode, artifacts_dir=BASE_DIR / "output")

    post_info = result.get("post_info", {})
    post_id = post_info.get("id", "N/A")
    post_title = post_info.get("title", article["title"])

    print("\n==================================================================")
    print(f"🎉 BÀI VIẾT ĐÃ ĐƯỢC XUẤT BẢN THÀNH CÔNG LÊN HAPPYCO.ASIA!")
    print(f"🆔 Post ID: {post_id}")
    print(f"📝 Tiêu đề: {post_title}")
    print(f"🌐 Quản trị: https://happyco.asia/admin/post")
    print("==================================================================")

    # Nếu trigger từ GitHub Issue: phản hồi và đóng issue
    if issue_num > 0:
        comment_md = f"""### ✅ Bài viết đã được tự động đăng thành công lên Happyco.asia!

- **Tiêu đề**: **{post_title}**
- **Mã bài viết (CMS ID)**: `{post_id}`
- **Chuyên mục**: `{category}`
- **Số lượng ảnh độc quyền**: 5/5 ảnh (16:9 widescreen, đã gắn logo Happyco Duo)
- **Trạng thái**: Đã xuất bản ({publish_mode})
- **Xem trong trang quản trị**: [Happyco Admin Posts](https://happyco.asia/admin/post)
"""
        post_github_issue_comment(issue_num, comment_md)
        close_github_issue(issue_num)
        print(f"  [GitHub Issue #{issue_num}] Đã gửi phản hồi và đóng Issue tự động!")

if __name__ == "__main__":
    main()
