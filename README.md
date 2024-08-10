# Enhanced Minimalist RAG System

This is an enhanced version of the simple Retrieval-Augmented Generation (RAG) system using PyTinyDB for document storage, with advanced document management, audio recording, transcription, and playback functionality.

## Project Overview

This RAG (Retrieval-Augmented Generation) system is an open-source project developed as a first full Python project. It serves as an educational tool to understand and implement various aspects of document management, audio processing, natural language processing (NLP), and chatbot functionality using only Python libraries.

### Purpose and Goals

The main objectives of this project are:
1. To create a functional RAG system without relying on external Large Language Models (LLMs)
2. To demonstrate the capabilities of Python's built-in and commonly used libraries
3. To serve as a learning platform for Python development and NLP concepts

## Features

- Document Management: 
  - Add, search, list, edit, and delete text documents
  - Pagination for large document sets
  - In-line search within document lists
  - Sorting options (by timestamp, content, or category)
  - Color coding for different document categories
- Audio Handling:
  - Record audio with customizable duration
  - Transcribe audio to text
  - Play audio files
- Natural Language Processing: Analyze text using NLTK for various NLP tasks
- Chatbot: Interact with the system using natural language
- Simple "brain" for response generation without using LLMs
- User-friendly interface with keyboard navigation

## Technologies and Libraries Used

- Python 3.x
- NLTK (Natural Language Toolkit)
- TinyDB for document storage
- PyAudio for audio recording
- SpeechRecognition for audio transcription
- gTTS (Google Text-to-Speech) for text-to-speech conversion
- prompt-toolkit for enhanced UI

## Prerequisites

- Python 3.7 or higher
- FFmpeg (for audio playback)

## Installation Guide

1. Clone the repository:
   ```
   git clone https://github.com/your-username/enhanced-rag-system.git
   cd enhanced-rag-system
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python3 -m venv enhanced_rag_env
   source enhanced_rag_env/bin/activate  # On Windows, use `enhanced_rag_env\Scripts\activate`
   ```

3. Install required dependencies:
   ```
   pip install nltk tinydb pyaudio SpeechRecognition gTTS prompt-toolkit
   ```

4. Download necessary NLTK data:
   ```python
   import nltk
   nltk.download(['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger'])
   ```

5. Install FFmpeg (if not already installed):
   ```
   sudo apt update
   sudo apt install ffmpeg
   ```

## Usage Instructions

To run the RAG system:

```
python mini_rag.py
```

### Main Menu Options

1. Add text document
2. Add PDF document
3. Search documents
4. List all documents
5. Record and transcribe audio
6. Play audio
7. List all audio files
8. Delete document
9. Delete audio file
10. NLP mode
11. Speech interaction mode
12. Chatbot mode
13. Exit

### Key Bindings

When in document selection mode:
- Up/Down arrows: Navigate through documents
- Page Up/Page Down: Navigate between pages
- Enter: Select the current document
- Ctrl+D: Delete the selected document
- Ctrl+E: Edit the selected document
- Ctrl+S: Change sorting option

### Example Usage

Adding a document:
```
Enter your choice: 1
Enter document content: This is a sample document about Python programming.
Enter category (default/important/personal/work): important
Document added successfully.
```

Searching documents:
```
Enter your choice: 2
Enter search keyword: Python
Search Results for 'Python':
- This is a sample document about Python programming...
```

Using the chatbot:
```
Enter your choice: 12
Entering chatbot mode. Type 'exit' to return to the main menu.
You: Hello
Chatbot: Hello! How can I assist you with the document management system?
You: Can you search for documents about Python?
Chatbot: Certainly! I'll search for documents containing: python
Here are some relevant documents:
- This is a sample document about Python programming...
You: exit
Exiting chatbot mode.
```

## System Architecture

The RAG system is composed of several key components:

1. Document Management:
   - Uses TinyDB for storing and retrieving documents
   - Implements CRUD (Create, Read, Update, Delete) operations for documents

