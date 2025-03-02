from setuptools import setup, find_packages

setup(
    name="alexandria",
    version="0.1.0",
    packages=find_packages(include=["alexandria", "clifrontend", "scraping", "libfetch"]),
    install_requires=[
        "click",
        "textual",
        "requests",
        "prompt_toolkit",
        "rich",
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
