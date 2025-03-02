import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque

def get_valid_links(soup, base_url, visited):
    """Extract and normalize valid documentation links from a page."""
    valid_links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        full_url = urljoin(base_url, href)
        full_url, _ = urldefrag(full_url)  # Remove fragment identifiers
        parsed_url = urlparse(full_url)
        
        # Ensure it's within the same domain and not visited
        if parsed_url.netloc == urlparse(base_url).netloc and full_url not in visited:
            if "search" not in parsed_url.path:  # Fragment is already removed
                print("adding", full_url)
                valid_links.add(full_url)
    
    return valid_links

def fetch_all_links(start_url):
    """Crawl documentation pages and retrieve all relevant links."""
    visited = set()
    queue = deque([start_url])
    all_links = set()
    
    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            new_links = get_valid_links(soup, url, visited)
            all_links.update(new_links)
            queue.extend(new_links - visited)  # Add only unvisited links
        except Exception as e:
            pass
        
    return all_links


def scrape_webpage(url):
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
    
    return sections

def scrape_full_documentation(start_url):
    """Crawl all relevant documentation pages and save structured data."""
    
    all_links = fetch_all_links(start_url)

    for index in range(len(all_links)):
        print(f"scraping {index}/{len(all_links)}") 

    all_sections = list()
     
    for url in all_links:
        print(f"🔎 Scraping: {url}")
        
        try:
            sections = scrape_webpage(url)
            all_sections.extend(sections)
        
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
    
    with open("structured_docs.json", "w", encoding="utf-8") as file:
        json.dump(all_sections, file, indent=4, ensure_ascii=False)
    
    print("✅ Scraping complete! Data saved to 'structured_docs.json'.")
    return all_sections

# Example usage
start_url = "https://docs.pycord.dev/en/stable/api/index.html"
scrape_full_documentation(start_url)
