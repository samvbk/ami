# backend/audio_simple.py
import os
import uuid
from gtts import gTTS

class AudioHandler:
    def __init__(self):
        self.audio_dir = "audio"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def text_to_speech(self, text):
        try:
            # Generate unique filename
            filename = f"{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            # Use gTTS for text-to-speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filepath)
            
            print(f"✅ Audio saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Audio generation failed: {e}")
            return None

audio_handler = AudioHandler()