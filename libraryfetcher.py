import importlib.util
import requests

def is_builtin(library_name):
    spec = importlib.util.find_spec(library_name)
    return spec is not None and spec.origin == 'built-in'

def get_builtin_documentation_url(library_name):
    return f"https://docs.python.org/3/library/{library_name}.html"

def get_pypi_info(library_name):
    url = f"https://pypi.org/pypi/{library_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_documentation_url_from_pypi(library_name):
    info = get_pypi_info(library_name)
    if info:
        urls = info['info'].get('project_urls', {})
        for key in ['Documentation', 'Docs', 'documentation']:
            if key in urls and urls[key]:
                return urls[key]
        docs_url = info['info'].get('docs_url')
        if docs_url:
            return docs_url
        if 'Home' in urls and urls['Home']:
            return urls['Home']
        home_page = info['info'].get('home_page')
        if home_page:
            return home_page
    return None

def get_documentation_url(library_name):
    if is_builtin(library_name):
        return get_builtin_documentation_url(library_name)
    else:
        doc_url = get_documentation_url_from_pypi(library_name)
        if doc_url:
            return doc_url
        else:
            return f"Documentation not found for '{library_name}'."

if __name__ == "__main__":
    library = input("Enter the Python library name: ").strip()
    print("Documentation URL:", get_documentation_url(library))
