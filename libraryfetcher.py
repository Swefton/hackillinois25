import importlib.util
import requests
import re

def extract_top_level_modules(import_line):
    """
    Parses Python import statements to figure out the
    top-level package name(s). Examples:
      - from sentence_transformers import SentenceTransformer
      - from x.y.z import stuff
      - import csv
      - import os, re
      - import bs4 as soup
      - import foo.bar as baz
      - from .some_local_module import example
    Returns a list of root packages, e.g. ["sentence_transformers"], ["os", "re"], ["some_local_module"].
    """
    import_line = import_line.strip()

    # Case: from <something> import ...
    if import_line.startswith("from "):
        # Example: "from sentence_transformers.something import SentenceTransformer"
        match = re.match(r"^from\s+([a-zA-Z0-9_\.]+)\s+import\s+.*", import_line)
        if match:
            module_part = match.group(1)
            # Strip leading dots in case of relative import: ".foo" -> "foo"
            module_part = module_part.lstrip('.')
            # e.g. "sentence_transformers.something" -> "sentence_transformers"
            root_name = module_part.split('.')[0]
            return [root_name]
        return []

    # Case: import <library>, <library2>
    if import_line.startswith("import "):
        # Everything after "import "
        rest = import_line[7:].strip()
        # Could be "bs4 as soup, os, re"
        # so split by commas first
        chunks = [c.strip() for c in rest.split(',')]
        root_list = []
        for chunk in chunks:
            # chunk could be "bs4 as soup" or "x.y.z as alias"
            # we only want the base name "bs4" or "x"
            first_token = chunk.split()[0]     # e.g. "bs4", "x.y.z"
            first_token = first_token.lstrip('.')  # remove leading dots if any
            root_list.append(first_token.split('.')[0])
        return root_list

    return []


# ------------------------------------
# 2) Simple “library name → doc link” 
#    logic (Python-only example).
# ------------------------------------
STANDARD_LIBRARY = {
    # Add whichever stdlib modules you want recognized
    "os", "json", "re", "csv", "xml", "sys", "math", "time"
}

ALIASES = {
    # Modules whose PyPI name differs from the import name
    "bs4": "beautifulsoup4",
}

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
        # Try 'Documentation', 'Docs', etc., then docs_url, then homepage
        project_urls = info.get('project_urls') or {}
        for key in ['Documentation', 'Docs', 'documentation']:
            if key in project_urls and project_urls[key]:
                return project_urls[key]
        if info.get('docs_url'):
            return info.get('docs_url')
        if 'Home' in project_urls and project_urls['Home']:
            return project_urls['Home']
        return info.get('home_page')
    return None

def get_python_doc_url(library_name):
    # If it's truly built-in (like 'sys', 'time')
    if is_builtin(library_name):
        return get_builtin_doc_url(library_name)

    # If it's in our standard library set
    if library_name in STANDARD_LIBRARY:
        return f"https://docs.python.org/3/library/{library_name}.html"

    # If there's a known alias (bs4 -> beautifulsoup4)
    library_name = ALIASES.get(library_name, library_name)

    # Check PyPI metadata
    doc_url = get_pypi_doc_url(library_name)
    if doc_url:
        return doc_url

    return None

# =============================
# Node.js (npm) Ecosystem Functions
# =============================
def get_npm_doc_url(library_name):
    url = f"https://registry.npmjs.org/{library_name}"
    response = requests.get(url)
    if response.status_code == 200:
        info = response.json()
        latest = info.get('dist-tags', {}).get('latest')
        if latest:
            version_info = info.get('versions', {}).get(latest, {})
            doc_url = version_info.get('homepage')
            if doc_url:
                return doc_url
            repo = version_info.get('repository', {})
            if isinstance(repo, dict) and repo.get('url'):
                return repo.get('url')
        if info.get('homepage'):
            return info.get('homepage')
    return None

