# Enhanced Minimalist RAG System

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Welcome to the Enhanced Minimalist RAG (Retrieval-Augmented Generation) System! This project showcases a robust document management and natural language processing system built entirely with Python. This is the result of a 23 hour sprint. I tap here. Goodnight. Python ONLY. Have fun. GG, you legends. Sledge.

## 🌟 Project Overview

This RAG system is an open-source project developed as a comprehensive Python application. It serves as an educational tool to explore and implement various aspects of:

- Document management
- Audio processing
- Natural language processing (NLP)
- Chatbot functionality

All of this is achieved using only Python libraries, demonstrating the power and versatility of the Python ecosystem.

### 🎯 Purpose and Goals

1. Create a functional RAG system without relying on external Large Language Models (LLMs)
2. Showcase the capabilities of Python's built-in and commonly used libraries
3. Provide a learning platform for Python development and NLP concepts

### 🚨 Project Rule

**IMPORTANT**: This project is restricted to using only Python libraries. No external tools, frameworks, or languages other than Python may be used. This rule challenges developers and highlights the capabilities of Python's ecosystem.

## ✨ Features

- 📄 Document Management: 
  - Add, search, list, edit, and delete text documents
  - Support for PDF documents in LaTeX format
  - Pagination for large document sets
  - In-line search within document lists
  - Sorting options (by timestamp, content, or category)
  - Color coding for different document categories
- 🎤 Audio Handling:
  - Record audio with customizable duration
  - Transcribe audio to text
  - Play audio files
- 🧠 Natural Language Processing: Analyze text using NLTK for various NLP tasks
- 🤖 Chatbot: Interact with the system using natural language
- 🎛️ User-friendly interface with keyboard navigation

## 🛠️ Technologies and Libraries Used

- Python 3.x
- NLTK (Natural Language Toolkit)
- TinyDB for document storage
- PyAudio for audio recording
- SpeechRecognition for audio transcription
- gTTS (Google Text-to-Speech) for text-to-speech conversion
- prompt-toolkit for enhanced UI

## 📋 Prerequisites

- Python 3.7 or higher
- FFmpeg (for audio playback)
- LaTeX installation (for PDF support)

## 🚀 Installation Guide

1. Clone the repository:
   ```
   git clone https://github.com/banditofsmoke/python_mini_RAG_SledgeHumma.git
   cd python_mini_RAG_SledgeHumma
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv enhanced_rag_env
   source enhanced_rag_env/bin/activate  # On Windows, use `enhanced_rag_env\Scripts\activate`
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download necessary NLTK data:
   ```python
   python -c "import nltk; nltk.download(['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger'])"
   ```

5. Install FFmpeg (if not already installed):
   ```
   sudo apt update && sudo apt install ffmpeg
   ```

## 🖥️ Usage Instructions

To run the RAG system:

```
python mini_rag.py
```

### Main Menu Options

1. Add text document
2. Add PDF document (LaTeX format only)
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

### ⌨️ Key Bindings

When in document selection mode:
- Up/Down arrows: Navigate through documents
- Page Up/Page Down: Navigate between pages
- Enter: Select the current document
- Ctrl+D: Delete the selected document
- Ctrl+E: Edit the selected document
- Ctrl+S: Change sorting option

### 📝 Example Usage

Adding a document:
```
Enter your choice: 1
Enter document content: This is a sample document about Python programming.
Enter category (default/important/personal/work): important
Document added successfully.
```

Searching documents:
```
Enter your choice: 3
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

## 🏗️ System Architecture

The RAG system comprises several key components:

1. Document Management:
   - Uses TinyDB for storing and retrieving documents
   - Implements CRUD operations for documents
   - Supports PDF documents in LaTeX format

2. Audio Processing:
   - Utilizes PyAudio for recording audio
   - Employs SpeechRecognition for transcribing audio to text
   - Uses subprocess to play audio files

3. Natural Language Processing:
   - Leverages NLTK for tasks such as tokenization, part-of-speech tagging, and named entity recognition

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

## 🔧 Troubleshooting

### ModuleNotFoundError
Ensure you're using the Python interpreter from your virtual environment:
```
which python
```
It should point to `/path/to/your/project/enhanced_rag_env/bin/python`

### PyAudio Issues
Install additional system dependencies:
```
sudo apt-get update
sudo apt-get install python3-dev libasound2-dev portaudio19-dev libportaudio2 libportaudiocpp0
pip install --upgrade pyaudio
```

### Audio Playback Issues
Verify FFmpeg installation:
```
ffmpeg -version
which ffplay
```

### ALSA-related Errors
1. Update audio drivers
2. Reinstall ALSA and PulseAudio:
   ```
   sudo apt-get update && sudo apt-get install --reinstall alsa-base pulseaudio
   sudo alsa force-reload
   ```
3. Add user to audio group:
   ```
   sudo usermod -a -G audio $USER
   ```
   Log out and log back in for changes to take effect.

## 🐛 Known Issues

- Audio recording and playback may encounter ALSA-related errors on some Linux systems.
- PDF document handling is currently limited to LaTeX format only.

## 🗺️ Development Roadmap

Future planned features:
- Voice integration for the chatbot
- Support for more document formats
- Improved document access control
- Agentic reasoning for advanced interactions
- Graphical user interface
- Enhanced error handling and logging
- Code modularization for better maintainability

Current limitations:
- Limited to text and LaTeX PDF formats
- Basic intent classification system
- Local document storage only

## 🤝 Contributing Guidelines

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

Please adhere to PEP 8 style guidelines and include appropriate comments.

## 📄 License Information

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- NLTK developers for essential NLP tools
- TinyDB creators for the lightweight document database
- PyAudio and SpeechRecognition library developers

Special thanks to the open-source community and all future contributors!
To my mentor, wwww.github.com/sebdg, thanks for just being a legend - oh, and the UI help.
## 📬 Contact Information

For questions, suggestions, or collaborations, please reach out:

Wayne Sletcher (SledgeHumma)
- LinkedIn: [Wayne Sletcher](https://www.linkedin.com/in/waynesletcheraisystemsbuilder/)
- Email: skeletonenglish@gmail.com
- GitHub: [banditofsmoke](https://github.com/banditofsmoke)
- Made in Sledge's Forge (Private Discord)

---

This project is part of an exciting journey into Python development and NLP. Your feedback and contributions are invaluable and greatly appreciated! Let's build something amazing together! 🚀