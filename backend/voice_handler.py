import os
import io
import wave
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
from gtts import gTTS
from config import config

AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def text_to_speech(text, filename="response.mp3"):
    """Convert text to speech using gTTS"""
    filepath = os.path.join(AUDIO_DIR, filename)
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filepath)
    return filepath

def play_audio(filepath):
    """Play audio file"""
    audio = AudioSegment.from_mp3(filepath)
    play(audio)

def speech_to_text(audio_data):
    """Convert speech to text using SpeechRecognition"""
    recognizer = sr.Recognizer()
    
    try:
        # Convert bytes to AudioData
        audio = sr.AudioData(audio_data, 16000, 2)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError:
        return "Speech service unavailable."

def record_audio(duration=5):
    """Record audio from microphone"""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024)
    
    frames = []
    print("Recording...")
    for _ in range(0, int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(data)
    
    print("Recording finished")
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return b''.join(frames)