import json
import tempfile
from tinydb import TinyDB, Query
import pyaudio
import wave
import speech_recognition as sr
import subprocess
from gtts import gTTS
import os
import datetime
import threading
import sys
import logging
import spacy
from prompt_toolkit import Application, HTML
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import TextArea, Button, Frame
from prompt_toolkit.application import get_app
from prompt_toolkit.filters import Condition
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import PyPDF2
import re

print(f"Current working directory: {os.getcwd()}")

# Set up logging
logging.basicConfig(filename='mini_rag.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize TinyDB
db = TinyDB('documents.json')

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Check if NLTK data is downloaded, if not, download it
import nltk

def download_nltk_data():
    resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"Downloading {resource}...")
            nltk.download(resource, quiet=True)

# Call this function at the start of your script
download_nltk_data()

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('tokenizers/punkt_tab/english.json')
except LookupError:
    print("Downloading necessary NLTK data...")
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    print("NLTK data downloaded successfully!")

#Simple RAG chatbot
class SimpleRAGChatbot:
    def __init__(self, db):
        self.db = db
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'farewell': ['bye', 'goodbye', 'see you'],
            'search': ['find', 'search', 'look for'],
            'add': ['add', 'create', 'new'],
            'delete': ['delete', 'remove', 'erase'],
            'list': ['list', 'show', 'display'],
            'help': ['help', 'assist', 'support']
        }

    def preprocess(self, text):
        try:
            tokens = word_tokenize(text.lower())
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalnum()]
            tokens = [token for token in tokens if token not in self.stop_words]
            return tokens
        except Exception as e:
            logging.error(f"Error in preprocessing: {str(e)}")
            return []

    def classify_intent(self, tokens):
        try:
            intent_scores = Counter()
            for intent, keywords in self.intents.items():
                intent_scores[intent] = sum(token in keywords for token in tokens)
            return intent_scores.most_common(1)[0][0] if intent_scores else 'unknown'
        except Exception as e:
            logging.error(f"Error in intent classification: {str(e)}")
            return 'unknown'

    def generate_response(self, intent, tokens):
        try:
            if intent == 'greeting':
                return "Hello! How can I assist you with the document management system?"
            elif intent == 'farewell':
                return "Goodbye! Feel free to return if you need any more assistance."
            elif intent == 'search':
                keywords = [token for token in tokens if token not in self.intents['search']]
                if keywords:
                    return f"Certainly! I'll search for documents containing: {', '.join(keywords)}"
                else:
                    return "What would you like me to search for?"
            elif intent == 'add':
                return "Sure, I can help you add a new document. What content would you like to add?"
            elif intent == 'delete':
                return "I can help you delete a document. Please provide more details about which document you want to remove."
            elif intent == 'list':
                return "I'd be happy to list the documents for you. Here's what we have:"
            elif intent == 'help':
                return "I can help you with various tasks like searching, adding, deleting, and listing documents. What would you like to do?"
            else:
                return "I'm not sure I understand. Could you please rephrase your request?"
        except Exception as e:
            logging.error(f"Error in response generation: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request. Could you try again?"

    def get_relevant_docs(self, tokens, limit=3):
        try:
            relevant_docs = []
            for doc in self.db.all():
                doc_tokens = self.preprocess(doc['content'])
                relevance = sum(token in doc_tokens for token in tokens)
                if relevance > 0:
                    relevant_docs.append((doc, relevance))
            relevant_docs.sort(key=lambda x: x[1], reverse=True)
            return [doc for doc, _ in relevant_docs[:limit]]
        except Exception as e:
            logging.error(f"Error in retrieving relevant documents: {str(e)}")
            return []

    def process_input(self, user_input):
        try:
            tokens = self.preprocess(user_input)
            intent = self.classify_intent(tokens)
            response = self.generate_response(intent, tokens)

            if intent in ['search', 'list']:
                relevant_docs = self.get_relevant_docs(tokens)
                if relevant_docs:
                    response += "\nHere are some relevant documents:\n"
                    for doc in relevant_docs:
                        response += f"- {doc['content'][:50]}...\n"
                else:
                    response += "\nI couldn't find any relevant documents."

            return response
        except Exception as e:
            logging.error(f"Error in processing input: {str(e)}")
            return "I apologize, but I encountered an error while processing your request. Could you please try again?"

# Function to ensure all required NLTK data is downloaded
def download_nltk_data():
    resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"Downloading {resource}...")
            nltk.download(resource, quiet=True)

