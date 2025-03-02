<picture>
  <img alt="Shows an image of Library of Alexandria with the text to the right, beige background." src="./static/alexandria.png"  width="full">
</picture>

<h2 align="center">Your command-line companion that demystifies niche libraries and brings clarity to complex codebases </h2>

[![Devpost](https://img.shields.io/badge/Devpost-HackIllinois_2025%20-blue?logo=devpost)](https://devpost.com/software/883389/joins/frpgZq6YfHu1kdWQSLLKmQ)

# Introduction
Developers waste too much time searching for documentation, switching between browser tabs, and asking the same questions over and over. Alexandria eliminates that friction by scanning your project, indexing its dependencies, and using an AI-powered local assistant to answer your questions—instantly.

Whether you're working in Python, Node.js, Java, Rust, or Go, Alexandria automatically detects the libraries you're using and fetches relevant documentation. Instead of Googling "How do I use FastAPI middleware?", just:
```
alexandria chat
How do I use FastAPI middleware?
```
Powered by FAISS for fast semantic search and Ollama for local AI reasoning, Alexandria works entirely offline—no API calls, no sending your project data to external services.

### 🚀 Who is this for?

- Junior developers needing quick answers without jumping between docs

- Mid-level engineers working across multiple languages

- Senior developers who want a fast, private way to query dependencies in their proprietary projects

No more endless Googling. No more tab-switching. Just ask, and get your answer instantly.

# Installation

### 1. Clone the repo 
```
git clone https://github.com/yourusername/alexandria.git
cd alexandria
```
### 2. Install ollama

Alexandria uses Ollama for local AI reasoning. If you haven't installed Ollama yet, follow these steps:
Visit the Ollama website for download and installation instructions.
Install Ollama according to your operating system's guidelines.
Verify your installation by running:

```bash
Copy
ollama version
```

### 3. Build and Set Up Alexandria
Dependencies: Install any required dependencies. For example, if Alexandria is built with Python, run:
```
pip install -r requirements.txt
```
Configuration: Customize your Alexandria configuration if needed. A sample configuration file (config.example.json) is provided—copy it to config.json and adjust the settings.

Build (if necessary): If Alexandria requires building or compiling components, follow the build instructions in the BUILD.md file.

# Tech Stack
🔧 Python – Core CLI development \
🔧 FAISS – Embedding creation and High-speed local semantic search \
🔧 Ollama – Self-hosted AI model for answering queries \
🔧 Rich CLI – Clean, intuitive terminal interface

# Features
✅ Scans dependencies automatically (Python, Node, Java, etc.) \
✅ Uses FAISS for fast semantic search \
✅ Works entirely offline (no API calls) \
✅ Supports custom model selection via Ollama \
✅ Persistent embeddings, updates when dependencies change

# How it works
### 1.  Scans Your Project For Relevant Dependencies

Alexandria automatically detects dependencies by scanning import statements (Python) and package manager files (package.json, requirements.txt, Cargo.toml, etc.).
It avoids unnecessary indexing (e.g., skips venv/ for Python).

### 2. Creates Embeddings from Documentation

For each detected library, Alexandria fetches relevant documentation links.
It then generates embeddings (vector representations of the documentation) using FAISS, storing them persistently for fast retrieval.

### 3. AI-Powered Search

When you ask a question (alexandria ask "How do I use FastAPI middleware?"), Alexandria retrieves the most relevant sections of documentation.
It then uses Ollama’s local LLM to generate a concise, useful response—without requiring an internet connection.

### 4. Works Offline, Update When Needed

Since all embeddings are stored locally, Alexandria doesn’t need API calls to function.
Rerunning alexandria update refreshes embeddings when dependencies change, keeping results accurate.

# Demo

[![AI Did My Groceries](https://github.com/user-attachments/assets/d9359085-bde6-41d4-aa4e-6520d0221872)](https://www.youtube.com/watch?v=L2Ya9PYNns8)

# License
This project is licensed under the MIT License. See the LICENSE file for details.
