import ollama
from scraping import search
from scraping import query_processing

def get_ai_response(query: str, directory: str) -> str:
    """
    Processes the user query, searches relevant documentation,
    and returns an AI-generated response.
    """
    clean_query, query_vector = query_processing.preprocess_query(query)
    context = search.search_docs(clean_query, directory)
    
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': f'Answer this coding query:{query} with this context from the documentation: {context}'}]
    )
    
    return response['message']['content']
