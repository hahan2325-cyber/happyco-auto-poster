# 🌟 Happyco Autonomous Cloud Poster 24/7

Hệ thống AI tự động hóa toàn diện quy trình sáng tạo nội dung và xuất bản bài viết lên website [happyco.asia](https://happyco.asia) vận hành liên tục 24/24 trên đám mây **GitHub Actions**.

---

## 🎯 Điểm Nổi Bật

1. **Chuẩn SEO Chuyên Sâu**:
   - Tự động tạo bài viết chuyên sâu cho 3 nhóm đối tượng: **Chủ nhà, Vợ chồng trẻ, Kiến trúc sư**.
   - Cấu trúc 4 mục `<h2>` chặt chẽ, tối ưu thẻ Meta, từ khóa và liên kết nội bộ (internal link).
   - **Tuyệt đối tuân thủ khối hệ thống**: Không chèn sai lệch hoặc can thiệp vào các khối chữ ký/chân trang cố định của website.

2. **5 Ảnh Độc Bản 16:9 Không Trùng Lặp**:
   - Tự động sinh đúng **5 bức ảnh tỷ lệ 16:9 widescreen** (1 Thumbnail + 4 ảnh minh họa cho 4 mục `<h2>`).
   - Kiểm tra mã băm quang học **MD5 & dHash** đảm bảo **100% không trùng lặp**.
   - Tự động đóng dấu bản quyền logo **Happyco Duo Watermark** sắc nét.

3. **Vận Hành 24/24 Không Cần Bật Máy Tính**:
   - Toàn bộ quy trình chạy trên đám mây GitHub Actions.
   - Bạn có thể ra lệnh cho hệ thống viết bài ngay trên **điện thoại di động**.

---

## 📱 Hướng Dẫn Sử Dụng Trên Điện Thoại & Máy Tính

### 👉 Cách 1: Ra lệnh qua GitHub Issue (Nhanh & Tiện nhất trên điện thoại)
1. Mở ứng dụng GitHub trên điện thoại hoặc vào link: [Tạo Yêu Cầu Mới](https://github.com/hahan2325-cyber/happyco-auto-poster/issues/new)
2. Nhập **Tiêu đề bài viết** vào ô `Title` (Ví dụ: `Thiết kế phòng ngủ master tân cổ điển cho vợ chồng trẻ`).
3. Bấm **Submit new issue**.
4. 🤖 **Hệ thống AI sẽ tự động kích hoạt:**
   - Tự viết bài, tự sinh 5 ảnh độc bản, tải lên CDN và đăng trực tiếp lên Happyco CMS.
   - Khi hoàn thành, Bot sẽ tự động **bình luận link bài viết và mã ID bài viết** vào ngay Issue đó rồi tự đóng Issue lại!

---

### 👉 Cách 2: Bấm nút Run Workflow thủ công
1. Vào tab **Actions**: [Chạy Workflow](https://github.com/hahan2325-cyber/happyco-auto-poster/actions/workflows/auto_post.yml)
2. Bấm vào nút **Run workflow**.
3. Điền các tùy chọn:
   - **Chủ đề bài viết**: Nhập chủ đề bạn muốn (hoặc để trống để AI tự động chọn chủ đề xu hướng hot nhất).
   - **Chuyên mục**: Chọn `BLOG NỘI THẤT`, `GIA CÔNG VÁN CÔNG NGHIỆP`, `THIẾT KẾ THI CÔNG NỘI THẤT`...
   - **Trạng thái**: Chọn `publish` (xuất bản ngay) hoặc `draft` (lưu nháp).
4. Bấm nút xanh **Run workflow**.

---

### 👉 Cách 3: Lịch Chạy Tự Động Hàng Ngày (Auto Cron 24/24)
Hệ thống đã được thiết lập sẵn lịch tự động đăng 2 bài mỗi ngày:
- ⏰ **11:00 Trưa (Giờ Việt Nam)**: Tự động chọn 1 chủ đề thịnh hành và xuất bản.
- ⏰ **17:00 Chiều (Giờ Việt Nam)**: Tự động xuất bản bài thứ 2 trong ngày.

---

## 🔒 Bảo Mật & Thông Tin Quản Trị
Toàn bộ thông tin tài khoản quản trị (`CMS_EMAIL`, `CMS_PASSWORD`), khóa `GEMINI_API_KEY` và `HF_TOKEN` đã được mã hóa an toàn 100% trong **GitHub Secrets** của kho lưu trữ này.

- Quản trị bài viết: [https://happyco.asia/admin/post](https://happyco.asia/admin/post)
- Thư viện media: [https://happyco.asia/admin/media](https://happyco.asia/admin/media)
