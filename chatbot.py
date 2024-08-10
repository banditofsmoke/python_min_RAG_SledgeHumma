from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

class SimpleRAGChatbot:
    def __init__(self, document_manager):
        self.document_manager = document_manager
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'farewell': ['bye', 'goodbye', 'see you'],
            'search': ['find', 'search', 'look for'],
            'add': ['add', 'create', 'new'],
            'delete': ['delete', 'remove', 'erase'],
            'list': ['list', 'show', 'display'],
            'help': ['help', 'assist', 'support']
        }

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
        if intent == 'greeting':
            return "Hello! How can I assist you with the document management system?"
        elif intent == 'farewell':
            return "Goodbye! Feel free to return if you need any more assistance."
        elif intent == 'search':
            keywords = [token for token in tokens if token not in self.intents['search']]
            if keywords:
                return f"Certainly! I'll search for documents containing: {', '.join(keywords)}"
            else:
                return "What would you like me to search for?"
        elif intent == 'add':
            return "Sure, I can help you add a new document. What content would you like to add?"
        elif intent == 'delete':
            return "I can help you delete a document. Please provide more details about which document you want to remove."
        elif intent == 'list':
            return "I'd be happy to list the documents for you. Here's what we have:"
        elif intent == 'help':
            return "I can help you with various tasks like searching, adding, deleting, and listing documents. What would you like to do?"
        else:
            return "I'm not sure I understand. Could you please rephrase your request?"

    def get_relevant_docs(self, tokens, limit=3):
        relevant_docs = []
        for doc in self.document_manager.list_all_documents():
            doc_tokens = self.preprocess(doc['content'])
            relevance = sum(token in doc_tokens for token in tokens)
            if relevance > 0:
                relevant_docs.append((doc, relevance))
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in relevant_docs[:limit]]

    def process_input(self, user_input):
        tokens = self.preprocess(user_input)
        intent = self.classify_intent(tokens)
        response = self.generate_response(intent, tokens)

        if intent in ['search', 'list']:
            relevant_docs = self.get_relevant_docs(tokens)
            if relevant_docs:
                response += "\nHere are some relevant documents:\n"
                for doc in relevant_docs:
                    response += f"- {doc['content'][:50]}...\n"
            else:
                response += "\nI couldn't find any relevant documents."

        return response

def chatbot_mode(document_manager, speech_to_text, text_to_speech):
    chatbot = SimpleRAGChatbot(document_manager)
    print("Entering chatbot mode. Say 'exit' to return to the main menu.")
    print("You can type your messages or say 'voice input' to speak.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == 'voice input':
            print("Listening... Speak now.")
            user_input = speech_to_text()
            if user_input is None:
                print("Sorry, I didn't catch that. Please try again.")
                continue
            print(f"You said: {user_input}")
        
        if user_input.lower() == 'exit':
            print("Exiting chatbot mode.")
            break
        
        response = chatbot.process_input(user_input)
        print("Chatbot:", response)
        text_to_speech(response)