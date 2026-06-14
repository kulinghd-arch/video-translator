# Video Translator - Dịch Video & Tạo Giọng Đọc

Công cụ web tự động dịch văn bản trong video từ **Tiếng Trung → Tiếng Việt/Tiếng Thái** và tạo giọng đọc chuẩn.

## 🎯 Tính Năng

- ✅ Upload video (MP4, AVI, MOV, v.v.)
- ✅ OCR nhận dạng văn bản Tiếng Trung từ video
- ✅ Dịch tự động sang Tiếng Việt hoặc Tiếng Thái
- ✅ Text-to-Speech tạo giọng đọc chuẩn
- ✅ Ghép âm thanh vào video tự động
- ✅ Tải video đã xử lý

## 🚀 Cài Đặt & Chạy

### Requirements
- Python 3.8+
- FFmpeg
- Google Cloud API Keys

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

## 📁 Cấu Trúc Dự Án

```
video-translator/
├── backend/           # Python Flask API
├── frontend/          # HTML/CSS/JavaScript
├── requirements.txt   # Python dependencies
└── README.md
```

## 📝 License
MIT