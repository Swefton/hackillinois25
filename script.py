import os
import re
import csv
import requests
import importlib.util

# (Optional) Only needed if you actually parse HTML somewhere
# from bs4 import BeautifulSoup

# =========================================
# Part 1: Finding Python libraries in code
# =========================================
def find_python_libraries(directory="."):
    """Find all top-level Python libraries imported in a project, skipping hidden directories."""
    libraries = set()
    import_pattern = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)')

    for root, dirs, files in os.walk(directory):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            match = import_pattern.match(line)
                            if match:
                                libraries.add(match.group(1))
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")

    return sorted(libraries)

# =======================================================
# Part 2: Functions to determine documentation URLs
# =======================================================
def is_builtin(library_name):
    """Check if a library is a built-in Python library."""
    spec = importlib.util.find_spec(library_name)
    return spec is not None and spec.origin == 'built-in'

def get_builtin_doc_url(library_name):
    """Get Python built-in library doc URL from docs.python.org."""
    return f"https://docs.python.org/3/library/{library_name}.html"

def get_pypi_doc_url(library_name):
    """
    Query PyPI for a project's JSON metadata and try to find
    an official documentation link (Documentation, Docs, doc_url, homepage, etc.).
    """
    url = f"https://pypi.org/pypi/{library_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        info = response.json().get('info', {})
        urls = info.get('project_urls') or {}  # Use empty dict if None

        # Check common keys in project_urls
        for key in ['Documentation', 'Docs', 'documentation']:
            if key in urls and urls[key]:
                return urls[key]

        # Fallbacks: docs_url, homepage, etc.
        docs_url = info.get('docs_url')
        if docs_url:
            return docs_url
        if 'Home' in urls and urls['Home']:
            return urls['Home']
        return info.get('home_page')
    return None

def get_python_doc_url(library_name):
    """Decide whether to get doc URL for a built-in or PyPI library."""
    if is_builtin(library_name):
        return get_builtin_doc_url(library_name)
    else:
        doc_url = get_pypi_doc_url(library_name)
        if doc_url:
            return doc_url
        else:
            return f"Documentation not found for '{library_name}'."

# (Below are extra ecosystem functions, shown for completeness.)
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

def get_packagist_doc_url(package_name):
    url = f"https://repo.packagist.org/p/{package_name}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        packages = data.get('packages', {}).get(package_name, {})
        if packages:
            versions = sorted(packages.keys(), reverse=True)
            for version in versions:
                info = packages[version]
                if 'homepage' in info and info['homepage']:
                    return info['homepage']
                elif 'repository' in info and info['repository']:
                    return info['repository']
    return None

def get_maven_doc_url(library_name):
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
            if 'homepage' in docs[0] and docs[0]['homepage']:
                return docs[0]['homepage']
            else:
                return f"https://search.maven.org/artifact/{groupId}/{artifactId}"
    return None

def get_nuget_doc_url(library_name):
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

def get_go_doc_url(library_name):
    return f"https://pkg.go.dev/{library_name}"

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

# ==================================================
# Part 3: Main workflow to combine everything
# ==================================================
def main():
    # 1. Find Python libraries by scanning the current directory
    libs = find_python_libraries()
    if not libs:
        print("No Python libraries found.")
        return

    # Print them out for reference
    print("Python libraries found:")
    for lib in libs:
        print(f" - {lib}")

    # 2. Read the common_libs.csv into a dictionary { lib_name: doc_link }
    common_libs_map = {}  # Ensure this is a dict, not None
    csv_path = "common_libs.csv"

    # Attempt to read CSV only if it exists
    if os.path.isfile(csv_path):
        try:
            with open(csv_path, mode="r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    # Skip completely blank or short rows
                    if not row or len(row) < 2:
                        continue
                    # Safely strip them. If they're somehow None, skip
                    if row[0] is None or row[1] is None:
                        continue
                    lib_name, doc_link = row[0].strip(), row[1].strip()
                    # Only add if both library and link are non-empty
                    if lib_name and doc_link:
                        common_libs_map[lib_name] = doc_link
        except Exception as e:
            print(f"Warning: Error while reading '{csv_path}': {e}")
    else:
        print(f"Note: '{csv_path}' not found. Will only fetch from PyPI/built-in docs.")

    # 3. For each library found, decide on the doc link:
    #    - If library is in common_libs.csv, use that link.
    #    - Otherwise, fetch from PyPI or built-in docs.
    results = []
    for lib in libs:
        if lib in common_libs_map:
            doc_url = common_libs_map[lib]
        else:
            doc_url = get_python_doc_url(lib)
        results.append((lib, doc_url))

    # 4. Write the results to output.csv
    out_path = "output.csv"
    try:
        with open(out_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Library", "Documentation Link"])
            for lib_name, doc_link in results:
                writer.writerow([lib_name, doc_link])
        print(f"\nDocumentation links have been written to '{out_path}'.")
    except Exception as e:
        print(f"Error writing to '{out_path}': {e}")

if __name__ == "__main__":
    main()
