# Trang chấm slide SlideGen

Đang chạy tại https://slidegen-annotation.vercel.app (Vercel project `slidegen-annotation`, Postgres Neon đã kết nối, `ANNOTATOR_CODES` và `ADMIN_TOKEN` đã đặt; mã đợt 2 nằm trong `slidegen_data/annotation/round2/credentials.json`, không push).

Đợt 2 (tập test `testset_v2`, prompt vòng 4) dùng cùng giao thức và cùng bảng `ratings`; mã cặp có tiền tố `r2-`, ảnh ở thư mục `img2/` của dataset ảnh, bảng ánh xạ ở `slidegen_data/annotation/round2/secret_mapping.json`. Dựng lại bằng `python scripts/build_annotation_set.py --round 2 --upload`.

Trang web tĩnh + 3 API serverless trên Vercel để người chấm so sánh cặp slide (chấm mù). Kết quả lưu trong Postgres (Neon). Ảnh slide được tải từ một dataset Hugging Face, tên file là mã ngẫu nhiên nên không lộ hệ thống tạo ra slide.

## Cấu trúc

| Đường dẫn | Vai trò |
|---|---|
| `public/index.html`, `public/app.js`, `public/style.css` | Giao diện: đăng nhập bằng mã, hướng dẫn, màn hình chấm |
| `public/data/pairs.json` | Danh sách cặp: văn bản nguồn + tên ảnh A/B (sinh bởi `scripts/build_annotation_set.py`) |
| `public/data/assignments.json` | Hàng đợi cặp đã xáo trộn của từng người chấm (`A1`, `A2`, `A3`) |
| `api/session.js` | Kiểm tra mã người chấm, trả về các cặp đã chấm để tiếp tục đúng chỗ |
| `api/submit.js` | Lưu (hoặc sửa) câu trả lời một cặp |
| `api/export.js` | Xuất toàn bộ kết quả, cần header `x-admin-token` |

Bảng ánh xạ "cặp → hệ thống, vị trí trái/phải" **không nằm trong thư mục này**; nó được lưu riêng ở `slidegen_data/annotation/secret_mapping.json` (không deploy, không push công khai) để giải mã kết quả.

## Deploy lên Vercel

1. Vercel dashboard → **Add New → Project** → import repo GitHub, chọn **Root Directory = `annotation_web`**. Framework: *Other*. Không cần build command.
2. Project → **Storage → Create Database → Neon (Postgres)** → Connect vào project. Vercel tự thêm biến `DATABASE_URL`/`POSTGRES_URL`.
3. Project → **Settings → Environment Variables**, thêm:
   - `ANNOTATOR_CODES` = `maBiMat1:A1,maBiMat2:A2,maBiMat3:A3` (mã bí mật gửi riêng cho từng người chấm).
   - `ADMIN_TOKEN` = một chuỗi ngẫu nhiên dài, chỉ người quản lý giữ.
4. **Deploy**. Bảng `ratings` được tạo tự động ở lần gọi API đầu tiên.

Có thể deploy bằng CLI thay cho bước 1 và 4: `npx vercel --cwd annotation_web deploy --prod --yes --token $VERCEL_TOKEN`.

## Hướng dẫn cho người chấm

1. Mở đường link trang chấm, nhập **mã người chấm** được gửi riêng.
2. Đọc kỹ trang **Hướng dẫn** (luôn mở lại được bằng nút *Hướng dẫn* góc trên).
3. Với mỗi cặp: đọc văn bản nguồn → xem hai slide (nhấp vào ảnh để phóng to) → chọn A / Ngang nhau / B cho cả 6 tiêu chí → đánh dấu lỗi nghiêm trọng nếu có → **Lưu và tiếp tục**.
4. Phím tắt: `1` = A tốt hơn, `2` = Ngang nhau, `3` = B tốt hơn cho tiêu chí đang tô sáng; `Enter` để lưu.
5. Có thể dừng bất cứ lúc nào; lần sau mở lại trang sẽ tiếp tục đúng cặp chưa chấm. Nút *Cặp trước* cho phép sửa câu trả lời đã lưu.
6. Nên chấm thành nhiều buổi, mỗi buổi không quá khoảng 45 phút để tránh mệt.

## Lấy kết quả

```bash
curl -s -H "x-admin-token: $ADMIN_TOKEN" https://<ten-project>.vercel.app/api/export > ratings.json
python scripts/analyze_annotations.py ratings.json slidegen_data/annotation/secret_mapping.json
# đợt 2:
python scripts/analyze_annotations.py ratings.json slidegen_data/annotation/round2/secret_mapping.json --out slidegen_data/annotation/round2/report
```

## Chạy thử cục bộ

Không cần Vercel: `scripts/` có server giả lập API dùng cho kiểm thử giao diện bằng Playwright (đăng nhập sai/đúng, chấm thiếu tiêu chí, quay lại cặp trước, tải lại trang giữa chừng, hoàn thành).
