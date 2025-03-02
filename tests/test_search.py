from scraping import search 
import os

# Get the path to the `.alexandria` directory
alexandria_path = os.path.join(os.getcwd(), ".alexandria")

# Run the search function using the correct directory
results = search.search_docs("intents needed", alexandria_path, k=3)
print(results)
