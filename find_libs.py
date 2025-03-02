import os
import re
import json
import xml.etree.ElementTree as ET

def find_python_libraries(directory="."):
    """Scan .py files for top-level imports."""
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
                    print(f"Skipping {file_path}: {e}")
    return libraries

def find_node_libraries(directory="."):
    """Find Node libraries by parsing package.json files while skipping node_modules and hidden directories."""
    libraries = set()
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories and node_modules
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
        if "package.json" in files:
            file_path = os.path.join(root, "package.json")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    data = json.load(f)
                    # Only use production dependencies to avoid too many libraries.
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
