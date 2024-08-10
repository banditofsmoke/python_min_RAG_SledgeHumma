# Enhanced Minimalist RAG System

This is an enhanced version of the simple Retrieval-Augmented Generation (RAG) system using PyTinyDB for document storage, with advanced document management, audio recording, transcription, and playback functionality.

## Features

- Document management:
  - Add, search, list, edit, and delete documents
  - Pagination for large document sets
  - In-line search within document lists
  - Sorting options (by timestamp, content, or category)
  - Color coding for different document categories
- Audio functionality:
  - Record audio with customizable duration
  - Transcribe audio to text
  - Play audio files
- User-friendly interface with keyboard navigation

## Prerequisites

- Python 3.7 or higher
- FFmpeg (for audio playback)

## Setup

1. Navigate to your project directory:
   ```
   cd ~/Projects/mini_rag
   ```

2. Create a new virtual environment:
   ```
   python3 -m venv enhanced_rag_env
   ```

3. Activate the virtual environment:
   ```
   source enhanced_rag_env/bin/activate
   ```

4. Install the required packages:
   ```
   pip install tinydb pyaudio SpeechRecognition prompt-toolkit
   ```

5. Install FFmpeg (if not already installed):
   ```
   sudo apt update
   sudo apt install ffmpeg
   ```

## Usage

1. Ensure you're in the project directory and the virtual environment is activated.

2. Run the script:
   ```
   python mini_rag.py
   ```

3. Follow the on-screen prompts to interact with the RAG system.

## Key Bindings

When in document selection mode:

- Up/Down arrows: Navigate through documents
- Page Up/Page Down: Navigate between pages
- Enter: Select the current document
- Ctrl+D: Delete the selected document
- Ctrl+E: Edit the selected document
- Ctrl+S: Change sorting option

## Troubleshooting

### ModuleNotFoundError

If you encounter "ModuleNotFoundError", ensure you're using the Python interpreter from your virtual environment:

1. Check which Python you're using:
   ```
   which python
   ```
   It should point to `/home/your_username/Projects/mini_rag/enhanced_rag_env/bin/python`

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

### Other Issues

If you're experiencing other issues:

1. Make sure all required packages are installed correctly.
2. Check that you're running the latest version of the script.
3. Ensure your virtual environment is activated when running the script.

If problems persist, try recreating your virtual environment and reinstalling the packages.

## Contributing

Feel free to fork this project and submit pull requests with improvements or bug fixes. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is open source and available under the [MIT License](https://opensource.org/licenses/MIT).