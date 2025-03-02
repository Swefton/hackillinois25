import os
import re
import csv
import requests
import importlib.util
import sys
import xml.etree.ElementTree as ET

# =========================================
# Part 1: Scanning libraries for each language
# =========================================

def find_python_libraries(directory="."):
    """Find all top-level Python libraries imported in a project."""
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

def find_node_libraries(directory="."):
    """Find Node libraries by scanning .js files."""
    libraries = set()
    require_pattern = re.compile(r"require\(['\"]([^'\"]+)['\"]\)")
    import_pattern = re.compile(r"import\s+(?:.*\s+from\s+)?['\"]([^'\"]+)['\"]")
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".js"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        for pattern in (require_pattern, import_pattern):
                            matches = pattern.findall(content)
                            for match in matches:
                                libraries.add(match)
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")
    return sorted(libraries)

def find_ruby_libraries(directory="."):
    """Find Ruby libraries by scanning .rb files."""
    libraries = set()
    require_pattern = re.compile(r"^\s*require\s+['\"]([^'\"]+)['\"]")
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".rb"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            match = require_pattern.match(line)
                            if match:
                                libraries.add(match.group(1))
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")
    return sorted(libraries)

def find_php_libraries(directory="."):
    """Find PHP libraries by scanning .php files."""
    libraries = set()
    pattern = re.compile(r"^\s*(?:require|include)(?:_once)?\s+['\"]([^'\"]+)['\"]")
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".php"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            match = pattern.match(line)
                            if match:
                                libraries.add(match.group(1))
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")
    return sorted(libraries)

def find_maven_libraries(directory="."):
    """Find Maven libraries by parsing pom.xml."""
    libraries = set()
    pom_path = os.path.join(directory, "pom.xml")
    if os.path.isfile(pom_path):
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            for dependency in root.findall(".//m:dependency", ns):
                groupId = dependency.find("m:groupId", ns)
                artifactId = dependency.find("m:artifactId", ns)
                if groupId is not None and artifactId is not None:
                    libraries.add(f"{groupId.text}:{artifactId.text}")
        except Exception as e:
            print(f"Error parsing pom.xml: {e}")
    return sorted(libraries)

def find_nuget_libraries(directory="."):
    """Find NuGet libraries by scanning .csproj files."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".csproj"):
                file_path = os.path.join(root, file)
                try:
                    tree = ET.parse(file_path)
                    root_elem = tree.getroot()
                    for package in root_elem.findall(".//PackageReference"):
                        include_attr = package.attrib.get("Include")
                        if include_attr:
                            libraries.add(include_attr)
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")
    return sorted(libraries)

def find_go_libraries(directory="."):
    """Find Go libraries by scanning .go files for import statements."""
    libraries = set()
    import_pattern = re.compile(r'import\s+"([^"]+)"')
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".go"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            match = import_pattern.search(line)
                            if match:
                                libraries.add(match.group(1))
                except Exception as e:
                    print(f"Skipping {file_path} due to error: {e}")
    return sorted(libraries)

def find_rust_libraries(directory="."):
    """Find Rust libraries by reading Cargo.toml dependencies."""
    libraries = set()
    cargo_path = os.path.join(directory, "Cargo.toml")
    if os.path.isfile(cargo_path):
        try:
            with open(cargo_path, "r", encoding="utf-8") as f:
                in_dependencies = False
                for line in f:
                    line = line.strip()
                    if line.startswith("[dependencies]"):
                        in_dependencies = True
                        continue
                    if in_dependencies:
                        if line.startswith("["):
                            in_dependencies = False
                        elif line and "=" in line:
                            lib = line.split("=")[0].strip()
                            libraries.add(lib)
        except Exception as e:
            print(f"Error reading Cargo.toml: {e}")
    return sorted(libraries)

# =========================================
# Part 2: Functions to determine documentation URLs
# =========================================

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
    an official documentation link.
    """
    url = f"https://pypi.org/pypi/{library_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        info = response.json().get('info', {})
        urls = info.get('project_urls') or {}  # use empty dict if None
        for key in ['Documentation', 'Docs', 'documentation']:
            if key in urls and urls[key]:
                return urls[key]
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

# =========================================
# Part 3: Load common libraries CSV for a given language
# =========================================

def load_common_libraries(language, base_dir="."):
    common_libs_map = {}
    csv_filename = f"{language}_common_libraries.csv"
    csv_path = os.path.join(base_dir, csv_filename)
    if os.path.isfile(csv_path):
        try:
            with open(csv_path, mode="r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    if row[0] is None or row[1] is None:
                        continue
                    lib_name, doc_link = row[0].strip(), row[1].strip()
                    if lib_name and doc_link:
                        common_libs_map[lib_name] = doc_link
        except Exception as e:
            print(f"Warning: Error while reading '{csv_path}': {e}")
    else:
        print(f"Note: '{csv_filename}' not found. Will only fetch from external sources.")
    return common_libs_map

# =========================================
# Part 4: Main workflow
# =========================================

def main():
    # Determine language from command-line argument (default: python)
    language = "python"
    if len(sys.argv) > 1:
        language = sys.argv[1].lower()
    
    # Mapping of languages to their scanning and documentation functions
    SCAN_FUNCTIONS = {
        'python': find_python_libraries,
        'node': find_node_libraries,
        'ruby': find_ruby_libraries,
        'php': find_php_libraries,
        'maven': find_maven_libraries,
        'nuget': find_nuget_libraries,
        'go': find_go_libraries,
        'rust': find_rust_libraries,
    }
    
    DOC_FUNCTIONS = {
        'python': get_python_doc_url,
        'node': get_npm_doc_url,
        'ruby': get_rubygems_doc_url,
        'php': get_packagist_doc_url,
        'maven': get_maven_doc_url,
        'nuget': get_nuget_doc_url,
        'go': get_go_doc_url,
        'rust': get_rust_doc_url,
    }
    
    if language not in SCAN_FUNCTIONS or language not in DOC_FUNCTIONS:
        print(f"Language '{language}' is not supported.")
        return
    
    print(f"Scanning for {language} libraries...")
    common_libs_map = load_common_libraries(language)
    libs = SCAN_FUNCTIONS[language]()
    if not libs:
        print(f"No {language} libraries found.")
        return
    
    print(f"{language.capitalize()} libraries found:")
    for lib in libs:
        print(f" - {lib}")
    
    results = []
    for lib in libs:
        if lib in common_libs_map:
            doc_url = common_libs_map[lib]
        else:
            doc_url = DOC_FUNCTIONS[language](lib)
            if not doc_url:
                doc_url = f"Documentation not found for '{lib}'."
        results.append((lib, doc_url))
    
    out_path = f"output_{language}.csv"
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
