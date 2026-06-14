import cv2
import os
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

class VideoService:
    def __init__(self):
        """Initialize video service"""
        pass
    
    def get_video_info(self, video_path):
        """
        Lấy thông tin video
        
        Args:
            video_path: đường dẫn file video
        
        Returns:
            dict: thông tin video
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise Exception(f"Cannot open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'duration': duration,
                'fps': fps,
                'width': width,
                'height': height,
                'total_frames': total_frames
            }
        
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def merge_audio_to_video(self, video_path, audio_results, output_path):
        """
        Ghép âm thanh vào video
        
        Args:
            video_path: đường dẫn video gốc
            audio_results: List[dict] chứa audio_file, timestamp
            output_path: đường dẫn file video đầu ra
        
        Returns:
            str: đường dẫn file video đã xử lý
        """
        try:
            video_clip = VideoFileClip(video_path)
            audio_clips = []
            
            for audio_result in audio_results:
                audio_file = audio_result['audio_file']
                timestamp = audio_result['timestamp']
                
                if os.path.exists(audio_file):
                    audio = AudioFileClip(audio_file)
                    audio = audio.set_start(timestamp)
                    audio_clips.append(audio)
            
            if not audio_clips:
                video_clip.write_videofile(output_path, verbose=False, logger=None)
                video_clip.close()
                return output_path
            
            final_audio = CompositeAudioClip(audio_clips)
            final_video = video_clip.set_audio(final_audio)
            
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            final_video.close()
            video_clip.close()
            final_audio.close()
            
            for audio_result in audio_results:
                audio_file = audio_result['audio_file']
                if os.path.exists(audio_file):
                    try:
                        os.remove(audio_file)
                    except:
                        pass
            
            return output_path
        
        except Exception as e:
            print(f"Error merging audio to video: {e}")
            raise