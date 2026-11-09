# 🌟 Happyco Autonomous Cloud Poster 24/7 - Multi-Agent Architecture

Hệ thống AI Đa Tác Tử (Multi-Agent System) tự động hóa toàn diện quy trình sáng tạo nội dung và xuất bản bài viết lên website [happyco.asia](https://happyco.asia) vận hành liên tục 24/24 trên đám mây **GitHub Actions**.

---

## 🏛️ Kiến Trúc Đội Ngũ Tác Tử (Multi-Agent System)

1. **Tổng Biên Tập (Chief QA Agent)**:
   - Kiểm duyệt khắt khe 6 tiêu chuẩn cốt lõi trước khi cho phép xuất bản.
   - **Chặn 100% thương hiệu đối thủ**: Không nhắc An Cường, Ba Thanh, Mộc Phát... chỉ dùng thuật ngữ kỹ thuật chung và tôn vinh thương hiệu Happyco.
   - **Bảo vệ tính bất biến của chân trang**: Tuyệt đối không chèn ô địa chỉ hay hotline vào nội dung vì hệ thống website đã có sẵn 2 khối chân trang cố định.
   - **Chuẩn SEO & Thẩm mỹ**: Bắt buộc 4 mục `<h2>`, tối thiểu 2-3 liên kết nội bộ (internal links), cấm đánh số máy móc "Hình 1, Hình 2".
   - **Kiểm soát tính logic hình ảnh**: Khớp nối 100% ảnh với ngữ cảnh bài viết; 0% ảnh trùng lặp (MD5 & dHash check).

2. **Sub-Agent 1 (B2B Woodworking Specialist - Gia Công Ván B2B)**:
   - Chuyên trách chuyên mục **GIA CÔNG VÁN CÔNG NGHIỆP (ID: 265)**.
   - Phục vụ: Xưởng mộc vừa và nhỏ, anh em thợ mộc tự do, thầu thợ, kiến trúc sư dự án.
   - Nội dung: Dây chuyền CNC Nesting tối ưu phôi ván, dán cạnh keo PUR Noline siêu chống nước màng keo dưới 0.05mm, vát tay nắm chữ J/K âm cánh, khoan cam chốt tự động, dán tem mã vạch barcode từng chi tiết theo sơ đồ 3D.
   - Hình ảnh: 100% ảnh nhà xưởng thực tế, máy CNC, máy dán PUR, phôi ván. **Tuyệt đối cấm ảnh phòng khách hay tivi**.

3. **Sub-Agent 2 (B2C Interior Specialist - Blog Nội Thất)**:
   - Chuyên trách chuyên mục **BLOG NỘI THẤT (ID: 266)**.
   - Phục vụ 3 nhóm đối tượng: **Chủ nhà** (bền, phong thủy vượng tài, giá trực tiếp tại xưởng), **Vợ chồng trẻ** (thẩm mỹ hiện đại, giữ lửa hôn nhân, an toàn bo cong cho con nhỏ, ván chuẩn E1/E0), **Kiến trúc sư** (hiện thực hóa 3D, độ chính xác mộc, shadow gap, PUR noline).
   - Hình ảnh: 100% ảnh không gian sống sang trọng, vách tivi, tủ rượu cánh kính Slim, phòng ngủ master.

4. **Asset Library & Duo Watermark Pipeline**:
   - Kho ảnh chuẩn Full HD 1376x768 được phân loại theo từng cụm chủ đề (`b2b_cnc`, `b2b_pur`, `b2c_living`, `b2c_bedroom`).
   - Đóng dấu logo kép **Happyco Duo Watermark** sắc nét ở góc trên bên trái.
   - **Tuyệt đối không có watermark bên thứ 3** (pollinations.ai, canva, shutter...).

5. **Publisher Bot (Playwright Headless)**:
   - Tải ảnh lên CDN Happyco Media, lấy link Full HD gốc (loại bỏ hoàn toàn link thumb 150x150).
   - Chèn ảnh khổ lớn hiển thị đầy đủ trên mọi giao diện: `style="width: 100%; max-width: 800px; height: auto;"`.
   - Thiết lập chuẩn xác ô `#thumbnail` (chỉ lấy filename) và hiển thị ảnh đại diện 600x600 trên trang quản trị CMS.

---

## 📱 Hướng Dẫn Sử Dụng Trên Điện Thoại & Máy Tính

### 👉 Cách 1: Ra lệnh qua GitHub Issue (Nhanh & Tiện nhất trên điện thoại)
1. Mở ứng dụng GitHub trên điện thoại hoặc vào link: [Tạo Yêu Cầu Mới](https://github.com/hahan2325-cyber/happyco-auto-poster/issues/new)
2. Nhập **Tiêu đề bài viết** vào ô `Title` (Ví dụ: `Gia công dán cạnh PUR Noline và vát tay nắm J-K cánh tủ` hoặc `Thiết kế nội thất phòng ngủ master cho vợ chồng trẻ`).
3. Bấm **Submit new issue**.
4. 🤖 **Hệ thống AI sẽ tự động phân loại Sub-Agent phụ trách, sản xuất nội dung, duyệt QA, tải ảnh Full HD và đăng bài lên CMS.**
5. Khi hoàn thành, Bot sẽ tự động **bình luận mã bài viết, đường dẫn và thông tin kiểm duyệt** vào ngay Issue đó rồi tự đóng Issue lại.

---

### 👉 Cách 2: Bấm nút Run Workflow thủ công
1. Vào tab **Actions**: [Chạy Workflow](https://github.com/hahan2325-cyber/happyco-auto-poster/actions/workflows/auto_post.yml)
2. Bấm vào nút **Run workflow**.
3. Tùy chọn:
   - **Chủ đề bài viết**: Nhập chủ đề bạn muốn (hoặc để trống để AI tự động chọn chủ đề chuyên sâu).
   - **Chuyên mục**: Chọn `BLOG NỘI THẤT` (ID: 266) hoặc `GIA CÔNG VÁN CÔNG NGHIỆP` (ID: 265).
   - **Trạng thái**: Chọn `publish` (xuất bản ngay) hoặc `draft` (lưu nháp).
4. Bấm nút xanh **Run workflow**.

---

### 👉 Cách 3: Lịch Chạy Tự Động Hàng Ngày (Auto Cron 24/24)
Hệ thống đã được thiết lập sẵn lịch tự động đăng 2 bài mỗi ngày:
- ⏰ **11:00 Trưa (Giờ Việt Nam)**: Tự động chọn đề tài và xuất bản.
- ⏰ **17:00 Chiều (Giờ Việt Nam)**: Tự động xuất bản bài thứ 2 trong ngày.

---

## 🔒 Bảo Mật & Thông Tin Quản Trị
Toàn bộ thông tin tài khoản quản trị (`CMS_EMAIL`, `CMS_PASSWORD`), khóa `GEMINI_API_KEY` và `HF_TOKEN` đã được mã hóa an toàn 100% trong **GitHub Secrets** của kho lưu trữ.

- Quản trị bài viết: [https://happyco.asia/admin/post](https://happyco.asia/admin/post)
- Thư viện media: [https://happyco.asia/admin/media](https://happyco.asia/admin/media)
