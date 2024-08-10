from tinydb import TinyDB, Query
import datetime
import logging
import PyPDF2
import re
from config import DB_FILE
from utils import get_absolute_path, is_valid_pdf

db = TinyDB(DB_FILE)

def add_document(content, category='default', file_type='text'):
    try:
        db.insert({
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'category': category,
            'file_type': file_type
        })
        print("Document added successfully.")
    except Exception as e:
        logging.error(f"Error adding document: {str(e)}")
        print(f"An error occurred while adding the document. Please check the log file.")

def search_documents(keyword):
    query = Query()
    return db.search(query.content.search(keyword))

def list_all_documents():
    return db.all()

def delete_document(doc_id):
    db.remove(doc_ids=[doc_id])

def read_latex_pdf(file_path):
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

def process_pdf(file_path, category='default'):
    abs_path = get_absolute_path(file_path)
    if not os.path.exists(abs_path):
        print(f"Error: The file '{abs_path}' does not exist.")
        return False
    if not is_valid_pdf(abs_path):
        print(f"Error: The file '{abs_path}' is not a valid PDF file.")
        return False
    
    try:
        pdf_content = read_latex_pdf(abs_path)
        add_document(pdf_content, category, 'pdf')
        print(f"PDF document '{abs_path}' processed and added successfully.")
        return True
    except Exception as e:
        print(f"Error processing the PDF file: {str(e)}")
        logging.error(f"Error processing PDF file '{abs_path}': {str(e)}")
        return False