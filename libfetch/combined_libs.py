import os
import csv
import json

# Import the scanning functions from find_libs.py
from find_libs import (
    find_python_libraries,
    find_node_libraries,
    find_ruby_libraries,
    find_php_libraries,
    find_maven_libraries,
    find_nuget_libraries,
    find_go_libraries,
    find_rust_libraries
)

# Import the doc-fetching functions from libraryfetcher.py
from libraryfetcher import (
    get_python_doc_url,
    get_npm_doc_url,
    get_rubygems_doc_url,
    get_packagist_doc_url,
    get_maven_doc_url,
    get_nuget_doc_url,
    get_go_doc_url,
    get_rust_doc_url
)

def load_common_libraries_csv(language):
    """
    Loads a CSV of the form 'common_libraries/<language>_common_libraries.csv'
    with rows like: library,documentation_link
    Returns a dict {library_name: doc_link} or an empty dict if not found or error.
    """
    filename = f"common_libraries/{language}_common_libraries.csv"
    if not os.path.exists(filename):
        return {}

    common_map = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    lib_name, doc_link = row[0], row[1]
                    common_map[lib_name] = doc_link
    except Exception as e:
        print(f"Error reading {filename}: {e}")

    return common_map

def main():
    # 1) Map each language to its scanning function
    language_find_functions = {
        "python": find_python_libraries,
        "node": find_node_libraries,
        "ruby": find_ruby_libraries,
        "php": find_php_libraries,
        "maven": find_maven_libraries,
        "nuget": find_nuget_libraries,
        "go": find_go_libraries,
        "rust": find_rust_libraries
    }

    # 2) Map each language to the library-fetching function (doc URL lookup)
    language_fetcher_functions = {
        "python": get_python_doc_url,   # uses built-in or PyPI
        "node": get_npm_doc_url,
        "ruby": get_rubygems_doc_url,
        "php": get_packagist_doc_url,
        "maven": get_maven_doc_url,
        "nuget": get_nuget_doc_url,
        "go": get_go_doc_url,
        "rust": get_rust_doc_url
    }

    # 3) Minimal fallback mappings for ambiguous short inputs.
    # (This is minimal—only for very common cases.)
    fallback_maps = {
        "python": {
            "opencv": "opencv-python",
            "opencv-python": "opencv-python",
            "pd": "pandas",
            "bs4": "beautifulsoup"
        },
        # You can define fallback maps for other ecosystems if needed.
    }

    combined_results = {}

    # 4) Process each language
    for lang, finder_func in language_find_functions.items():
        print(f"Scanning for {lang} libraries...")
        libs = finder_func(".")  # Adjust the scanning directory as needed
        if libs is None:
            libs = set()
        else:
            libs = set(libs)
        print(f"Found {len(libs)} libraries for {lang}.")
        
        # Load existing common library docs from CSV (if available)
        common_map = load_common_libraries_csv(lang)
        results = []
        fetcher_func = language_fetcher_functions.get(lang)

        for lib in sorted(libs):
            # If a common documentation link exists, use it.
            if lib in common_map:
                doc_link = common_map[lib]
            else:
                # If there is a fallback mapping for this language, check if we should remap.
                if lang in fallback_maps and lib.lower() in fallback_maps[lang]:
                    original = lib
                    lib = fallback_maps[lang][lib.lower()]
                    print(f"[{lang}] Mapping ambiguous '{original}' to '{lib}'.")
                # Use the fetcher function for this language.
                if fetcher_func:
                    doc_link = fetcher_func(lib)
                else:
                    doc_link = f"Fetcher not implemented for '{lib}'."
                if not doc_link:
                    doc_link = f"Documentation not found for '{lib}'."
            results.append({"library": lib, "doc_link": doc_link})

        # Store results even if empty.
        combined_results[lang] = results

    # 5) Write the combined results to one JSON file.
    os.makedirs("library_links", exist_ok=True)
    out_file = "library_links/combined_libraries.json"
    try:
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(combined_results, f, indent=4)
        print(f"Combined libraries written to {out_file}")
    except Exception as e:
        print(f"Error writing {out_file}: {e}")

if __name__ == "__main__":
    main()
