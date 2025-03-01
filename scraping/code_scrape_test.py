import requests
from bs4 import BeautifulSoup

def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract paragraphs, headers, and code blocks
    texts = [tag.get_text() for tag in soup.find_all(["p", "h1", "h2", "h3", "code", "pre"])]

    with open("scraped.txt", "w", encoding="utf-8") as text_file:
        text_file.write("\n".join([text for text in texts if text.strip() != '']))
         
    return texts  # Return as list of text chunks

# Example usage
url = "https://requests.readthedocs.io/en/latest/"
scraped_texts = scrape_webpage(url)
print("\n".join(scraped_texts[:10]))  # Print first few results for preview
