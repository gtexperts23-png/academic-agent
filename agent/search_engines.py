import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def duckduckgo_search(query):
    url = f"https://duckduckgo.com/html/?q={query}"
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text,"html.parser")

    links = []
    for a in soup.select(".result__a"):
        href = a.get("href")
        if href:
            links.append(href)

    return links[:7]
