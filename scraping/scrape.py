import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
from collections import deque

def get_valid_links(soup, base_url, visited):
    """Extract and normalize valid documentation links from a page."""
    valid_links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)
        
        # Ensure it's within the same domain and not visited
        if parsed_url.netloc == urlparse(base_url).netloc and full_url not in visited:
            if "#" not in parsed_url.path and "search" not in parsed_url.path:
                valid_links.add(full_url)
    
    with open("links.txt", "w") as file:
        for link in valid_links:
            file.write(link + "\n")
    
    return valid_links

def scrape_webpage(url, visited):
    """Scrape content from a single webpage and return structured sections."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    sections = []  # List to hold structured documentation data
    current_section = None

    for tag in soup.find_all(["h1", "h2", "h3", "p", "pre", "code"]):
        text = tag.get_text().strip()
        if not text:
            continue

        if tag.name in ["h1", "h2", "h3"]:
            if current_section:
                sections.append(current_section)
            current_section = {"title": text, "content": [], "code": []}
        elif tag.name == "p" and current_section:
            current_section["content"].append(text)
        elif tag.name in ["pre", "code"] and current_section:
            current_section["code"].append(text)

    if current_section:
        sections.append(current_section)
    
    return sections, get_valid_links(soup, url, visited)

def scrape_full_documentation(start_url):
    """Crawl all relevant documentation pages and save structured data."""
    visited = set()
    queue = deque([start_url])
    all_sections = []
    
    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        print(f"🔎 Scraping: {url}")
        visited.add(url)
        
        try:
            sections, new_links = scrape_webpage(url, visited)
            all_sections.extend(sections)
            queue.extend(new_links - visited)  # Add only unvisited links
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
    
    with open("structured_docs.json", "w", encoding="utf-8") as file:
        json.dump(all_sections, file, indent=4, ensure_ascii=False)
    
    print("✅ Scraping complete! Data saved to 'structured_docs.json'.")
    return all_sections

# Example usage
start_url = "https://requests.readthedocs.io/en/latest/"
scrape_full_documentation(start_url)
