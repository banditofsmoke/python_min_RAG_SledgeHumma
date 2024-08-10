import logging
import os
import datetime
from colorama import Fore, Back, Style, init
from tqdm import tqdm
import time
import threading

from utils import setup_logging, download_nltk_data
from document_manager import add_document, search_documents, list_all_documents, delete_document, process_pdf
from audio_processor import record_audio, transcribe_audio, play_audio, list_audio_files, delete_audio, speech_to_text
from nlp_processor import nlp_mode
from chatbot import chatbot_mode
from user_interface import select_document, display_menu
from config import AUDIO_RECORD_SECONDS, ENCRYPTION_KEY

init(autoreset=True)  # Initialize colorama

def animated_loading(duration):
    symbols = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        i = (i + 1) % len(symbols)
        print(f"\r{Fore.CYAN}Loading {symbols[i]}", end="")
        time.sleep(0.1)
    print("\r" + " " * 20 + "\r", end="")

def speech_interaction_mode(document_manager):
    print(Fore.YELLOW + "🎤 Speech Interaction Mode 🎤" + Style.RESET_ALL)
    print(Fore.CYAN + "Say 'exit' to return to the main menu" + Style.RESET_ALL)
    
    while True:
        print(Fore.GREEN + "Listening... Speak now." + Style.RESET_ALL)
        text = speech_to_text()
        if text is None:
            print(Fore.RED + "Sorry, I didn't catch that. Please try again." + Style.RESET_ALL)
            continue
        
        print(Fore.YELLOW + f"You said: {text}" + Style.RESET_ALL)
        
        if text.lower() == 'exit':
            print(Fore.CYAN + "Exiting speech interaction mode." + Style.RESET_ALL)
            break
        
        if text.lower().startswith('add document'):
            content = text[len('add document'):].strip()
            add_document(content, 'speech_input')
            print(Fore.GREEN + "Document added successfully." + Style.RESET_ALL)
        elif text.lower().startswith('search'):
            query = text[len('search'):].strip()
            results = search_documents(query)
            if results:
                print(Fore.GREEN + "Search results:" + Style.RESET_ALL)
                for doc in results[:3]:  # Show top 3 results
                    print(f"- {doc['content'][:50]}...")
            else:
                print(Fore.YELLOW + "No documents found." + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "Command not recognized. You can say 'add document [content]' or 'search [query]'." + Style.RESET_ALL)

def advanced_document_management():
    while True:
        print(Fore.CYAN + "\n📚 Advanced Document Management 📚" + Style.RESET_ALL)
        print("1. Batch import documents")
        print("2. Export documents")
        print("3. Document analytics")
        print("4. Return to main menu")
        
        choice = input(Fore.GREEN + "Enter your choice: " + Style.RESET_ALL)
        
        if choice == '1':
            batch_import_documents()
        elif choice == '2':
            export_documents()
        elif choice == '3':
            document_analytics()
        elif choice == '4':
            break
        else:
            print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)

def batch_import_documents():
    folder_path = input(Fore.YELLOW + "Enter the folder path containing documents to import: " + Style.RESET_ALL)
    if not os.path.isdir(folder_path):
        print(Fore.RED + "Invalid folder path. Please try again." + Style.RESET_ALL)
        return
    
    files = [f for f in os.listdir(folder_path) if f.endswith(('.txt', '.pdf'))]
    if not files:
        print(Fore.YELLOW + "No .txt or .pdf files found in the specified folder." + Style.RESET_ALL)
        return
    
    print(Fore.CYAN + f"Found {len(files)} files to import." + Style.RESET_ALL)
    for file in tqdm(files, desc="Importing documents", unit="file"):
        file_path = os.path.join(folder_path, file)
        if file.endswith('.pdf'):
            process_pdf(file_path, 'batch_import')
        else:
            with open(file_path, 'r') as f:
                content = f.read()
                add_document(content, 'batch_import')
    
    print(Fore.GREEN + f"Successfully imported {len(files)} documents." + Style.RESET_ALL)

