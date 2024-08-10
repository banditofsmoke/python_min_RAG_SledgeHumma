import logging
import os
import nltk

def setup_logging():
    logging.basicConfig(filename='mini_rag.log', level=logging.ERROR, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

def download_nltk_data():
    resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            print(f"Downloading {resource}...")
            nltk.download(resource, quiet=True)

def get_absolute_path(file_path):
    return os.path.abspath(os.path.expanduser(file_path))

def is_valid_pdf(file_path):
    return os.path.isfile(file_path) and file_path.lower().endswith('.pdf')

def text_input_alternative():
    print("Audio recording failed. Please enter your message as text:")
    return input("Your message: ")