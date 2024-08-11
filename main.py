import asyncio
import logging
import os
import datetime
from colorama import init
import curses

from utils import setup_logging, download_nltk_data
from document_manager import add_document, search_documents, list_all_documents, delete_document, process_pdf
from audio_processor import record_audio, transcribe_audio, play_audio, list_audio_files, delete_audio, speech_to_text
from nlp_processor import nlp_mode
from chatbot import chatbot_mode
from user_interface import AIThemedInterface, show_message, get_confirmation, get_input, select_document

init(autoreset=True)  # Initialize colorama

async def speech_interaction_mode(stdscr):
    await show_message(stdscr, "Speech Interaction", "Say 'exit' to return to the main menu")
    
    while True:
        await show_message(stdscr, "Listening", "Speak now.")
        text = speech_to_text()
        if text is None:
            await show_message(stdscr, "Error", "Sorry, I didn't catch that. Please try again.")
            continue
        
        await show_message(stdscr, "You said", text)
        
        if text.lower() == 'exit':
            break
        
        if text.lower().startswith('add document'):
            content = text[len('add document'):].strip()
            add_document(content, 'speech_input')
            await show_message(stdscr, "Success", "Document added successfully.")
        elif text.lower().startswith('search'):
            query = text[len('search'):].strip()
            results = search_documents(query)
            if results:
                result_text = "Search results:\n" + "\n".join([f"- {doc['content'][:50]}..." for doc in results[:3]])
                await show_message(stdscr, "Search Results", result_text)
            else:
                await show_message(stdscr, "No Results", "No documents found.")
        else:
            await show_message(stdscr, "Unknown Command", "Command not recognized. You can say 'add document [content]' or 'search [query]'.")

async def advanced_document_management(stdscr):
    interface = AIThemedInterface()
    interface.menu_items = [
        "Batch import documents",
        "Export documents",
        "Document analytics",
        "Return to main menu"
    ]
    
    while True:
        choice = await interface.run(stdscr)
        
        if choice == "Batch import documents":
            await batch_import_documents(stdscr)
        elif choice == "Export documents":
            await export_documents(stdscr)
        elif choice == "Document analytics":
            await document_analytics(stdscr)
        elif choice == "Return to main menu":
            break

async def batch_import_documents(stdscr):
    folder_path = await get_input(stdscr, "Batch Import", "Enter the folder path containing documents to import:")
    if not os.path.isdir(folder_path):
        await show_message(stdscr, "Error", "Invalid folder path. Please try again.")
        return
    
    files = [f for f in os.listdir(folder_path) if f.endswith(('.txt', '.pdf'))]
    if not files:
        await show_message(stdscr, "No Files", "No .txt or .pdf files found in the specified folder.")
        return
    
    await show_message(stdscr, "Import Started", f"Importing {len(files)} files...")
    for file in files:
        file_path = os.path.join(folder_path, file)
        if file.endswith('.pdf'):
            process_pdf(file_path, 'batch_import')
        else:
            with open(file_path, 'r') as f:
                content = f.read()
                add_document(content, 'batch_import')
    
    await show_message(stdscr, "Import Complete", f"Successfully imported {len(files)} documents.")

async def export_documents(stdscr):
    documents = list_all_documents()
    if not documents:
        await show_message(stdscr, "No Documents", "No documents to export.")
        return
    
    export_path = await get_input(stdscr, "Export", "Enter the folder path to export documents:")
    if not os.path.isdir(export_path):
        try:
            os.makedirs(export_path)
        except OSError:
            await show_message(stdscr, "Error", "Failed to create export directory. Please try again.")
            return
    
    await show_message(stdscr, "Export Started", f"Exporting {len(documents)} documents...")
    for doc in documents:
        filename = f"doc_{doc.doc_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(os.path.join(export_path, filename), 'w') as f:
            f.write(f"Timestamp: {doc['timestamp']}\n")
            f.write(f"Category: {doc['category']}\n")
            f.write(f"Content:\n{doc['content']}")
    
    await show_message(stdscr, "Export Complete", f"Successfully exported {len(documents)} documents to {export_path}")

async def document_analytics(stdscr):
    documents = list_all_documents()
    if not documents:
        await show_message(stdscr, "No Documents", "No documents available for analysis.")
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
    
    analytics_text = f"""Document Analytics:
Total documents: {total_docs}
Average word count: {avg_word_count:.2f}

Category distribution:
{', '.join([f"{category}: {count} ({count/total_docs*100:.2f}%)" for category, count in categories.items()])}

Longest document: {len(longest_doc)} characters
Shortest document: {len(shortest_doc)} characters"""

    await show_message(stdscr, "Document Analytics", analytics_text)

