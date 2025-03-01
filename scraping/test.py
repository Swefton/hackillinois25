import requests
from bs4 import BeautifulSoup
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

# Example usage
start_url = "https://requests.readthedocs.io/en/latest/"
all_links = fetch_all_links(start_url)

# Print all links
for link in all_links:
    print(link)
