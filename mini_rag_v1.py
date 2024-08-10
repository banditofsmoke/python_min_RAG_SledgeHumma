import json
from tinydb import TinyDB, Query
import pyaudio
import wave
import speech_recognition as sr
import subprocess
import os
import datetime
import threading
import sys
from prompt_toolkit import Application
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

# Initialize TinyDB
db = TinyDB('documents.json')

# Function to add a document to the database
def add_document(content):
    db.insert({'content': content, 'timestamp': datetime.datetime.now().isoformat()})

# Function to search for documents
def search_documents(keyword):
    query = Query()
    return db.search(query.content.search(keyword))

# Function to list all documents
def list_all_documents():
    documents = db.all()
    print(f"Total documents: {len(documents)}")
    for doc in documents:
        timestamp = doc.get('timestamp', 'No timestamp')
        print(f"{timestamp}: {doc['content']}")

# Global variable to control recording
recording = True

# Function to handle user input to stop recording
def input_thread():
    global recording
    input("Press Enter to stop recording...")
    recording = False

# Function to record audio
def record_audio(max_duration=60, filename=None):
    global recording
    if filename is None:
        filename = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print(f"Recording... Press Enter to stop (max {max_duration} seconds)")
    frames = []
    recording = True

    # Start the input thread
    threading.Thread(target=input_thread, daemon=True).start()

    for _ in range(0, int(RATE / CHUNK * max_duration)):
        if not recording:
            break
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

# Function to transcribe audio
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

# Function to list all audio files
def list_audio_files():
    return [f for f in os.listdir() if f.endswith('.wav')]

# Function to play audio using ffplay with scrollable selection
def play_audio():
    audio_files = list_audio_files()
    if not audio_files:
        print("No audio files found.")
        return

    selected_index = [0]  # Use a list to make it mutable inside the closure

    def get_formatted_text():
        result = []
        for i, file in enumerate(audio_files):
            if i == selected_index[0]:
                result.append(('reverse', f'> {file}\n'))
            else:
                result.append(('', f'  {file}\n'))
        return result

    kb = KeyBindings()

    @kb.add('up')
    def _(event):
        selected_index[0] = (selected_index[0] - 1) % len(audio_files)

    @kb.add('down')
    def _(event):
        selected_index[0] = (selected_index[0] + 1) % len(audio_files)

    @kb.add('enter')
    def _(event):
        event.app.exit()

    application = Application(
        layout=Layout(Window(FormattedTextControl(get_formatted_text))),
        key_bindings=kb,
        full_screen=True
    )

    application.run()

    selected_file = audio_files[selected_index[0]]
    ffplay_path = "/usr/bin/ffplay"  # or the path returned by 'which ffplay'
    subprocess.run([ffplay_path, "-nodisp", "-autoexit", selected_file], check=True)

# Function to migrate existing documents (add timestamps)
def migrate_documents():
    documents = db.all()
    for doc in documents:
        if 'timestamp' not in doc:
            doc['timestamp'] = datetime.datetime.now().isoformat()
            db.update(doc, doc_ids=[doc.doc_id])
    print("Migration complete.")

# Main RAG function
def rag_process():
    while True:
        print("\n1. Add document")
        print("2. Search documents")
        print("3. List all documents")
        print("4. Record and transcribe audio")
        print("5. Play audio")
        print("6. List all audio files")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            content = input("Enter document content: ")
            add_document(content)
            print("Document added successfully.")
        elif choice == '2':
            keyword = input("Enter search keyword: ")
            results = search_documents(keyword)
            print(f"Found {len(results)} documents:")
            for doc in results:
                print(f"{doc['timestamp']}: {doc['content']}")
        elif choice == '3':
            list_all_documents()
        elif choice == '4':
            while True:
                try:
                    duration_input = input("Enter recording duration in seconds (max 60, press Enter for default): ")
                    if duration_input == "":
                        max_duration = 60
                    else:
                        max_duration = int(duration_input)
                    max_duration = min(60, max(1, max_duration))  # Ensure duration is between 1 and 60 seconds
                    break
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 60.")
            filename = record_audio(max_duration)
            text = transcribe_audio(filename)
            print(f"Transcribed text: {text}")
            add_document(text)
            print("Transcribed text added to database.")
        elif choice == '5':
            play_audio()
        elif choice == '6':
            audio_files = list_audio_files()
            if not audio_files:
                print("No audio files found.")
            else:
                print("Available audio files:")
                for file in audio_files:
                    print(file)
        elif choice == '7':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    # Run migration to add timestamps to existing documents
    migrate_documents()
    # Start the main RAG process
    rag_process()