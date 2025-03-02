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
    print(f"\n🔎 Searching for: {query}")

    # Step 1: Title Search (Find the top-k relevant sections)
    query_embedding = text_model.encode([query])
    _, title_idx = faiss_index.search(np.array(query_embedding, dtype=np.float32), k)
    best_sections = [sections[i] for i in title_idx[0]]  # Top-k relevant sections

    for rank, best_section in enumerate(best_sections, 1):
        print(f"\n🏆 Rank {rank} | 📌 Section: {best_section['title']}")
        print(f"🔗 Link: {best_section['url']}")

        # Step 2: BM25 Search **ONLY Within This Section**
        section_paragraphs = best_section["content"]
        
        if not section_paragraphs:
            print("\n❌ No matching content found.")
            continue
        
        bm25_section = BM25Okapi([p.split() for p in section_paragraphs])  # Only use paragraphs from best section
        paragraph_scores = bm25_section.get_scores(query.split())

        # Pick the highest-scoring paragraph **within this section**
        best_paragraph_idx = np.argmax(paragraph_scores)
        best_paragraph = section_paragraphs[best_paragraph_idx]

        print("\n📖 Best Matching Explanation:")
        print(best_paragraph)

        # Step 3: Code Search within the Best Section
        if best_section["code"]:
            print("\n💻 Code Example:")
            print("\n".join(best_section["code"]))
        else:
            print("\n❌ No code found for this query.")


# Example Queries
search_docs("intents needed", k=3)
