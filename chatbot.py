import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import random
import re
from colorama import Fore, Back, Style, init

init(autoreset=True)  # Initialize colorama

class EnhancedRAGChatbot:
    def __init__(self, document_manager):
        self.document_manager = document_manager
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings', 'howdy'],
            'farewell': ['bye', 'goodbye', 'see you', 'farewell'],
            'search': ['find', 'search', 'look for', 'locate'],
            'add': ['add', 'create', 'new', 'insert'],
            'delete': ['delete', 'remove', 'erase', 'eliminate'],
            'list': ['list', 'show', 'display', 'enumerate'],
            'help': ['help', 'assist', 'support', 'guide'],
            'summarize': ['summarize', 'summary', 'brief', 'overview'],
            'categorize': ['categorize', 'classify', 'group', 'sort']
        }
        self.state = {'context': None, 'last_docs': []}
        self.personality = self.generate_personality()

    def generate_personality(self):
        traits = {
            'friendliness': random.uniform(0.7, 1.0),
            'formality': random.uniform(0.3, 0.7),
            'enthusiasm': random.uniform(0.6, 1.0),
            'helpfulness': random.uniform(0.8, 1.0)
        }
        return traits

    def preprocess(self, text):
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalnum()]
        tokens = [token for token in tokens if token not in self.stop_words]
        return tokens

    def classify_intent(self, tokens):
        intent_scores = Counter()
        for intent, keywords in self.intents.items():
            intent_scores[intent] = sum(token in keywords for token in tokens)
        return intent_scores.most_common(1)[0][0] if intent_scores else 'unknown'

    def generate_response(self, intent, tokens):
        response = self.get_intent_response(intent, tokens)
        return self.apply_personality(response)

    def get_intent_response(self, intent, tokens):
        if intent == 'greeting':
            return self.greeting_response()
        elif intent == 'farewell':
            return self.farewell_response()
        elif intent == 'search':
            return self.search_response(tokens)
        elif intent == 'add':
            return self.add_response(tokens)
        elif intent == 'delete':
            return self.delete_response(tokens)
        elif intent == 'list':
            return self.list_response()
        elif intent == 'help':
            return self.help_response()
        elif intent == 'summarize':
            return self.summarize_response(tokens)
        elif intent == 'categorize':
            return self.categorize_response(tokens)
        else:
            return "I'm not sure I understand. Could you please rephrase your request?"

    def apply_personality(self, response):
        if self.personality['friendliness'] > 0.8:
            response = f"😊 {response}"
        if self.personality['formality'] < 0.5:
            response = response.replace("Hello", "Hey").replace("Goodbye", "Bye")
        if self.personality['enthusiasm'] > 0.8:
            response = f"{response} 🎉"
        if self.personality['helpfulness'] > 0.9:
            response += "\nIs there anything else I can help you with?"
        return response

    def greeting_response(self):
        greetings = [
            "Hello! How can I assist you today?",
            "Hi there! What can I do for you?",
            "Greetings! How may I help you?",
            "Hey! What would you like to know about your documents?"
        ]
        return random.choice(greetings)

    def farewell_response(self):
        farewells = [
            "Goodbye! Have a great day!",
            "Farewell! Don't hesitate to return if you need more assistance.",
            "See you later! It was a pleasure helping you.",
            "Bye for now! Remember, I'm always here to help with your documents."
        ]
        return random.choice(farewells)

    def search_response(self, tokens):
        keywords = [token for token in tokens if token not in self.intents['search']]
        if not keywords:
            return "What would you like me to search for in the documents?"
        
        results = self.document_manager['search_documents'](' '.join(keywords))
        if results:
            self.state['last_docs'] = results[:5]
            response = f"I found {len(results)} documents containing '{' '.join(keywords)}'.\n"
            response += "Here are the top results:\n"
            for i, doc in enumerate(self.state['last_docs'], 1):
                response += f"{i}. {doc['content'][:50]}...\n"
            response += "\nWould you like me to summarize any of these documents?"
        else:
            response = f"I couldn't find any documents containing '{' '.join(keywords)}'. Would you like to try a different search?"
        return response

    def add_response(self, tokens):
        self.state['context'] = 'adding'
        return "Sure, I can help you add a new document. What content would you like to add?"

    def delete_response(self, tokens):
        self.state['context'] = 'deleting'
        return "I can help you delete a document. Please provide the ID or the beginning of the content of the document you want to delete."

    def list_response(self):
        docs = self.document_manager['list_all_documents']()
        if docs:
            self.state['last_docs'] = docs[:10]
            response = "Here are the most recent documents in the system:\n"
            for i, doc in enumerate(self.state['last_docs'], 1):
                response += f"{i}. {doc['content'][:50]}...\n"
            response += "\nWould you like more details on any of these documents?"
        else:
            response = "There are currently no documents in the system. Would you like to add one?"
        return response

    def help_response(self):
        return """I can help you with the following tasks:
1. Search for documents
2. Add new documents
3. Delete existing documents
4. List all documents
5. Summarize document content
6. Categorize documents

Just tell me what you'd like to do, and I'll guide you through the process!"""

    def summarize_response(self, tokens):
        if not self.state['last_docs']:
            return "I'm sorry, but I don't have any documents to summarize right now. Would you like to search for some documents first?"
        
        try:
            doc_num = int(tokens[0]) - 1
            if 0 <= doc_num < len(self.state['last_docs']):
                doc = self.state['last_docs'][doc_num]
                summary = self.summarize_text(doc['content'])
                return f"Here's a summary of document {doc_num + 1}:\n{summary}"
            else:
                return "I'm sorry, but that document number is not valid. Please choose a number from the list I provided earlier."
        except ValueError:
            return "Which document would you like me to summarize? Please provide the number from the list I showed earlier."

    def categorize_response(self, tokens):
        if not self.state['last_docs']:
            return "I don't have any documents to categorize right now. Would you like to search for or list some documents first?"
        
        categories = self.categorize_documents(self.state['last_docs'])
        response = "I've categorized the documents as follows:\n"
        for category, docs in categories.items():
            response += f"\n{category.capitalize()}:\n"
            for doc in docs:
                response += f"- {doc['content'][:50]}...\n"
        return response

    def summarize_text(self, text, sentences=3):
        # This is a very basic summarization. In a real-world scenario, you'd want to use a more sophisticated method.
        sentences = text.split('.')[:sentences]
        return '. '.join(sentences) + '.'

    def categorize_documents(self, docs):
        # This is a basic categorization. In a real-world scenario, you'd want to use more advanced NLP techniques.
        categories = {'work': [], 'personal': [], 'other': []}
        for doc in docs:
            if 'work' in doc['content'].lower():
                categories['work'].append(doc)
            elif 'personal' in doc['content'].lower():
                categories['personal'].append(doc)
            else:
                categories['other'].append(doc)
        return categories

    def process_input(self, user_input):
        tokens = self.preprocess(user_input)
        intent = self.classify_intent(tokens)
        
        if self.state['context'] == 'adding':
            self.document_manager['add_document'](user_input, 'chatbot_added')
            self.state['context'] = None
            return "Document added successfully! Is there anything else you'd like to do?"
        
        if self.state['context'] == 'deleting':
            docs = self.document_manager['list_all_documents']()
            for doc in docs:
                if user_input.lower() in doc['content'].lower():
                    self.document_manager['delete_document'](doc.doc_id)
                    self.state['context'] = None
                    return f"Document containing '{user_input}' has been deleted. Is there anything else I can help with?"
            self.state['context'] = None
            return "I couldn't find a document matching that description. Would you like to try again or do something else?"
        
        return self.generate_response(intent, tokens)

