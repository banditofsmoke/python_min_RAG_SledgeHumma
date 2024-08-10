from tinydb import TinyDB, Query
import datetime
import logging
import PyPDF2
import re
from config import DB_FILE, ENCRYPTION_KEY
from utils import get_absolute_path, is_valid_pdf, preprocess_text
from fuzzywuzzy import fuzz
from cryptography.fernet import Fernet

db = TinyDB(DB_FILE)

class DocumentEncryption:
    def __init__(self, key=ENCRYPTION_KEY):
        self.fernet = Fernet(key)

    def encrypt(self, data):
        return self.fernet.encrypt(data.encode())

    def decrypt(self, encrypted_data):
        return self.fernet.decrypt(encrypted_data).decode()

encryption = DocumentEncryption()

def add_document(content, category='default', file_type='text', encrypt=True):
    try:
        if encrypt:
            content = encryption.encrypt(content)
        db.insert({
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'category': category,
            'file_type': file_type,
            'encrypted': encrypt
        })
        print("Document added successfully.")
    except Exception as e:
        logging.error(f"Error adding document: {str(e)}")
        print(f"An error occurred while adding the document. Please check the log file.")

def advanced_search(query, threshold=70):
    query_tokens = set(preprocess_text(query))
    results = []
    for doc in db.all():
        content = doc['content']
        if doc.get('encrypted', False):
            content = encryption.decrypt(content)
        doc_tokens = set(preprocess_text(content))
        similarity = fuzz.token_set_ratio(query_tokens, doc_tokens)
        if similarity >= threshold:
            results.append((doc, similarity))
    return sorted(results, key=lambda x: x[1], reverse=True)

def search_documents(keyword):
    results = advanced_search(keyword)
    return [doc for doc, _ in results]

def list_all_documents():
    docs = db.all()
    for doc in docs:
        if doc.get('encrypted', False):
            doc['content'] = encryption.decrypt(doc['content'])
    return docs

def delete_document(doc_id):
    db.remove(doc_ids=[doc_id])

def read_latex_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Enhanced LaTeX cleanup
            text = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', '', text)
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
    except Exception as e:
        logging.error(f"Error reading PDF file '{file_path}': {str(e)}")
        raise

def process_pdf(file_path, category='default', chunk_size=1000):
    abs_path = get_absolute_path(file_path)
    if not os.path.exists(abs_path):
        print(f"Error: The file '{abs_path}' does not exist.")
        return False
    if not is_valid_pdf(abs_path):
        print(f"Error: The file '{abs_path}' is not a valid PDF file.")
        return False
    
    try:
        full_text = read_latex_pdf(abs_path)
        chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            add_document(chunk, category, f'pdf_chunk_{i+1}')
        
        print(f"PDF document '{abs_path}' processed and added successfully in {len(chunks)} chunks.")
        return True
    except Exception as e:
        print(f"Error processing the PDF file: {str(e)}")
        logging.error(f"Error processing PDF file '{abs_path}': {str(e)}")
        return False

def get_document(doc_id):
    doc = db.get(doc_id=doc_id)
    if doc and doc.get('encrypted', False):
        doc['content'] = encryption.decrypt(doc['content'])
    return doc

def update_document(doc_id, new_content, new_category=None):
    doc = db.get(doc_id=doc_id)
    if doc:
        if doc.get('encrypted', False):
            new_content = encryption.encrypt(new_content)
        updates = {'content': new_content}
        if new_category:
            updates['category'] = new_category
        db.update(updates, doc_ids=[doc_id])
        print("Document updated successfully.")
    else:
        print("Document not found.")