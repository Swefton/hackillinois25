from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import faiss
import numpy as np
import os
import json
import glob

# Loading Text Models (Lazy Loaded)
text_model = SentenceTransformer("all-MiniLM-L6-v2") 
code_model = SentenceTransformer("microsoft/codebert-base")

def load_structured_docs(directory):
    """Load all structured_docs.json files from the given directory."""
    all_sections = []
    for json_file in glob.glob(os.path.join(directory, "**", "structured_docs.json"), recursive=True):
        with open(json_file, "r", encoding="utf-8") as file:
            sections = json.load(file)
            all_sections.extend(sections)
    return all_sections

def build_indexes(sections):
    """Build FAISS and BM25 indexes from the given sections."""
    # Step 1: Index Titles in FAISS
    title_texts = [sec["title"] for sec in sections]
    title_embeddings = text_model.encode(title_texts)
    dim = title_embeddings.shape[1]

    faiss_index = faiss.IndexFlatL2(dim)
    faiss_index.add(np.array(title_embeddings, dtype=np.float32))

    # Step 2: Prepare BM25 for Paragraph Search
    paragraph_texts = [" ".join(sec["content"]) for sec in sections]  
    bm25 = BM25Okapi([text.split() for text in paragraph_texts])

    # Step 3: Prepare FAISS for Code Search
    code_texts = ["\n".join(sec["code"]) for sec in sections if sec["code"]]
    code_embeddings = code_model.encode(code_texts) if code_texts else None

    code_index = None
    if code_embeddings is not None:
        code_index = faiss.IndexFlatL2(code_embeddings.shape[1])
        code_index.add(np.array(code_embeddings, dtype=np.float32))

    return faiss_index, bm25, code_index, sections

def search_docs(query, directory, k=3):
    """Search for relevant documents using FAISS and BM25."""
    sections = load_structured_docs(directory)
    if not sections:
        return []

    faiss_index, bm25, code_index, sections = build_indexes(sections)

    results = []
    query_embedding = text_model.encode([query])
    _, title_idx = faiss_index.search(np.array(query_embedding, dtype=np.float32), k)
    best_sections = [sections[i] for i in title_idx[0]]

    for best_section in best_sections:
        section_data = {
            "title": best_section["title"],
            "url": best_section["url"],
            "best_paragraph": None,
            "code": best_section.get("code", [])
        }

        section_paragraphs = best_section["content"]
        if section_paragraphs:
            bm25_section = BM25Okapi([p.split() for p in section_paragraphs])
            paragraph_scores = bm25_section.get_scores(query.split())
            best_paragraph_idx = np.argmax(paragraph_scores)
            section_data["best_paragraph"] = section_paragraphs[best_paragraph_idx]

        results.append(section_data)

    return results

if __name__ == "__main__":
    # Example usage
    results = search_docs("intents needed", "/path/to/.alexandria", k=3)
    print(results)
