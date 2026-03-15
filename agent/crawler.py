import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code == 200:
            return r.text
        return ""
    except:
        return ""

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    return text