def chatbot_mode(document_manager, speech_to_text, text_to_speech):
    chatbot = EnhancedRAGChatbot(document_manager)
    print(Fore.CYAN + Style.BRIGHT + "🤖 Enhanced RAG Chatbot Activated 🤖" + Style.RESET_ALL)
    print(Fore.YELLOW + "Say 'exit' to return to the main menu. Type 'voice' to use speech input." + Style.RESET_ALL)
    
    while True:
        user_input = input(Fore.GREEN + "You: " + Style.RESET_ALL)
        
        if user_input.lower() == 'voice':
            print(Fore.YELLOW + "Listening... Speak now." + Style.RESET_ALL)
            user_input = speech_to_text()
            if user_input is None:
                print(Fore.RED + "Sorry, I didn't catch that. Please try again." + Style.RESET_ALL)
                continue
            print(Fore.GREEN + f"You said: {user_input}" + Style.RESET_ALL)
        
        if user_input.lower() == 'exit':
            print(Fore.CYAN + Style.BRIGHT + "Thank you for using the Enhanced RAG Chatbot. Goodbye!" + Style.RESET_ALL)
            break
        
        response = chatbot.process_input(user_input)
        print(Fore.BLUE + "Chatbot: " + Style.RESET_ALL + response)
        text_to_speech(response)