# =============================
# Ruby (RubyGems) Ecosystem Functions
# =============================
def get_rubygems_doc_url(gem_name):
    url = f"https://rubygems.org/api/v1/gems/{gem_name}.json"
    response = requests.get(url)
    if response.status_code == 200:
        info = response.json()
        if info.get('documentation_uri'):
            return info['documentation_uri']
        elif info.get('homepage_uri'):
            return info['homepage_uri']
    return None

# =============================
# PHP (Packagist) Ecosystem Functions
# =============================
def get_packagist_doc_url(package_name):
    url = f"https://repo.packagist.org/p/{package_name}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        packages = data.get('packages', {}).get(package_name, {})
        if packages:
            # Choose the latest version (sorting keys in reverse order)
            versions = sorted(packages.keys(), reverse=True)
            for version in versions:
                info = packages[version]
                if 'homepage' in info and info['homepage']:
                    return info['homepage']
                elif 'repository' in info and info['repository']:
                    return info['repository']
    return None

# =============================
# Java (Maven Central) Ecosystem Functions
# =============================
def get_maven_doc_url(library_name):
    # Expect library_name in the format "groupId:artifactId"
    try:
        groupId, artifactId = library_name.split(':')
    except Exception:
        return "Invalid format for Maven library. Use 'groupId:artifactId'."
    url = f"https://search.maven.org/solrsearch/select?q=g:\"{groupId}\"+AND+a:\"{artifactId}\"&rows=1&wt=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        docs = data.get('response', {}).get('docs', [])
        if docs:
            # If available, return homepage; otherwise, fallback to the Maven Central project page
            if 'homepage' in docs[0] and docs[0]['homepage']:
                return docs[0]['homepage']
            else:
                return f"https://search.maven.org/artifact/{groupId}/{artifactId}"
    return None

# =============================
# .NET (NuGet) Ecosystem Functions
# =============================
def get_nuget_doc_url(library_name):
    # library_name is the package ID, e.g. Newtonsoft.Json
    url = f"https://api.nuget.org/v3/registration5-semver1/{library_name.lower()}/index.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        if items:
            first_item = items[0]
            sub_items = first_item.get('items', [])
            if sub_items:
                catalog_entry = sub_items[0].get('catalogEntry', {})
                project_url = catalog_entry.get('projectUrl')
                if project_url:
                    return project_url
    return None

# =============================
# Go Ecosystem Functions
# =============================
def get_go_doc_url(library_name):
    # For Go libraries, assume the input is the package's import path.
    return f"https://pkg.go.dev/{library_name}"

# =============================
# Rust (crates.io) Ecosystem Functions
# =============================
def get_rust_doc_url(library_name):
    url = f"https://crates.io/api/v1/crates/{library_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        crate = data.get('crate', {})
        if crate.get('documentation'):
            return crate['documentation']
        elif crate.get('homepage'):
            return crate['homepage']
        elif crate.get('repository'):
            return crate['repository']
    return None

# =============================
# Main Program
# =============================
def main():
    print("Supported ecosystems: python, node, ruby, php, maven, nuget, go, rust")
    ecosystem = input("Enter ecosystem: ").strip().lower()
    library_name = input("Enter the library name (or coordinates for maven, e.g. groupId:artifactId): ").strip()

    doc_url = None
    if ecosystem == 'python':
        doc_url = get_python_doc_url(library_name)
    elif ecosystem == 'node':
        doc_url = get_npm_doc_url(library_name)
    elif ecosystem == 'ruby':
        doc_url = get_rubygems_doc_url(library_name)
    elif ecosystem == 'php':
        doc_url = get_packagist_doc_url(library_name)
    elif ecosystem == 'maven':
        doc_url = get_maven_doc_url(library_name)
    elif ecosystem == 'nuget':
        doc_url = get_nuget_doc_url(library_name)
    elif ecosystem == 'go':
        doc_url = get_go_doc_url(library_name)
    elif ecosystem == 'rust':
        doc_url = get_rust_doc_url(library_name)
    else:
        print("Ecosystem not supported.")
        return

    if doc_url:
        print("Documentation URL:", doc_url)
    else:
        print(f"Documentation not found for '{library_name}' in the {ecosystem} ecosystem.")

if __name__ == "__main__":
    main()