async def rag_process(stdscr):
    setup_logging()
    download_nltk_data()

    interface = AIThemedInterface()

    while True:
        try:
            choice = await interface.run(stdscr)

            if choice == "Exit":
                if await get_confirmation(stdscr, "Exit", "Are you sure you want to exit?"):
                    await show_message(stdscr, "Goodbye", "Thank you for using the Enhanced RAG System. Goodbye!")
                    break
                continue

            if choice == "Add text document":
                content = await get_input(stdscr, "Add Document", "Enter document content:")
                category = await get_input(stdscr, "Add Document", "Enter category (default/important/personal/work):")
                if category not in ['important', 'personal', 'work']:
                    category = 'default'
                add_document(content, category)
                await show_message(stdscr, "Success", "Document added successfully.")
            elif choice == "Add PDF document":
                file_path = await get_input(stdscr, "Add PDF", "Enter the path to the PDF file:")
                category = await get_input(stdscr, "Add PDF", "Enter category (default/important/personal/work):")
                if category not in ['important', 'personal', 'work']:
                    category = 'default'
                success = process_pdf(file_path, category)
                if success:
                    await show_message(stdscr, "Success", "PDF processed and added successfully.")
                else:
                    await show_message(stdscr, "Error", "Failed to process PDF. Please check the file and try again.")
            elif choice == "Search documents":
                keyword = await get_input(stdscr, "Search", "Enter search keyword:")
                results = search_documents(keyword)
                if results:
                    selected_doc = await select_document(stdscr, results, f"Search Results for '{keyword}'")
                    if selected_doc:
                        await show_message(stdscr, "Selected Document", f"Timestamp: {selected_doc['timestamp']}\nContent: {selected_doc['content']}")
                else:
                    await show_message(stdscr, "No Results", f"No documents found containing '{keyword}'.")
            elif choice == "List all documents":
                documents = list_all_documents()
                if documents:
                    selected_doc = await select_document(stdscr, documents, "All Documents")
                    if selected_doc:
                        await show_message(stdscr, "Selected Document", f"Timestamp: {selected_doc['timestamp']}\nContent: {selected_doc['content']}")
                else:
                    await show_message(stdscr, "No Documents", "No documents found.")
            elif choice == "Record and transcribe audio":
                filename = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                duration = int(await get_input(stdscr, "Record Audio", "Enter recording duration in seconds:"))
                await show_message(stdscr, "Recording", "Recording audio...")
                success, message = record_audio(filename, duration)
                if success:
                    await show_message(stdscr, "Success", "Audio recorded successfully.")
                    await show_message(stdscr, "Transcribing", "Transcribing audio...")
                    text = transcribe_audio(filename)
                    await show_message(stdscr, "Transcription", f"Transcribed text: {text}")
                    add_document(text, 'audio_transcript')
                    await show_message(stdscr, "Success", "Transcribed text added to database.")
                else:
                    await show_message(stdscr, "Error", f"Error recording audio: {message}")
            elif choice == "Play audio":
                audio_files = list_audio_files()
                if audio_files:
                    file_list = "\n".join([f"{i+1}. {file}" for i, file in enumerate(audio_files)])
                    file_number = int(await get_input(stdscr, "Play Audio", f"Available audio files:\n{file_list}\nEnter the number of the file to play:"))
                    if 1 <= file_number <= len(audio_files):
                        await show_message(stdscr, "Playing", "Playing audio...")
                        play_audio(audio_files[file_number-1])
                    else:
                        await show_message(stdscr, "Error", "Invalid file number.")
                else:
                    await show_message(stdscr, "No Files", "No audio files found.")
            elif choice == "List all audio files":
                audio_files = list_audio_files()
                if audio_files:
                    file_list = "\n".join(audio_files)
                    await show_message(stdscr, "Audio Files", f"Available audio files:\n{file_list}")
                else:
                    await show_message(stdscr, "No Files", "No audio files found.")
            elif choice == "Delete document":
                documents = list_all_documents()
                if documents:
                    selected_doc = await select_document(stdscr, documents, "Select Document to Delete")
                    if selected_doc:
                        if await get_confirmation(stdscr, "Confirm Deletion", f"Are you sure you want to delete this document?\nContent: {selected_doc['content'][:50]}..."):
                            delete_document(selected_doc.doc_id)
                            await show_message(stdscr, "Success", "Document deleted successfully.")
                        else:
                            await show_message(stdscr, "Cancelled", "Deletion cancelled.")
                else:
                    await show_message(stdscr, "No Documents", "No documents found.")
            elif choice == "Delete audio file":
                audio_files = list_audio_files()
                if audio_files:
                    file_list = "\n".join([f"{i+1}. {file}" for i, file in enumerate(audio_files)])
                    file_number = int(await get_input(stdscr, "Delete Audio", f"Select an audio file to delete:\n{file_list}\nEnter the number of the file to delete:"))
                    if 1 <= file_number <= len(audio_files):
                        if await get_confirmation(stdscr, "Confirm Deletion", f"Are you sure you want to delete {audio_files[file_number-1]}?"):
                            delete_audio(audio_files[file_number-1])
                            await show_message(stdscr, "Success", "Audio file deleted successfully.")
                        else:
                            await show_message(stdscr, "Cancelled", "Deletion cancelled.")
                    else:
                        await show_message(stdscr, "Error", "Invalid file number.")
                else:
                    await show_message(stdscr, "No Files", "No audio files found.")
            elif choice == "NLP mode":
                await nlp_mode(stdscr)
            elif choice == "Speech interaction mode":
                await speech_interaction_mode(stdscr)
            elif choice == "Chatbot mode":
                await chatbot_mode(stdscr)
            elif choice == "Advanced document management":
                await advanced_document_management(stdscr)
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {str(e)}")
            await show_message(stdscr, "Error", f"An unexpected error occurred: {str(e)}\nPlease check the log file for more details.")

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: asyncio.run(rag_process(stdscr)))