# backend/audio_utils.py
import os
import io
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import numpy as np
from typing import Optional

class AudioHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_dir = "audio"
        os.makedirs(self.audio_dir, exist_ok=True)
    
    def text_to_speech(self, text: str, filename: str = None) -> str:
        """Convert text to speech using gTTS"""
        if filename is None:
            filename = f"response_{int(time.time())}.mp3"
        
        filepath = os.path.join(self.audio_dir, filename)
        
        try:
            # Use gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filepath)
            return filepath
        except Exception as e:
            print(f"Error in TTS: {e}")
            return None
    
    def play_audio(self, filepath: str):
        """Play audio file"""
        try:
            audio = AudioSegment.from_mp3(filepath)
            play(audio)
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def speech_to_text(self, audio_data: bytes = None, use_mic: bool = True) -> str:
        """Convert speech to text"""
        try:
            if use_mic:
                # Use microphone
                with sr.Microphone() as source:
                    print("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=5)
            else:
                # Use provided audio data
                audio = sr.AudioData(audio_data, 16000, 2)
            
            # Recognize using Google
            text = self.recognizer.recognize_google(audio)
            return text
            
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand that."
        except sr.RequestError as e:
            return f"Could not request results: {e}"
        except Exception as e:
            return f"Error in speech recognition: {e}"
    
    def record_audio_duration(self, duration: int = 5, sample_rate: int = 16000) -> bytes:
        """Record audio using sounddevice (works on macOS)"""
        print(f"Recording for {duration} seconds...")
        
        try:
            # Record audio
            audio_data = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()  # Wait until recording is finished
            
            # Convert to bytes
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, sample_rate, format='WAV')
            buffer.seek(44)  # Skip WAV header
            
            return buffer.read()
            
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

# Global instance
audio_handler = AudioHandler()