# Call this function at the start of your script
download_nltk_data()

# Text-to-speech function using gTTS
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        os.system(f"mpg321 {fp.name}")  # You might need to install mpg321
    os.unlink(fp.name)
    
#Record audio
def record_audio(filename, duration=5):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print(f"Recording for {duration} seconds...")
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
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

        return True, "Audio recorded successfully."
    except Exception as e:
        logging.error(f"Error in audio recording: {str(e)}")
        return False, str(e)

def text_input_alternative():
    print("Audio recording failed. Please enter your message as text:")
    return input("Your message: ")

# STT
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

# Validiate File_PATH
def get_absolute_path(file_path):
    """Convert a relative path to an absolute path."""
    return os.path.abspath(os.path.expanduser(file_path))

#validate pdf
def is_valid_pdf(file_path):
    """Check if the given file path is a valid PDF file."""
    return os.path.isfile(file_path) and file_path.lower().endswith('.pdf')

def read_latex_pdf(file_path):
    """Read and process a LaTeX-generated PDF file."""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Clean up common LaTeX artifacts
            text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remove LaTeX commands
            text = re.sub(r'\{|\}', '', text)  # Remove curly braces
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            
            return text.strip()
    except Exception as e:
        logging.error(f"Error reading PDF file '{file_path}': {str(e)}")
        raise

# Function to add a document to the database
def add_document(content, category='default'):
    try:
        db.insert({
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'category': category,
            'file_type': 'pdf' if content.startswith('PDF content:') else 'text'
        })
        print("Document added successfully.")
    except Exception as e:
        logging.error(f"Error adding document: {str(e)}")
        print(f"An error occurred while adding the document. Please check the log file.")

