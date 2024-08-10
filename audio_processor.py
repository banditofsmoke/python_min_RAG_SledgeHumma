import pyaudio
import wave
import speech_recognition as sr
import subprocess
import os
import datetime
from config import AUDIO_FORMAT, AUDIO_CHANNELS, AUDIO_RATE, AUDIO_CHUNK, AUDIO_RECORD_SECONDS

def record_audio(filename, duration=AUDIO_RECORD_SECONDS):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=AUDIO_CHANNELS, rate=AUDIO_RATE, input=True, frames_per_buffer=AUDIO_CHUNK)

    print(f"Recording for {duration} seconds...")
    frames = []
    for _ in range(0, int(AUDIO_RATE / AUDIO_CHUNK * duration)):
        data = stream.read(AUDIO_CHUNK)
        frames.append(data)
    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(AUDIO_CHANNELS)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(AUDIO_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return True, "Audio recorded successfully."

def transcribe_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results"

def play_audio(filename):
    if os.path.exists(filename):
        subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], check=True)
    else:
        print(f"File {filename} not found.")

def list_audio_files():
    return [f for f in os.listdir() if f.endswith(f'.{AUDIO_FORMAT}')]

def delete_audio(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print(f"{filename} deleted successfully.")
    else:
        print(f"File {filename} not found.")

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Speak now.")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None