def export_documents():
    documents = list_all_documents()
    if not documents:
        print(Fore.YELLOW + "No documents to export." + Style.RESET_ALL)
        return
    
    export_path = input(Fore.YELLOW + "Enter the folder path to export documents: " + Style.RESET_ALL)
    if not os.path.isdir(export_path):
        try:
            os.makedirs(export_path)
        except OSError:
            print(Fore.RED + "Failed to create export directory. Please try again." + Style.RESET_ALL)
            return
    
    for doc in tqdm(documents, desc="Exporting documents", unit="doc"):
        filename = f"doc_{doc.doc_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(os.path.join(export_path, filename), 'w') as f:
            f.write(f"Timestamp: {doc['timestamp']}\n")
            f.write(f"Category: {doc['category']}\n")
            f.write(f"Content:\n{doc['content']}")
    
    print(Fore.GREEN + f"Successfully exported {len(documents)} documents to {export_path}" + Style.RESET_ALL)

def document_analytics():
    documents = list_all_documents()
    if not documents:
        print(Fore.YELLOW + "No documents available for analysis." + Style.RESET_ALL)
        return
    
    total_docs = len(documents)
    categories = {}
    word_count = 0
    longest_doc = ''
    shortest_doc = documents[0]['content']
    
    for doc in documents:
        categories[doc['category']] = categories.get(doc['category'], 0) + 1
        words = len(doc['content'].split())
        word_count += words
        if len(doc['content']) > len(longest_doc):
            longest_doc = doc['content']
        if len(doc['content']) < len(shortest_doc):
            shortest_doc = doc['content']
    
    avg_word_count = word_count / total_docs
    
    print(Fore.CYAN + "\n📊 Document Analytics 📊" + Style.RESET_ALL)
    print(f"Total documents: {total_docs}")
    print(f"Average word count: {avg_word_count:.2f}")
    print("\nCategory distribution:")
    for category, count in categories.items():
        print(f"  - {category}: {count} ({count/total_docs*100:.2f}%)")
    print(f"\nLongest document: {len(longest_doc)} characters")
    print(f"Shortest document: {len(shortest_doc)} characters")

