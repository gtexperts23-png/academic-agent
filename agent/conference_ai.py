from .crawler import fetch_page, extract_text
from .extractor import estimate_names

def analyze_link(url):
    html = fetch_page(url)
    if not html:
        return None

    text = extract_text(html)

    names_count = estimate_names(text)

    if names_count >= 10:
        return {
            "link": url,
            "names": names_count
        }

    return None