# Function to select a document from a list with advanced features
def select_document(documents, title):
    selected_index = [0]
    page = [0]
    items_per_page = 10
    search_query = ['']
    sort_by = ['timestamp']
    sort_order = ['desc']
    exit_flag = [False]

    def get_formatted_text():
        result = []
        result.append(('bold', f"{title}\n\n"))
        
        filtered_docs = [doc for doc in documents if search_query[0].lower() in doc['content'].lower()]
        filtered_docs.sort(key=lambda x: x[sort_by[0]], reverse=(sort_order[0] == 'desc'))
        
        start = page[0] * items_per_page
        end = start + items_per_page
        current_page_docs = filtered_docs[start:end]
        
        for i, doc in enumerate(current_page_docs, start=start):
            if i == selected_index[0]:
                result.append(('reverse', f"> {doc['timestamp']}: {doc['content'][:50]}... [{doc.get('category', 'N/A')}]\n"))
            else:
                category_color = {
                    'default': '',
                    'important': '#ansired',
                    'personal': '#ansigreen',
                    'work': '#ansiblue'
                }.get(doc.get('category', 'default'), '')
                result.append((category_color, f"  {doc['timestamp']}: {doc['content'][:50]}... [{doc.get('category', 'N/A')}]\n"))
        
        result.append(('', f"\nPage {page[0] + 1}/{(len(filtered_docs) - 1) // items_per_page + 1}"))
        result.append(('', "\nPress 'q' to return to main menu"))
        return result

    def update_search(text):
        search_query[0] = text
        page[0] = 0
        selected_index[0] = 0

    search_field = TextArea(
        height=1,
        prompt='Search: ',
        multiline=False,
        wrap_lines=False,
        accept_handler=update_search
    )

    kb = KeyBindings()

    @kb.add('up')
    def _(event):
        selected_index[0] = (selected_index[0] - 1) % len(documents)

    @kb.add('down')
    def _(event):
        selected_index[0] = (selected_index[0] + 1) % len(documents)

    @kb.add('pageup')
    def _(event):
        page[0] = max(0, page[0] - 1)

    @kb.add('pagedown')
    def _(event):
        page[0] = min((len(documents) - 1) // items_per_page, page[0] + 1)

    @kb.add('enter')
    def _(event):
        event.app.exit()

    @kb.add('q')
    def _(event):
        exit_flag[0] = True
        event.app.exit()

    @kb.add('c-d')
    def _(event):
        if 0 <= selected_index[0] < len(documents):
            db.remove(doc_ids=[documents[selected_index[0]].doc_id])
            documents.pop(selected_index[0])
            selected_index[0] = min(selected_index[0], len(documents) - 1)

    @kb.add('c-e')
    def _(event):
        if 0 <= selected_index[0] < len(documents):
            doc = documents[selected_index[0]]
            new_content = input(f"Edit document content (current: {doc['content']}): ")
            if new_content:
                doc['content'] = new_content
                db.update({'content': new_content}, doc_ids=[doc.doc_id])

    @kb.add('c-s')
    def _(event):
        nonlocal sort_by, sort_order
        sort_options = ['timestamp', 'content', 'category']
        current_index = sort_options.index(sort_by[0])
        sort_by[0] = sort_options[(current_index + 1) % len(sort_options)]
        if sort_by[0] != sort_options[current_index]:
            sort_order[0] = 'desc'
        else:
            sort_order[0] = 'asc' if sort_order[0] == 'desc' else 'desc'

    root_container = HSplit([
        search_field,
        Window(content=FormattedTextControl(get_formatted_text)),
    ])

    layout = Layout(root_container)

    application = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=True
    )

    application.run()
    
    if exit_flag[0]:
        return None
    return documents[selected_index[0]]

