import os

# Database
DB_FILE = 'documents.json'

# Audio
AUDIO_FORMAT = 'wav'
AUDIO_CHANNELS = 1
AUDIO_RATE = 44100
AUDIO_CHUNK = 1024
AUDIO_RECORD_SECONDS = 5

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)

# NLP
SPACY_MODEL = 'en_core_web_sm'

# UI
ITEMS_PER_PAGE = 10