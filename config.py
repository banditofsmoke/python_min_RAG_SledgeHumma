import os
from cryptography.fernet import Fernet

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

# Encryption
ENCRYPTION_KEY = Fernet.generate_key()  # Generate a new key each time the app starts
# For persistent key, you might want to store this securely and load it instead of generating new each time