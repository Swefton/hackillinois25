import importlib.util
import requests

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
        urls = info.get('project_urls', {})
        # Check common documentation keys
        for key in ['Documentation', 'Docs', 'documentation']:
            if key in urls and urls[key]:
                return urls[key]
        # Check standalone docs_url or homepage fields
        docs_url = info.get('docs_url')
        if docs_url:
            return docs_url
        if 'Home' in urls and urls['Home']:
            return urls['Home']
        return info.get('home_page')
    return None

def get_python_doc_url(library_name):
    if is_builtin(library_name):
        return get_builtin_doc_url(library_name)
    else:
        doc_url = get_pypi_doc_url(library_name)
        return doc_url if doc_url else f"Documentation not found for '{library_name}'."

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

    if ecosystem == 'python':
        print("Documentation URL:", get_python_doc_url(library_name))
    elif ecosystem == 'node':
        doc_url = get_npm_doc_url(library_name)
        print("Documentation URL:", doc_url if doc_url else f"Documentation not found for '{library_name}'.")
    elif ecosystem == 'ruby':
        doc_url = get_rubygems_doc_url(library_name)
        print("Documentation URL:", doc_url if doc_url else f"Documentation not found for '{library_name}'.")
    elif ecosystem == 'php':
        doc_url = get_packagist_doc_url(library_name)
        print("Documentation URL:", doc_url if doc_url else f"Documentation not found for '{library_name}'.")
    elif ecosystem == 'maven':
        doc_url = get_maven_doc_url(library_name)
        print("Documentation URL:", doc_url if doc_url else f"Documentation not found for '{library_name}'.")
    elif ecosystem == 'nuget':
        doc_url = get_nuget_doc_url(library_name)
        print("Documentation URL:", doc_url if doc_url else f"Documentation not found for '{library_name}'.")
    elif ecosystem == 'go':
        print("Documentation URL:", get_go_doc_url(library_name))
    elif ecosystem == 'rust':
        doc_url = get_rust_doc_url(library_name)
        print("Documentation URL:", doc_url if doc_url else f"Documentation not found for '{library_name}'.")
    else:
        print("Ecosystem not supported.")

if __name__ == "__main__":
    main()

