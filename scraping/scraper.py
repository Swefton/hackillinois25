import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Function to scrape text from a webpage
def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract paragraphs and headers
    texts = [tag.get_text() for tag in soup.find_all(["p", "h1", "h2", "h3", "code"])]
    
    return texts  # Return as list of text chunks

# Function to convert text into embeddings and store in FAISS index
def create_faiss_index(text_chunks, model):
    embeddings = model.encode(text_chunks)
    embedding_dim = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(embedding_dim)  # L2 distance-based index
    index.add(np.array(embeddings, dtype=np.float32))  # Store embeddings
    
    return index, text_chunks  # Return FAISS index and corresponding text chunks

# Function to search FAISS index for relevant text based on a query
def search_docs(query, index, model, text_chunks, k=3):
    query_embedding = model.encode([query])
    _, indices = index.search(np.array(query_embedding, dtype=np.float32), k)
    
    return [text_chunks[i] for i in indices[0]]  # Retrieve top-k relevant text sections

if __name__ == "__main__":
    # Define webpage URL
    url = "https://docs.python.org/3/library/os.html"  # Example: Python os module docs

    print(f"Scraping webpage: {url}")
    text_chunks = scrape_webpage(url)

    # Load SentenceTransformer model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Create FAISS index
    print("Creating FAISS index...")
    index, text_chunks = create_faiss_index(text_chunks, model)

    # Example query
    query = "what is malloc?"
    print(f"\n🔎 Searching for: {query}")

    # Search for relevant sections
    results = search_docs(query, index, model, text_chunks, k=3)

    # Display results
    print("\n📌 Most relevant sections:\n")
    for i, res in enumerate(results):
        print(f"{i+1}. {res}\n")
