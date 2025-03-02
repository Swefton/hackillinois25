from setuptools import setup, find_packages

setup(
    name="alexandria",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "textual",
        "requests",
        "sentence-transformers",
        "rank-bm25",
        "faiss-cpu",
        "ollama"
    ],
    entry_points={
        "console_scripts": [
            "alexandria=alexandria.cli:cli",
        ],
    },
)
