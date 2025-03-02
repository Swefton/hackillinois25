# combined_libs.py

import os
import csv

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


def write_library_links_csv(language, entries):
    """
    Writes the list of (library, doc_link) tuples to
    library_links/<language>_libraries.csv with no header row.
    """
    os.makedirs("library_links", exist_ok=True)
    out_file = f"library_links/{language}_libraries.csv"
    try:
        with open(out_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            # Write each (lib, doc) pair
            for lib_name, doc_link in entries:
                writer.writerow([lib_name, doc_link])
    except Exception as e:
        print(f"Error writing {out_file}: {e}")


def main():
    # 1) Collect libraries from find_libs.py
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

    # 2) Map each language to the libraryfetcher function we should use if it's not in the CSV
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

    # 3) For each language, gather libraries and find doc links
    for lang, finder_func in language_find_functions.items():
        libs = finder_func(".")  # Scan current directory; adjust as needed
        if not libs:
            # Skip writing output if no libraries are found
            continue

        # Load existing "common" library docs from CSV (may be empty if not found)
        common_map = load_common_libraries_csv(lang)

        results = []
        fetcher_func = language_fetcher_functions[lang]

        for lib in libs:
            if lib in common_map:
                # Found in CSV
                doc_link = common_map[lib]
            else:
                # Not in CSV; use libraryfetcher
                doc_link = fetcher_func(lib)
                if not doc_link:
                    doc_link = f"Documentation not found for '{lib}'."
            results.append((lib, doc_link))

        # Write out each language's results to library_links/<language>_libraries.csv
        write_library_links_csv(lang, results)


if __name__ == "__main__":
    main()
