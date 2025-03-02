import string
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer

# !MPORTANT: NEEDS TO RUN nltk.download("stopwords")

# Load stopwords once
stop_words = set(stopwords.words("english"))
text_model = SentenceTransformer("all-MiniLM-L6-v2") 

def preprocess_query(query):
    """Cleans and tokenizes a user query for better vector search."""
    # Step 1: Normalize text (lowercase, remove punctuation)
    query = query.lower().strip()
    query = query.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation

    # Step 2: Remove stopwords & tokenize
    tokens = query.split()
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Step 3: Rejoin tokens for FAISS-friendly search
    clean_query = " ".join(filtered_tokens)

    # Step 4: Generate an embedding for FAISS search
    query_embedding = text_model.encode([clean_query])  # Convert to embedding

    return clean_query, query_embedding


if __name__ == "__main__":
    query = "How do I read the content of a server response?"
    clean_query, query_vector = preprocess_query(query)

    print("Query:", query)
    print("Processed Query:", clean_query)
    print("Embedding Shape:", query_vector.shape)