2. Audio Processing:
   - Utilizes PyAudio for recording audio
   - Employs SpeechRecognition for transcribing audio to text
   - Uses subprocess to play audio files

3. Natural Language Processing:
   - Leverages NLTK for various NLP tasks such as tokenization, part-of-speech tagging, and named entity recognition

4. Chatbot:
   - Implements a simple intent classification system
   - Generates responses based on classified intents
   - Integrates with the document management system for information retrieval

### Key Classes and Functions

- `SimpleRAGChatbot`: Main class for chatbot functionality
- `add_document()`: Adds a new document to the database
- `search_documents()`: Searches for documents based on keywords
- `record_audio()`: Records audio input from the user
- `transcribe_audio()`: Converts audio to text
- `perform_nlp_tasks()`: Executes various NLP analyses on text

## Troubleshooting

### ModuleNotFoundError
If you encounter "ModuleNotFoundError", ensure you're using the Python interpreter from your virtual environment:
1. Check which Python you're using:
   ```
   which python
   ```
   It should point to `/path/to/your/project/enhanced_rag_env/bin/python`
2. If it doesn't, activate your virtual environment:
   ```
   source enhanced_rag_env/bin/activate
   ```

### PyAudio Issues
If you're having issues with PyAudio, you may need to install additional system dependencies:
```
sudo apt-get update
sudo apt-get install python3-dev libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0
pip uninstall pyaudio
pip install pyaudio
```

### Audio Playback Issues
For issues with audio playback, ensure FFmpeg is installed correctly:
```
ffmpeg -version
which ffplay
```
If `ffplay` is not in your PATH, you may need to modify the `play_audio` function in `mini_rag.py` to use the full path to `ffplay`.

### ALSA-related Errors
If you encounter ALSA-related errors:

1. Ensure your system's audio drivers are up to date.
2. Try reinstalling ALSA and PulseAudio:
   ```
   sudo apt-get update
   sudo apt-get install --reinstall alsa-base pulseaudio
   ```
3. Restart the ALSA service:
   ```
   sudo alsa force-reload
   ```
4. Check if your user is in the audio group:
   ```
   groups $USER
   ```
   If 'audio' is not listed, add your user to the audio group:
   ```
   sudo usermod -a -G audio $USER
   ```
   Log out and log back in for the changes to take effect.

### Other Issues
If you're experiencing other issues:
1. Make sure all required packages are installed correctly.
2. Check that you're running the latest version of the script.
3. Ensure your virtual environment is activated when running the script.
If problems persist, try recreating your virtual environment and reinstalling the packages.

## Known Issues

- Audio recording and playback may encounter ALSA-related errors on some Linux systems.
- PDF document handling is currently in development.

## Development Roadmap

Future planned features include:
- Voice integration for the chatbot (Text-to-Speech and Speech-to-Text)
- Enhanced file system to support .txt and potentially PDF files
- Improved document access control for the chatbot
- Implementation of agentic reasoning for more advanced interactions
- Develop a graphical user interface
- Improve error handling and logging
- Modularize codebase for better maintainability

Known limitations:
- Currently limited to text and audio file formats
- Basic intent classification system in the chatbot
- Limited to local document storage and retrieval

## Contributing Guidelines

Contributions to improve and expand the RAG system are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch for your feature: `git checkout -b feature-name`
3. Implement your changes, following the project's coding standards
4. Write or update tests as necessary
5. Update the documentation to reflect your changes
6. Submit a pull request with a clear description of your changes

Please ensure your code adheres to PEP 8 style guidelines and includes appropriate comments.

## License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NLTK developers for providing essential NLP tools
- TinyDB creators for the lightweight document database
- PyAudio and SpeechRecognition libraries for audio processing capabilities

Special thanks to the open-source community and all future contributors to this project.

## Contact Information

For questions, suggestions, or collaborations, please reach out to:

Wayne Sletcher
Email: skeletonenglish@gmail.com
GitHub: https://github.com/banditofsmoke

---

This project is maintained as part of an educational journey in Python development and NLP. Your feedback and contributions are greatly appreciated!