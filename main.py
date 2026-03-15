import requests
from bs4 import BeautifulSoup
import random
import time

SEARCH_TERMS = [
    "medical conference 2026 speakers",
    "academic congress 2026 faculty",
    "symposium programme participants 2026",
    "international conference speakers list"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def search_duckduckgo(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.select(".result__a"):
        href = a.get("href")
        if href:
            links.append(href)

    return links[:5]


def extract_names_from_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")

        texts = soup.get_text("\n").split("\n")
        names = [t.strip() for t in texts if len(t.strip().split()) == 2]

        return len(set(names))

    except:
        return 0


def run_agent():
    print("Agent started")

    for term in SEARCH_TERMS:
        print("Searching:", term)

        links = search_duckduckgo(term)

        for link in links:
            print("Checking:", link)

            count = extract_names_from_page(link)

            print("Names found:", count)

            if count >= 10:
                print("✅ GOOD CONFERENCE:", link)

            time.sleep(random.randint(5,10))


run_agent()
