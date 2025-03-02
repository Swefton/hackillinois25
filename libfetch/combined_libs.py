import os
import csv
import json

# Import the scanning functions from find_libs.py
from libfetch.find_libs import (
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
from libfetch.libraryfetcher import (
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
        print("NOT FOUND IN COMMON LIBRARIES")
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

def parse_workspace_for_libraries(alexandria_folder, directory):
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
        "python": get_python_doc_url,
        "node": get_npm_doc_url,
        "ruby": get_rubygems_doc_url,
        "php": get_packagist_doc_url,
        "maven": get_maven_doc_url,
        "nuget": get_nuget_doc_url,
        "go": get_go_doc_url,
        "rust": get_rust_doc_url
    }

    # 3) Minimal fallback mappings for ambiguous short inputs.
    fallback_maps = {
        "python": {
            "opencv": "opencv-python",
            "opencv-python": "opencv-python",
            "pd": "pandas",
            "bs4": "beautifulsoup"
        },
    }

    combined_results = {}

    # 4) Process each language
    for lang, finder_func in language_find_functions.items():
        print(f"Scanning for {lang} libraries...")
        libs = finder_func(directory) 
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
            if lib in common_map:
                doc_link = common_map[lib]
            else:
                if lang in fallback_maps and lib.lower() in fallback_maps[lang]:
                    original = lib
                    lib = fallback_maps[lang][lib.lower()]
                    print(f"[{lang}] Mapping ambiguous '{original}' to '{lib}'.")
                if fetcher_func:
                    doc_link = fetcher_func(lib)
                else:
                    doc_link = f"Fetcher not implemented for '{lib}'."
                if not doc_link:
                    doc_link = f"Documentation not found for '{lib}'."
            results.append({"library": lib, "doc_link": doc_link})

        combined_results[lang] = results

    # 5) Save the combined results inside the .alexandria folder
    alexandria_library_path = os.path.join(alexandria_folder, "combined_libraries.json")

    try:
        with open(alexandria_library_path, "w", encoding="utf-8") as f:
            json.dump(combined_results, f, indent=4)
        print(f"✅ Combined libraries saved to {alexandria_library_path}")
    except Exception as e:
        print(f"❌ Error writing {alexandria_library_path}: {e}")
