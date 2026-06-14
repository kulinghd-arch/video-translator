import cv2
from paddleocr import PaddleOCR
import os

class OCRService:
    def __init__(self):
        """Initialize OCR services"""
        self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        
    def extract_text_from_video(self, video_path, sample_rate=1):
        """
        Trích xuất văn bản từ video
        
        Args:
            video_path: đường dẫn file video
            sample_rate: lấy mẫu mỗi N frame
        
        Returns:
            List[dict] chứa text, timestamp
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise Exception(f"Cannot open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        results = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            if frame_count % sample_rate != 0:
                frame_count += 1
                continue
            
            timestamp = frame_count / fps
            ocr_text = self._ocr_frame(frame)
            
            if ocr_text.strip():
                results.append({
                    'frame': frame_count,
                    'timestamp': timestamp,
                    'text': ocr_text,
                    'confidence': 0.8
                })
            
            frame_count += 1
        
        cap.release()
        return results
    
    def _ocr_frame(self, frame):
        """Nhận dạng văn bản trong 1 frame"""
        try:
            result = self.paddle_ocr.ocr(frame, cls=True)
            
            if not result or not result[0]:
                return ""
            
            texts = []
            for line in result:
                if line:
                    for item in line:
                        text = item[1]
                        texts.append(text)
            
            return ' '.join(texts)
        
        except Exception as e:
            print(f"OCR error: {e}")
            return ""