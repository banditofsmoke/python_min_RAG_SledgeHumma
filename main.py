import logging
from utils import setup_logging, download_nltk_data
from document_manager import add_document, search_documents, list_all_documents, delete_document, process_pdf
from audio_processor import record_audio, transcribe_audio, play_audio, list_audio_files, delete_audio, speech_to_text
from nlp_processor import nlp_mode
from chatbot import chatbot_mode
from user_interface import select_document, display_menu
from config import AUDIO_RECORD_SECONDS
import datetime
import os

def rag_process():
    setup_logging()
    download_nltk_data()

    while True:
        try:
            choice = display_menu()

            if choice == '1':
                content = input("Enter document content: ")
                category = input("Enter category (default/important/personal/work): ")
                if category not in ['important', 'personal', 'work']:
                    category = 'default'
                add_document(content, category)
            elif choice == '2':
                file_path = input("Enter the path to the PDF file: ")
                category = input("Enter category (default/important/personal/work): ")
                if category not in ['important', 'personal', 'work']:
                    category = 'default'
                process_pdf(file_path, category)
            elif choice == '3':
                keyword = input("Enter search keyword: ")
                results = search_documents(keyword)
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
            elif choice == '4':
                documents = list_all_documents()
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
                documents = list_all_documents()
                if documents:
                    selected_doc = select_document(documents, "Select Document to Delete")
                    if selected_doc:
                        confirm = input(f"Are you sure you want to delete this document? (y/n)\nContent: {selected_doc['content'][:50]}...\n")
                        if confirm.lower() == 'y':
                            delete_document(selected_doc.doc_id)
                            print("Document deleted successfully.")
                        else:
                            print("Deletion cancelled.")
                    else:
                        print("Returned to main menu.")
                else:
                    print("No documents found.")
            elif choice == '9':
                audio_files = list_audio_files()
                if audio_files:
                    print("Select an audio file to delete:")
                    for i, file in enumerate(audio_files):
                        print(f"{i+1}. {file}")
                    file_number = int(input("Enter the number of the file to delete: "))
                    if 1 <= file_number <= len(audio_files):
                        delete_audio(audio_files[file_number-1])
                    else:
                        print("Invalid file number.")
                else:
                    print("No audio files found.")
            elif choice == '10':
                nlp_mode()
            elif choice == '11':
                # Implement speech interaction mode here
                pass
            elif choice == '12':
                chatbot_mode(list_all_documents, speech_to_text, lambda x: print(x))  # Replace with actual TTS function
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