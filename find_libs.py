import os
import re
import webbrowser
import requests
from bs4 import BeautifulSoup

def find_python_libraries(directory="."):
    """Find all top-level Python libraries imported in a project, skipping hidden directories."""
    libraries = set()
    import_pattern = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)')

    for root, dirs, files in os.walk(directory):
        # Skip hidden directories (starting with .)
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            match = import_pattern.match(line)
                            if match:
                                libraries.add(match.group(1))  # Capture only the module name
                except Exception as e:
                    print(f"Skipping {file_path}: {e}")

    return sorted(libraries)

if __name__ == "__main__":
    libs = find_python_libraries()
    print("Python libraries found:" if libs else "No libraries found.")
    for lib in libs:
        print(f"- {lib}")