# Chatbot function
def chatbot_mode(db):
    chatbot = SimpleRAGChatbot(db)
    print("Entering chatbot mode. Say 'exit' to return to the main menu.")
    print("You can type your messages or say 'voice input' to speak.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'voice input':
            print("Listening... Speak now.")
            user_input = speech_to_text()
            if user_input is None:
                print("Sorry, I didn't catch that. Please try again.")
                continue
            print(f"You said: {user_input}")
        
        if user_input.lower() == 'exit':
            print("Exiting chatbot mode.")
            break
        
        response = chatbot.process_input(user_input)
        print("Chatbot:", response)
        text_to_speech(response)

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

# Function to search for documents
def search_documents(keyword):
    try:
        query = Query()
        results = db.search(query.content.search(keyword))
        if results:
            selected_doc = select_document(results, f"Search Results for '{keyword}'")
            if selected_doc:
                print("\nSelected document:")
                print(f"Timestamp: {selected_doc['timestamp']}")
                print(f"Content: {selected_doc['content']}")
            else:
                print("Returned to main menu.")
        else:
            print(f"No documents found containing '{keyword}'.")
    except Exception as e:
        logging.error(f"Error searching documents: {str(e)}")
        print(f"An error occurred while searching documents. Please check the log file.")

# Function to list all documents
def list_all_documents():
    try:
        documents = db.all()
        if documents:
            selected_doc = select_document(documents, "All Documents")
            if selected_doc:
                print("\nSelected document:")
                print(f"Timestamp: {selected_doc['timestamp']}")
                print(f"Content: {selected_doc['content']}")
            else:
                print("Returned to main menu.")
        else:
            print("No documents found.")
    except Exception as e:
        logging.error(f"Error listing documents: {str(e)}")
        print(f"An error occurred while listing documents. Please check the log file.")

# Function to record audio
def record_audio(filename, duration=5):
    CHUNK = 256
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print(f"Recording for {duration} seconds...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
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

# Function to play audio
def play_audio(filename):
    if os.path.exists(filename):
        subprocess.run(["ffplay", "-nodisp", "-autoexit", filename], check=True)
    else:
        print(f"File {filename} not found.")

def text_input_alternative():
    print("Audio recording failed. Please enter your message as text:")
    return input("Your message: ")

# Function to list all audio files
def list_audio_files():
    return [f for f in os.listdir() if f.endswith('.wav')]

# Function to delete a document
def delete_document():
    try:
        documents = db.all()
        if not documents:
            print("No documents found.")
            return

        selected_doc = select_document(documents, "Select Document to Delete")
        if selected_doc:
            confirm = input(f"Are you sure you want to delete this document? (y/n)\nContent: {selected_doc['content'][:50]}...\n")
            if confirm.lower() == 'y':
                db.remove(doc_ids=[selected_doc.doc_id])
                print("Document deleted successfully.")
            else:
                print("Deletion cancelled.")
        else:
            print("Returned to main menu.")
    except Exception as e:
        logging.error(f"Error deleting document: {str(e)}")
        print(f"An error occurred while deleting the document. Please check the log file.")

# Function to delete an audio file
def delete_audio():
    try:
        audio_files = list_audio_files()
        if not audio_files:
            print("No audio files found.")
            return

        print("Select an audio file to delete:")
        for i, file in enumerate(audio_files):
            print(f"{i+1}. {file}")
        
        choice = input("Enter the number of the file to delete (or 'q' to cancel): ")
        if choice.lower() == 'q':
            print("Deletion cancelled.")
            return

        try:
            file_index = int(choice) - 1
            if 0 <= file_index < len(audio_files):
                file_to_delete = audio_files[file_index]
                confirm = input(f"Are you sure you want to delete {file_to_delete}? (y/n): ")
                if confirm.lower() == 'y':
                    os.remove(file_to_delete)
                    print(f"{file_to_delete} deleted successfully.")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid file number.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    except Exception as e:
        logging.error(f"Error deleting audio file: {str(e)}")
        print(f"An error occurred while deleting the audio file. Please check the log file.")

# Function to perform NLP tasks
def perform_nlp_tasks(text):
    doc = nlp(text)
    
    print("\nNLP Analysis:")
    print("1. Named Entities:")
    for ent in doc.ents:
        print(f"   - {ent.text} ({ent.label_})")
    
    print("\n2. Part-of-Speech Tagging:")
    for token in doc[:10]:  # Limit to first 10 tokens for brevity
        print(f"   - {token.text}: {token.pos_}")
    
    print("\n3. Dependency Parsing:")
    for token in doc[:10]:  # Limit to first 10 tokens for brevity
        print(f"   - {token.text} --> {token.dep_}")
    
    print("\n4. Noun Chunks:")
    for chunk in doc.noun_chunks:
        print(f"   - {chunk.text}")

# Function for NLP mode
def nlp_mode():
    while True:
        print("\nNLP Mode:")
        print("1. Analyze a document")
        print("2. Analyze custom text")
        print("3. Return to main menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            documents = db.all()
            if documents:
                selected_doc = select_document(documents, "Select Document for NLP Analysis")
                if selected_doc:
                    perform_nlp_tasks(selected_doc['content'])
                else:
                    print("Returned to NLP menu.")
            else:
                print("No documents found.")
        elif choice == '2':
            text = input("Enter the text you want to analyze: ")
            perform_nlp_tasks(text)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp.mp3")
    os.system("mpg321 temp.mp3")  # You might need to install mpg321: sudo apt-get install mpg321
    os.remove("temp.mp3")

def listen_continuous():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... (Say 'stop listening' to end)")
        while True:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                text = r.recognize_google(audio)
                print(f"You said: {text}")
                if "stop listening" in text.lower():
                    print("Stopping listening mode.")
                    break
                response = f"I heard you say: {text}"
                speak(response)
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
            except Exception as e:
                print(f"Error: {str(e)}")
                break

def speech_interaction_mode():
    recognizer = sr.Recognizer()
    
    print("Speech Interaction Mode")
    print("Speak 'exit' to return to the main menu")
    
    while True:
        with sr.Microphone() as source:
            print("Listening... Speak now.")
            audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            
            if text.lower() == 'exit':
                print("Exiting speech interaction mode.")
                break
            
            response = f"I heard you say: {text}"
            print("System response:", response)
            speak(response)
        
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Could you please repeat?")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

# Main RAG function
def rag_process():
    while True:
        try:
            print("\n1. Add text document")
            print("2. Add PDF document")
            print("3. Search documents")
            print("4. List all documents")
            print("5. Record and transcribe audio")
            print("6. Play audio")
            print("7. List all audio files")
            print("8. Delete document")
            print("9. Delete audio file")
            print("10. NLP mode")
            print("11. Speech interaction mode")
            print("12. Chatbot mode")
            print("13. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                content = input("Enter document content: ")
                category = input("Enter category (default/important/personal/work): ")
                if category not in ['important', 'personal', 'work']:
                    category = 'default'
                add_document(content, category)
            # In your rag_process() function, replace the PDF handling part with this:
            elif choice == '2':
                file_path = input("Enter the path to the PDF file: ")
                abs_path = get_absolute_path(file_path)
                
                print(f"Checking file: {abs_path}")  # Debug print
                
                if not os.path.exists(abs_path):
                    print(f"Error: The file '{abs_path}' does not exist.")
                elif not is_valid_pdf(abs_path):
                    print(f"Error: The file '{abs_path}' is not a valid PDF file.")
                else:
                    try:
                        pdf_content = read_latex_pdf(abs_path)
                        category = input("Enter category (default/important/personal/work): ")
                        if category not in ['important', 'personal', 'work']:
                            category = 'default'
                        add_document(pdf_content, category)
                        print(f"PDF document '{abs_path}' processed and added successfully.")
                    except Exception as e:
                        print(f"Error processing the PDF file: {str(e)}")
                        logging.error(f"Error processing PDF file '{abs_path}': {str(e)}")
            elif choice == '3':
                keyword = input("Enter search keyword: ")
                search_documents(keyword)
            elif choice == '4':
                list_all_documents()
            elif choice == '5':
                filename = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                duration = int(input("Enter recording duration in seconds: "))
                success, message = record_audio(filename, duration)
                if success:
                    text = transcribe_audio(filename)
                    print(f"Transcribed text: {text}")
                    add_document(text, 'audio_transcript')
                    print("Transcribed text added to database.")
                else:
                    print(f"Error recording audio: {message}")
                    text = text_input_alternative()
                    add_document(text, 'manual_input')
                    print("Manually entered text added to database.")
            elif choice == '6':
                audio_files = list_audio_files()
                if audio_files:
                    print("Available audio files:")
                    for i, file in enumerate(audio_files):
                        print(f"{i+1}. {file}")
                    file_number = int(input("Enter the number of the file to play: "))
                    if 1 <= file_number <= len(audio_files):
                        play_audio(audio_files[file_number-1])
                    else:
                        print("Invalid file number.")
                else:
                    print("No audio files found.")
            elif choice == '7':
                audio_files = list_audio_files()
                if audio_files:
                    print("Available audio files:")
                    for file in audio_files:
                        print(file)
                else:
                    print("No audio files found.")
            elif choice == '8':
                delete_document()
            elif choice == '9':
                delete_audio()
            elif choice == '10':
                nlp_mode()
            elif choice == '11':
                speech_interaction_mode()
            elif choice == '12':
                chatbot_mode(db)
            elif choice == '13':
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {str(e)}")
            print(f"An unexpected error occurred. Please check the log file.")

if __name__ == "__main__":
    try:
        rag_process()
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        print(f"A critical error occurred. Please check the log file.")