from google.cloud import texttospeech
import os
from dotenv import load_dotenv

load_dotenv()

class TTSService:
    def __init__(self):
        """Initialize Text-to-Speech service"""
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        try:
            self.client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Warning: Google Cloud TTS not configured. Error: {e}")
            self.client = None
        
        self.voices = {
            'vi': {
                'language_code': 'vi-VN',
                'name': 'vi-VN-Standard-A',
                'ssml_gender': texttospeech.SsmlVoiceGender.FEMALE
            },
            'th': {
                'language_code': 'th-TH',
                'name': 'th-TH-Standard-A',
                'ssml_gender': texttospeech.SsmlVoiceGender.FEMALE
            }
        }
    
    def text_to_speech(self, text, language='vi', output_path=None, speed=1.0):
        """
        Chuyển đổi văn bản thành giọng đọc
        
        Args:
            text: văn bản cần đọc
            language: 'vi' hoặc 'th'
            output_path: đường dẫn lưu file
            speed: tốc độ đọc
        
        Returns:
            str: đường dẫn file âm thanh
        """
        if not text or not text.strip():
            return None
        
        if not self.client:
            raise Exception("Google Cloud TTS not configured")
        
        try:
            voice_config = self.voices.get(language, self.voices['vi'])
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_config['language_code'],
                name=voice_config['name'],
                ssml_gender=voice_config['ssml_gender']
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speed
            )
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            if output_path:
                with open(output_path, 'wb') as out:
                    out.write(response.audio_content)
                return output_path
            
            return response.audio_content
        
        except Exception as e:
            print(f"TTS error: {e}")
            raise