from setuptools import setup, find_packages

setup(
    name="hackillinois25",
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
            "hackillinois25=hackillinois25.cli:cli",
        ],
    },
)
