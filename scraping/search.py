from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import faiss
import numpy as np
import json

# Load structured documentation
with open("structured_docs.json", "r", encoding="utf-8") as file:
    sections = json.load(file)

# Load embedding models
text_model = SentenceTransformer("all-MiniLM-L6-v2")  # For title & paragraph search
code_model = SentenceTransformer("microsoft/codebert-base")  # For code search

# Step 1: Index Titles in FAISS
title_texts = [sec["title"] for sec in sections]
title_embeddings = text_model.encode(title_texts)
dim = title_embeddings.shape[1]

faiss_index = faiss.IndexFlatL2(dim)
faiss_index.add(np.array(title_embeddings, dtype=np.float32))

# Step 2: Prepare BM25 for Paragraph Search
paragraph_texts = [" ".join(sec["content"]) for sec in sections]  # Combine paragraphs per section
bm25 = BM25Okapi([text.split() for text in paragraph_texts])

# Step 3: Prepare FAISS for Code Search
code_texts = ["\n".join(sec["code"]) for sec in sections if sec["code"]]
code_embeddings = code_model.encode(code_texts) if code_texts else None

if code_embeddings is not None:
    code_index = faiss.IndexFlatL2(code_embeddings.shape[1])
    code_index.add(np.array(code_embeddings, dtype=np.float32))


# 🔎 Multi-Level Search
def search_docs(query, k=3):
    results = []
    query_embedding = text_model.encode([query])
    _, title_idx = faiss_index.search(np.array(query_embedding, dtype=np.float32), k)
    best_sections = [sections[i] for i in title_idx[0]]  # Top-k relevant sections

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
    # Example Queries
    search_docs("intents needed", k=3)
