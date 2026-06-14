from google.cloud import translate_v2
import os
from dotenv import load_dotenv

load_dotenv()

class TranslationService:
    def __init__(self):
        """Initialize translation service"""
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        try:
            self.client = translate_v2.Client()
        except Exception as e:
            print(f"Warning: Google Cloud not configured. Error: {e}")
            self.client = None
    
    def translate(self, text, source_lang='zh', target_lang='vi'):
        """
        Dịch văn bản
        
        Args:
            text: văn bản cần dịch
            source_lang: 'zh'
            target_lang: 'vi' hoặc 'th'
        
        Returns:
            str: văn bản đã dịch
        """
        if not text or not text.strip():
            return ""
        
        try:
            if self.client:
                result = self.client.translate_text(
                    text,
                    source_language=source_lang,
                    target_language=target_lang
                )
                return result['translatedText']
            else:
                return text
        
        except Exception as e:
            print(f"Translation error: {e}")
            return text