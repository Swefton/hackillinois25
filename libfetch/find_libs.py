import os
import re
import json
import xml.etree.ElementTree as ET

# Optional: known import-name-to-PyPI-name mapping
ALIAS_MAP = {
    "bs4": "beautifulsoup",
    # Add others as needed
}

def parse_import_line(line):
    """
    Parse a single line of Python code looking for import statements.
    Return a set of top-level library names discovered.
    """
    libraries = set()

    # Remove inline comments to avoid confusion, e.g., "import foo  # comment"
    if "#" in line:
        line = line.split("#", 1)[0]
    line = line.strip()

    # Regex patterns to capture multiple forms of imports
    # Examples of matches we want to handle:
    #   import foo
    #   import foo, bar
    #   import foo as f, bar
    #   from foo import something
    #   from foo.bar import something
    #   from foo.bar.baz import something as x
    #   import foo.bar
    import_pattern = r'^\s*import\s+(.*)'
    from_pattern = r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+(.*)'

    # Case 1: "import ..."
    m_import = re.match(import_pattern, line)
    if m_import:
        # Everything after "import"
        remainder = m_import.group(1)
        # Split on commas, e.g. "foo as f, bar" → ["foo as f", " bar"]
        chunks = remainder.split(',')
        for chunk in chunks:
            chunk = chunk.strip()
            # Remove " as alias" if present, e.g. "foo as f" → "foo"
            chunk = chunk.split()[0]  # because chunk might be "foo" or "foo as something"
            # Strip off submodules: "foo.bar" → "foo"
            top_level = chunk.split('.', 1)[0]
            # Map known aliases if needed
            if top_level in ALIAS_MAP:
                top_level = ALIAS_MAP[top_level]
            libraries.add(top_level)
        return libraries

    # Case 2: "from foo import ..."
    m_from = re.match(from_pattern, line)
    if m_from:
        # The group(1) is the part after 'from' and before 'import'
        top_level = m_from.group(1).split('.', 1)[0]
        if top_level in ALIAS_MAP:
            top_level = ALIAS_MAP[top_level]
        libraries.add(top_level)
        return libraries

    return libraries

def find_python_libraries(directory="."):
    """
    Scan .py files for Python imports, handling:
      - import foo, bar as b
      - from foo.bar import baz
      - multiple imports on one line
      - aliases
      - submodules
    """
    libraries = set()
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            found = parse_import_line(line)
                            libraries.update(found)
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")
    return libraries

def find_node_libraries(directory="."):
    """Find Node libraries by parsing package.json files while skipping node_modules and hidden directories."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        if "package.json" in files:
            file_path = os.path.join(root, "package.json")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    # Only use production dependencies
                    deps = data.get("dependencies", {})
                    libraries.update(deps.keys())
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return libraries

def find_ruby_libraries(directory="."):
    """Find Ruby libraries by scanning Gemfile entries."""
    libraries = set()
    gem_pattern = re.compile(r'^\s*gem\s+[\'"]([^\'"]+)[\'"]')
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "Gemfile" in files:
            file_path = os.path.join(root, "Gemfile")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        match = gem_pattern.match(line)
                        if match:
                            libraries.add(match.group(1))
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return libraries

def find_php_libraries(directory="."):
    """Find PHP libraries by parsing composer.json files."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "composer.json" in files:
            file_path = os.path.join(root, "composer.json")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    for key in ["require", "require-dev"]:
                        deps = data.get(key, {})
                        libraries.update(deps.keys())
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return libraries

def find_maven_libraries(directory="."):
    """Find Maven libraries by parsing pom.xml files."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "pom.xml" in files:
            file_path = os.path.join(root, "pom.xml")
            try:
                tree = ET.parse(file_path)
                root_elem = tree.getroot()
                # Look for all dependency elements
                for dependency in root_elem.findall('.//dependency'):
                    groupId = dependency.find('groupId')
                    artifactId = dependency.find('artifactId')
                    if groupId is not None and artifactId is not None:
                        lib = f"{groupId.text}:{artifactId.text}"
                        libraries.add(lib)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return libraries

def find_nuget_libraries(directory="."):
    """Find NuGet libraries by parsing .csproj and packages.config files."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".csproj"):
                file_path = os.path.join(root, file)
                try:
                    tree = ET.parse(file_path)
                    root_elem = tree.getroot()
                    # Find PackageReference elements (handle possible namespaces)
                    for pr in root_elem.findall(".//{*}PackageReference"):
                        include = pr.attrib.get("Include")
                        if include:
                            libraries.add(include)
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")
            elif file == "packages.config":
                file_path = os.path.join(root, file)
                try:
                    tree = ET.parse(file_path)
                    root_elem = tree.getroot()
                    for pkg in root_elem.findall("package"):
                        pkg_id = pkg.attrib.get("id")
                        if pkg_id:
                            libraries.add(pkg_id)
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")
    return libraries

def find_go_libraries(directory="."):
    """Find Go libraries by parsing go.mod files."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "go.mod" in files:
            file_path = os.path.join(root, "go.mod")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    in_require_block = False
                    for line in f:
                        line = line.strip()
                        if line.startswith("require ("):
                            in_require_block = True
                            continue
                        if in_require_block:
                            if line == ")":
                                in_require_block = False
                            else:
                                parts = line.split()
                                if parts:
                                    libraries.add(parts[0])
                        else:
                            if line.startswith("require"):
                                parts = line.split()
                                if len(parts) >= 2:
                                    libraries.add(parts[1])
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return libraries

def find_rust_libraries(directory="."):
    """Find Rust libraries by scanning Cargo.toml files for dependencies."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "Cargo.toml" in files:
            file_path = os.path.join(root, "Cargo.toml")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    in_dependencies = False
                    for line in f:
                        line = line.strip()
                        # Start of dependencies block
                        if line.startswith("[dependencies]"):
                            in_dependencies = True
                            continue
                        # End of dependencies block if a new section starts
                        if line.startswith("[") and in_dependencies:
                            in_dependencies = False
                        if in_dependencies and line and not line.startswith("#"):
                            # Expecting format: library_name = "version" or similar
                            parts = line.split("=")
                            if parts:
                                lib_name = parts[0].strip().strip('"').strip("'")
                                libraries.add(lib_name)
            except Exception as e:
                print(f"Skipping {file_path}: {e}")
    return libraries

def main():
    language_scanners = {
        "Python": find_python_libraries,
        "Node": find_node_libraries,
        "Ruby": find_ruby_libraries,
        "PHP": find_php_libraries,
        "Maven": find_maven_libraries,
        "NuGet": find_nuget_libraries,
        "Go": find_go_libraries,
        "Rust": find_rust_libraries,
    }
    
    for lang, finder in language_scanners.items():
        libs = finder()
        if libs:
            print(f"{lang} libraries found:")
            for lib in sorted(libs):
                print(f"- {lib}")
        else:
            print(f"No {lang} libraries found.")
        print()

if __name__ == "__main__":
    main()
