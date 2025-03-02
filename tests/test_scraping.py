import os
import json
from scraping import scrape

# Path to combined_libraries.json inside .alexandria
alexandria_folder = os.path.join(os.getcwd(), ".alexandria")
combined_libraries_path = os.path.join(alexandria_folder, "combined_libraries.json")

# Ensure the file exists
if not os.path.exists(combined_libraries_path):
    print(f"❌ Error: {combined_libraries_path} does not exist.")
    exit(1)

# Load libraries from combined_libraries.json
with open(combined_libraries_path, "r", encoding="utf-8") as file:
    combined_libraries = json.load(file)

# Extract libraries and documentation links
test_libraries = []
for lang, libraries in combined_libraries.items():
    for lib in libraries:
        print(lang,lib)
        if lib["doc_link"] and "Documentation not found" not in lib["doc_link"]:
            test_libraries.append([lib["library"], lib["doc_link"]])

# Run scraping on all collected libraries
for name, link in test_libraries:
    scrape.scrape_full_documentation(link, name, os.getcwd())

print("✅ Finished scraping all detected libraries.")
