import requests
from bs4 import BeautifulSoup
import json

def scrape_webpage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    sections = []  # List to hold structured documentation data
    current_section = None

    for tag in soup.find_all(["h1", "h2", "h3", "p", "pre", "code"]):
        text = tag.get_text().strip()

        if not text:
            continue  # Skip empty elements

        if tag.name in ["h1", "h2", "h3"]:
            # Start a new section when encountering a title
            if current_section:
                sections.append(current_section)
            current_section = {"title": text, "content": [], "code": []}

        elif tag.name == "p" and current_section:
            # Add paragraph content to the current section
            current_section["content"].append(text)

        elif tag.name in ["pre", "code"] and current_section:
            # Append code to the current section
            current_section["code"].append(text)

    if current_section:
        sections.append(current_section)  # Add the last processed section

    # Save structured data to a JSON file
    with open("structured_docs.json", "w", encoding="utf-8") as file:
        json.dump(sections, file, indent=4, ensure_ascii=False)

    return sections

# Example usage
url = "https://requests.readthedocs.io/en/latest/user/quickstart/"
structured_docs = scrape_webpage(url)

print("✅ Scraping complete! Data saved to 'structured_docs.json'.")
