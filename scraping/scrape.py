import os
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque, defaultdict
from tqdm import tqdm

# Strategy 1: Heuristic-Based Filtering: inclusion and exclusion keywords.
INCLUSION_KEYWORDS = ['doc', 'guide', 'api', 'reference', 'tutorial']
EXCLUSION_KEYWORDS = ['contribute', 'sponsor', 'changelog', 'issues', 'download']

def get_valid_links(soup, base_url, visited):
    """Extract and normalize valid documentation links from a page using heuristics."""
    valid_links = set()
    for a_tag in soup.find_all("a", href=True):
        anchor_text = a_tag.get_text().strip().lower()
        href = a_tag["href"].strip()
        full_url = urljoin(base_url, href)
        full_url, _ = urldefrag(full_url)  # Remove fragment identifiers
        parsed_url = urlparse(full_url)

        # Only consider URLs in the same domain and not already visited.
        if parsed_url.netloc == urlparse(base_url).netloc and full_url not in visited:
            path_lower = parsed_url.path.lower()

            # Exclude links with any exclusion keyword.
            if any(kw in path_lower for kw in EXCLUSION_KEYWORDS):
                continue

            # Only add if the URL path or anchor text contains an inclusion keyword.
            if any(kw in path_lower for kw in INCLUSION_KEYWORDS) or any(kw in anchor_text for kw in INCLUSION_KEYWORDS):
                valid_links.add(full_url)
    return valid_links

def fetch_all_links(start_url, name, max_depth=3):
    """
    Crawl documentation pages starting at start_url.
    Build a tree view of the pages and return both the set of URLs and the tree.
    """
    visited = set()
    tree = defaultdict(list)  # key: parent URL, value: list of child URLs
    queue = deque([(start_url, None, 0)])  # (current URL, parent URL, current depth)
    all_links = set([start_url])
    
    print(f"Indexing {name}")
    
    while queue:
        url, parent, depth = queue.popleft()
        if url in visited or depth > max_depth:
            continue
        visited.add(url)
        
        # Build tree: assign as child to its parent if available.
        if parent:
            tree[parent].append(url)
        else:
            tree[url]  # ensure root is present

        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            new_links = get_valid_links(soup, url, visited)
            for link in new_links:
                all_links.add(link)
                queue.append((link, url, depth + 1))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

    return all_links, tree

# Strategy 2: Simple Content Analysis: check page content length.
def scrape_webpage(url):
    """Scrape content from a single webpage and return structured sections."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
        return None

    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.extract()

    # Simple content analysis: if the page doesn't have enough text, skip it.
    full_text = soup.get_text(separator=" ", strip=True)
    if len(full_text) < 200:
        print(f"Skipping {url}: insufficient content.")
        return None

    sections = []  # List to hold structured documentation data
    current_section = None

    # Extract headings and paragraphs, grouping content under headings.
    for tag in soup.find_all(["h1", "h2", "h3", "p", "pre", "code"]):
        text = tag.get_text().strip()
        if not text:
            continue

        if tag.name in ["h1", "h2", "h3"]:
            if current_section:
                sections.append(current_section)
            current_section = {"title": text, "content": [], "code": [], "url": url}
        elif tag.name == "p" and current_section:
            current_section["content"].append(text)
        elif tag.name in ["pre", "code"] and current_section:
            current_section["code"].append(text)

    if current_section:
        sections.append(current_section)
    
    return sections

def scrape_full_documentation(start_url, library_name, directory):
    """Crawl all relevant documentation pages, build a tree view, and cache structured data inside .alexandria."""
    
    # Ensure the .alexandria folder exists
    alexandria_path = os.path.join(directory, ".alexandria")
    if not os.path.exists(alexandria_path):
        print(f"❌ Error: The .alexandria directory is missing in {directory}. Run 'alexandria init' first.")
        return None, None
    
    # Define the vectordb folder inside .alexandria
    vectordb_path = os.path.join(alexandria_path, "vectordb", library_name)
    
    # Ensure the library-specific cache directory exists
    os.makedirs(vectordb_path, exist_ok=True)

    # Fetch links and scrape documentation
    all_links, tree = fetch_all_links(start_url, library_name)
    print(f"Total unique documentation pages found: {len(all_links)}")

    all_sections = []
    
    for index, url in enumerate(tqdm(all_links, desc="🔎 Scraping Progress", unit="page")):
        try:
            sections = scrape_webpage(url)
            if sections:
                all_sections.extend(sections)
        except Exception as e:
            print(f"\n❌ Failed to scrape {url}: {e}")
    
    # Save structured documentation data inside .alexandria/vectordb/
    structured_docs_path = os.path.join(vectordb_path, "structured_docs.json")
    with open(structured_docs_path, "w", encoding="utf-8") as file:
        json.dump(all_sections, file, indent=4, ensure_ascii=False)
    
    # Save the tree view
    doc_tree_path = os.path.join(vectordb_path, "doc_tree.json")
    with open(doc_tree_path, "w", encoding="utf-8") as file:
        json.dump(tree, file, indent=4, ensure_ascii=False)
    
    print(f"✅ Scraping complete!") 
    
    return all_sections, tree


# Example usage:
if __name__ == "__main__":
    start_url = "https://docs.pycord.dev/en/stable/"
    sections, tree = scrape_full_documentation(start_url)