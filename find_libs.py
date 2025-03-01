import os
import re
import requests
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from urllib.parse import urljoin

# List of standard library modules
STANDARD_LIBS = set(sys.stdlib_module_names)

def find_python_libraries(directory="."):
    """Find top-level Python libraries in a project."""
    libs = set()
    pattern = re.compile(r'^\s*(?:import|from)\s+(\w+)')

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # Skip hidden dirs
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                        libs.update(match.group(1) for line in f if (match := pattern.match(line)))
                except:
                    pass

    # Exclude standard library modules
    return sorted(libs - STANDARD_LIBS)

@lru_cache(maxsize=None)
def get_docs_link(lib_name):
    """Get the documentation link for a library dynamically."""
    # Known documentation URLs for popular libraries
    known_docs = {
        "bs4": "https://www.crummy.com/software/BeautifulSoup/bs4/doc/",
        "numpy": "https://numpy.org/doc/",
    }

    # Return known documentation URLs if available
    if lib_name in known_docs:
        return known_docs[lib_name]

    # Fetch documentation URL from PyPI
    url = f"https://pypi.org/pypi/{lib_name}/json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        info = data.get("info", {})
        project_urls = info.get("project_urls", {}) or {}  # Ensure project_urls is a dictionary
        home_page = info.get("home_page", "")

        # Check for the "Documentation" key in project_urls
        if isinstance(project_urls, dict) and "Documentation" in project_urls:
            return project_urls["Documentation"]

        # Check for common documentation patterns in project_urls
        if isinstance(project_urls, dict):
            for key, value in project_urls.items():
                if "readthedocs" in value or "docs" in key.lower():
                    return value

        # Check if the home page contains documentation
        if home_page and ("readthedocs" in home_page or "docs" in home_page):
            return home_page

        # Fallback to GitHub/GitLab repository
        repo_url = project_urls.get("Source", "") or project_urls.get("Repository", "")
        if repo_url:
            if "github.com" in repo_url:
                return urljoin(repo_url, "blob/main/README.md")
            elif "gitlab.com" in repo_url:
                return urljoin(repo_url, "-/blob/main/README.md")

        # Fallback to PyPI home page
        if home_page:
            return home_page

        # If no documentation or home page is found, return a default message
        return "No documentation found"

    except requests.RequestException:
        return "Library not found"

def get_docs_links(libraries):
    """Get documentation links for multiple libraries in parallel."""
    with ThreadPoolExecutor() as executor:
        docs_links = dict(zip(libraries, executor.map(get_docs_link, libraries)))
    return docs_links

if __name__ == "__main__":
    libs = find_python_libraries()
    print(libs)
    
    docs_links = get_docs_links(libs)
    print(docs_links)