def rag_process():
    setup_logging()
    download_nltk_data()

    print(Fore.CYAN + Style.BRIGHT + """
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║   Welcome to the Enhanced RAG System!     ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """ + Style.RESET_ALL)

    while True:
        try:
            choice = display_menu()

            if choice == '1':
                content = input(Fore.YELLOW + "Enter document content: " + Style.RESET_ALL)
                category = input(Fore.YELLOW + "Enter category (default/important/personal/work): " + Style.RESET_ALL)
                if category not in ['important', 'personal', 'work']:
                    category = 'default'
                add_document(content, category)
                print(Fore.GREEN + "Document added successfully." + Style.RESET_ALL)
            elif choice == '2':
                file_path = input(Fore.YELLOW + "Enter the path to the PDF file: " + Style.RESET_ALL)
                category = input(Fore.YELLOW + "Enter category (default/important/personal/work): " + Style.RESET_ALL)
                if category not in ['important', 'personal', 'work']:
                    category = 'default'
                success = process_pdf(file_path, category)
                if success:
                    print(Fore.GREEN + "PDF processed and added successfully." + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Failed to process PDF. Please check the file and try again." + Style.RESET_ALL)
            elif choice == '3':
                keyword = input(Fore.YELLOW + "Enter search keyword: " + Style.RESET_ALL)
                results = search_documents(keyword)
                if results:
                    selected_doc = select_document(results, f"Search Results for '{keyword}'")
                    if selected_doc:
                        print(Fore.CYAN + "\nSelected document:" + Style.RESET_ALL)
                        print(f"Timestamp: {selected_doc['timestamp']}")
                        print(f"Content: {selected_doc['content']}")
                    else:
                        print(Fore.YELLOW + "Returned to main menu." + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + f"No documents found containing '{keyword}'." + Style.RESET_ALL)
            elif choice == '4':
                documents = list_all_documents()
                if documents:
                    selected_doc = select_document(documents, "All Documents")
                    if selected_doc:
                        print(Fore.CYAN + "\nSelected document:" + Style.RESET_ALL)
                        print(f"Timestamp: {selected_doc['timestamp']}")
                        print(f"Content: {selected_doc['content']}")
                    else:
                        print(Fore.YELLOW + "Returned to main menu." + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "No documents found." + Style.RESET_ALL)
            elif choice == '5':
                filename = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                duration = int(input(Fore.YELLOW + "Enter recording duration in seconds: " + Style.RESET_ALL))
                print(Fore.CYAN + "Recording audio..." + Style.RESET_ALL)
                success, message = record_audio(filename, duration)
                if success:
                    print(Fore.GREEN + "Audio recorded successfully." + Style.RESET_ALL)
                    print(Fore.CYAN + "Transcribing audio..." + Style.RESET_ALL)
                    text = transcribe_audio(filename)
                    print(Fore.GREEN + f"Transcribed text: {text}" + Style.RESET_ALL)
                    add_document(text, 'audio_transcript')
                    print(Fore.GREEN + "Transcribed text added to database." + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"Error recording audio: {message}" + Style.RESET_ALL)
            elif choice == '6':
                audio_files = list_audio_files()
                if audio_files:
                    print(Fore.CYAN + "Available audio files:" + Style.RESET_ALL)
                    for i, file in enumerate(audio_files):
                        print(f"{i+1}. {file}")
                    file_number = int(input(Fore.YELLOW + "Enter the number of the file to play: " + Style.RESET_ALL))
                    if 1 <= file_number <= len(audio_files):
                        print(Fore.CYAN + "Playing audio..." + Style.RESET_ALL)
                        play_audio(audio_files[file_number-1])
                    else:
                        print(Fore.RED + "Invalid file number." + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "No audio files found." + Style.RESET_ALL)
            elif choice == '7':
                audio_files = list_audio_files()
                if audio_files:
                    print(Fore.CYAN + "Available audio files:" + Style.RESET_ALL)
                    for file in audio_files:
                        print(file)
                else:
                    print(Fore.YELLOW + "No audio files found." + Style.RESET_ALL)
            elif choice == '8':
                documents = list_all_documents()
                if documents:
                    selected_doc = select_document(documents, "Select Document to Delete")
                    if selected_doc:
                        confirm = input(Fore.YELLOW + f"Are you sure you want to delete this document? (y/n)\nContent: {selected_doc['content'][:50]}...\n" + Style.RESET_ALL)
                        if confirm.lower() == 'y':
                            delete_document(selected_doc.doc_id)
                            print(Fore.GREEN + "Document deleted successfully." + Style.RESET_ALL)
                        else:
                            print(Fore.YELLOW + "Deletion cancelled." + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Returned to main menu." + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "No documents found." + Style.RESET_ALL)
            elif choice == '9':
                audio_files = list_audio_files()
                if audio_files:
                    print(Fore.CYAN + "Select an audio file to delete:" + Style.RESET_ALL)
                    for i, file in enumerate(audio_files):
                        print(f"{i+1}. {file}")
                    file_number = int(input(Fore.YELLOW + "Enter the number of the file to delete: " + Style.RESET_ALL))
                    if 1 <= file_number <= len(audio_files):
                        delete_audio(audio_files[file_number-1])
                        print(Fore.GREEN + "Audio file deleted successfully." + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Invalid file number." + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "No audio files found." + Style.RESET_ALL)
            elif choice == '10':
                nlp_mode()
            elif choice == '11':
                speech_interaction_mode({'add_document': add_document, 'search_documents': search_documents})
            elif choice == '12':
                document_manager = {
                    'add_document': add_document,
                    'search_documents': search_documents,
                    'list_all_documents': list_all_documents,
                    'delete_document': delete_document
                }
                chatbot_mode(document_manager, speech_to_text, lambda x: print(Fore.BLUE + "Chatbot: " + Style.RESET_ALL + x))
            elif choice == '13':
                advanced_document_management()
            elif choice == '14':
                print(Fore.CYAN + "Exiting the Enhanced RAG System. Goodbye!" + Style.RESET_ALL)
                break
            else:
                print(Fore.RED + "Invalid choice. Please try again." + Style.RESET_ALL)

            # Add a small delay and loading animation between operations
            threading.Thread(target=animated_loading, args=(1,)).start()

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {str(e)}")
            print(Fore.RED + f"An unexpected error occurred: {str(e)}" + Style.RESET_ALL)
            print(Fore.YELLOW + "Please check the log file for more details." + Style.RESET_ALL)

        # Ask if the user wants to continue
        continue_choice = input(Fore.CYAN + "\nDo you want to perform another operation? (y/n): " + Style.RESET_ALL).lower()
        if continue_choice != 'y':
            print(Fore.CYAN + "Thank you for using the Enhanced RAG System. Goodbye!" + Style.RESET_ALL)
            break

def main():
    try:
        rag_process()
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        print(Fore.RED + f"A critical error occurred: {str(e)}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Please check the log file for more details." + Style.RESET_ALL)
    finally:
        # Perform any necessary cleanup
        print(Fore.CYAN + "Cleaning up and saving data..." + Style.RESET_ALL)
        # Add any cleanup code here (e.g., saving data, closing connections)

if __name__ == "__main__":
    main()