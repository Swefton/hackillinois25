import os
from scraping import scrape



test_libraries = [["pycord", "https://docs.pycord.dev/en/stable/"], ["spotipy", "https://spotipy.readthedocs.io/en/2.25.1/"], ["python-docx","https://python-docx.readthedocs.io/en/latest/"]]


for name,link in test_libraries:
    scrape.scrape_full_documentation(link, name, os.getcwd())

