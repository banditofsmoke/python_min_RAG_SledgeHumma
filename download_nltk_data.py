import nltk

def download_nltk_data():
    resources = ['punkt', 'stopwords', 'wordnet', 'punkt_tab']
    for resource in resources:
        print(f"Downloading {resource}...")
        nltk.download(resource, quiet=True)
    print("All NLTK data downloaded successfully!")

if __name__ == "__main__":
    download_nltk_data()