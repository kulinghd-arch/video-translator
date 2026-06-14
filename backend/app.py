from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import json

from services.ocr_service import OCRService
from services.translation_service import TranslationService
from services.tts_service import TTSService
from services.video_service import VideoService

load_dotenv()

app = Flask(__name__)
CORS(app)

# Cấu hình
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Khởi tạo services
ocr_service = OCRService()
translation_service = TranslationService()
tts_service = TTSService()
video_service = VideoService()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Video Translator API is running'})

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload video file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Lấy thông tin video
        video_info = video_service.get_video_info(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'duration': video_info['duration'],
            'width': video_info['width'],
            'height': video_info['height']
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_video():
    """Process video: OCR -> Translate -> TTS -> Merge"""
    try:
        data = request.json
        filename = data.get('filename')
        target_language = data.get('target_language', 'vi')
        
        if not filename:
            return jsonify({'error': 'Filename required'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        # Bước 1: OCR
        print(f"[1] Starting OCR for {filename}...")
        ocr_results = ocr_service.extract_text_from_video(filepath)
        
        if not ocr_results:
            return jsonify({'error': 'No text detected in video'}), 400
        
        # Bước 2: Dịch
        print(f"[2] Translating to {target_language}...")
        translated_results = []
        for ocr in ocr_results:
            translated_text = translation_service.translate(
                ocr['text'], 
                source_lang='zh',
                target_lang=target_language
            )
            translated_results.append({
                **ocr,
                'translated_text': translated_text
            })
        
        # Bước 3: TTS
        print(f"[3] Generating speech...")
        audio_results = []
        for idx, result in enumerate(translated_results):
            audio_file = tts_service.text_to_speech(
                result['translated_text'],
                language=target_language,
                output_path=os.path.join(OUTPUT_FOLDER, f"audio_{idx}.mp3")
            )
            audio_results.append({
                **result,
                'audio_file': audio_file
            })
        
        # Bước 4: Merge
        print(f"[4] Merging video with audio...")
        output_filename = f"translated_{os.path.splitext(filename)[0]}.mp4"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        final_video = video_service.merge_audio_to_video(
            filepath,
            audio_results,
            output_path
        )
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'message': 'Video processing completed successfully'
        }), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_video(filename):
    """Download processed video"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    return jsonify({
        'source': 'zh',
        'targets': [
            {'code': 'vi', 'name': 'Tiếng Việt'},
            {'code': 'th', 'name': 'ไทย (Tiếng Thái)'}
        ]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)