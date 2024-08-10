import spacy
from config import SPACY_MODEL

nlp = spacy.load(SPACY_MODEL)

def perform_nlp_tasks(text):
    doc = nlp(text)
    
    analysis = {
        "Named Entities": [(ent.text, ent.label_) for ent in doc.ents],
        "Part-of-Speech": [(token.text, token.pos_) for token in doc[:10]],
        "Dependency Parsing": [(token.text, token.dep_) for token in doc[:10]],
        "Noun Chunks": [chunk.text for chunk in doc.noun_chunks]
    }
    
    return analysis

def print_nlp_analysis(analysis):
    print("\nNLP Analysis:")
    for key, value in analysis.items():
        print(f"\n{key}:")
        for item in value:
            if isinstance(item, tuple):
                print(f"   - {item[0]}: {item[1]}")
            else:
                print(f"   - {item}")

def nlp_mode(document_manager):
    while True:
        print("\nNLP Mode:")
        print("1. Analyze a document")
        print("2. Analyze custom text")
        print("3. Return to main menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            documents = document_manager.list_all_documents()
            if documents:
                # Implement document selection here
                selected_doc = documents[0]  # Placeholder
                analysis = perform_nlp_tasks(selected_doc['content'])
                print_nlp_analysis(analysis)
            else:
                print("No documents found.")
        elif choice == '2':
            text = input("Enter the text you want to analyze: ")
            analysis = perform_nlp_tasks(text)
            print_nlp_analysis(analysis)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")