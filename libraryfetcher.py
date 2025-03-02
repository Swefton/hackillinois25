import importlib.util
import requests
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from rapidfuzz import process, fuzz  # pip install rapidfuzz

# =============================
# Utility: Get a Candidate Pool from Popular Packages
# =============================
def get_candidate_pool():
    # Download a list of top PyPI packages from Hugovk’s Top PyPI Packages (30-day list)
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # "rows" is a list of dictionaries with a "project" key.
        candidate_packages = [row['project'] for row in data.get('rows', [])]
        return candidate_packages
    except Exception as e:
        print("Error retrieving candidate pool:", e)
        return []

# =============================
# Python Ecosystem Functions
# =============================
def is_builtin(library_name):
    spec = importlib.util.find_spec(library_name)
    return spec is not None and spec.origin == 'built-in'

def get_builtin_doc_url(library_name):
    return f"https://docs.python.org/3/library/{library_name}.html"

def get_pypi_doc_url(library_name):
    url = f"https://pypi.org/pypi/{library_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        info = response.json().get('info', {})
        urls = info.get('project_urls') or {}
        # Look through keys (case-insensitively) for documentation info.
        for key, value in urls.items():
            if key.lower() in ['documentation', 'docs'] and value:
                return value
        if info.get('docs_url'):
            return info.get('docs_url')
        if info.get('home_page'):
            return info.get('home_page')
    return None

def get_python_doc_url(library_name):
    if is_builtin(library_name):
        return get_builtin_doc_url(library_name)
    else:
        return get_pypi_doc_url(library_name)

# Use BeautifulSoup to scrape PyPI search results for package names.
def scrape_pypi_search(user_input):
    search_url = f"https://pypi.org/search/?q={user_input}"
    response = requests.get(search_url)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('a', class_='package-snippet')
    package_names = []
    for result in results:
        name_tag = result.find('span', class_='package-snippet__name')
        if name_tag:
            package_names.append(name_tag.text.strip())
    return package_names

# Combine candidate pool from popular packages and scraped packages,
# then use multiple fuzzy scorers with a dynamic cutoff.
def search_best_pypi_match(user_input):
    # Use a lower cutoff for very short inputs.
    cutoff = 20 if len(user_input) < 5 else 40

    candidate_pool = get_candidate_pool()
    scraped_candidates = scrape_pypi_search(user_input)
    # Combine and remove duplicates.
    candidates = list(set(candidate_pool + scraped_candidates))
    if not candidates:
        return None

    # Try a simple substring match first.
    for pkg in candidates:
        if user_input.lower() in pkg.lower():
            return pkg

    # Try several scorers.
    scorers = [fuzz.partial_ratio, fuzz.token_set_ratio, fuzz.ratio]
    best_match = None
    best_score = 0
    for scorer in scorers:
        result = process.extractOne(
            user_input,
            candidates,
            scorer=scorer,
            score_cutoff=cutoff
        )
        if result:
            match, score, _ = result
            if score > best_score:
                best_score = score
                best_match = match
    return best_match

# =============================
# Main Program
# =============================
def main():
    print("Supported ecosystems: python, node, ruby, php, maven, nuget, go, rust")
    ecosystem = input("Enter ecosystem: ").strip().lower()
    library_name = input("Enter the library name (or coordinates for maven, e.g. groupId:artifactId): ").strip()
    
    if ecosystem == 'python':
        # Minimal fallback mapping for ambiguous short inputs.
        fallback_map = {
            "opencv": "opencv-python",
            "opencv-python": "opencv-python",
            "pd": "pandas",
            "bs4": "beautifulsoup"
        }
        # Check if the user input is in our fallback map.
        if library_name.lower() in fallback_map:
            print(f"Falling back to known package name for '{library_name}'.")
            library_name = fallback_map[library_name.lower()]
        
        # First, try using the (possibly remapped) name directly.
        doc_url = get_python_doc_url(library_name)
        if not doc_url:
            print(f"No documentation found for '{library_name}'. Attempting to find a close match...")
            best_match = search_best_pypi_match(library_name)
            if best_match and best_match.lower() != library_name.lower():
                print(f"Did you mean '{best_match}'?")
                library_name = best_match
                doc_url = get_python_doc_url(library_name)
        
        # Minimal fallback for known exceptions (e.g., opencv fallback already handled in fallback_map).
        if not doc_url and library_name.lower() in fallback_map:
            library_name = fallback_map[library_name.lower()]
            doc_url = get_python_doc_url(library_name)
    else:
        print("Ecosystem not supported in this example.")
        return

    if doc_url:
        print("Documentation URL:", doc_url)
    else:
        print(f"Documentation not found for '{library_name}' in the {ecosystem} ecosystem.")

if __name__ == "__main__":
    main()
