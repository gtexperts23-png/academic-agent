import requests
from bs4 import BeautifulSoup
import re
import time
import random
import schedule
import datetime
import threading

from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# ================= FLASK =================

app = Flask(__name__)

@app.route("/")
def home():
    return "ULTRA Academic Agent Running"


# ================= GOOGLE SHEET =================

SHEET_NAME = "Academic Conferences Agent"

def connect_sheet():

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "google.json", scope
    )

    client = gspread.authorize(creds)

    return client.open(SHEET_NAME).worksheet("Sheet1")


def save(data):

    sheet = connect_sheet()

    links = sheet.col_values(11)

    if data["link"] in links:
        return

    sheet.append_row([
        data["title"],
        data["field"],
        data["city"],
        data["venue"],
        data["country"],
        data["duration"],
        data["names"],
        "",
        data["list_type"],
        data["pdf"],
        data["link"],
        "",
        str(datetime.date.today())
    ])

    print("✅ SAVED", data["title"])


# ================= NLP =================

def count_names(text):

    prof = re.findall(r"Prof\.?\s+[A-Z][a-z]+", text)
    dr = re.findall(r"Dr\.?\s+[A-Z][a-z]+", text)
    mr = re.findall(r"[A-Z][a-z]+\s[A-Z][a-z]+", text)

    return len(prof) + len(dr) + int(len(mr)/8)


def detect_country(text):

    m = re.search(
        r"Italy|Germany|France|Spain|Netherlands|USA|Canada|Japan|Australia",
        text
    )
    return m.group(0) if m else ""


def detect_city(text):

    m = re.search(
        r"Rome|Paris|Berlin|Madrid|Amsterdam|Toronto|Tokyo|Sydney",
        text
    )
    return m.group(0) if m else ""


def detect_duration(text):

    d = re.findall(r"\d{1,2}\s+(June|July|August|September)", text)

    return len(d)


# ================= FETCH =================

session = requests.Session()

def fetch(url):

    try:
        r = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=25)
        return r.text
    except:
        return None


# ================= ULTRA ANALYZE =================

def deep_scan(url, field, depth=0):

    if depth > 2:
        return

    html = fetch(url)

    if not html:
        return

    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(" ", strip=True)

    names = count_names(text)

    if names >= 6:

        title = soup.title.string if soup.title else "Conference"

        data = {
            "title": title[:80],
            "field": field,
            "city": detect_city(text),
            "venue": "",
            "country": detect_country(text),
            "duration": detect_duration(text),
            "names": names,
            "list_type": "page",
            "pdf": "",
            "link": url
        }

        save(data)

    # PDF miner
    for a in soup.select("a"):

        href = a.get("href")

        if not href:
            continue

        if ".pdf" in href:

            data = {
                "title": "PDF Programme",
                "field": field,
                "city": "",
                "venue": "",
                "country": "",
                "duration": "",
                "names": "",
                "list_type": "pdf",
                "pdf": href,
                "link": url
            }

            save(data)

        if any(k in href.lower() for k in ["speaker","faculty","participant","programme"]):

            if href.startswith("/"):
                base = "/".join(url.split("/")[:3])
                href = base + href

            deep_scan(href, field, depth+1)

            time.sleep(2)


# ================= SEARCH =================

FIELDS = ["medical","engineering","education","ai","science"]

COUNTRIES = ["italy","germany","france","spain","usa","canada","japan"]

def queries():

    q = []

    for f in FIELDS:
        for c in COUNTRIES:
            q.append(f"{f} conference speakers {c} 2026")

    random.shuffle(q)

    return q[:25]


def google_search(q):

    html = fetch(f"https://www.google.com/search?q={q}")

    if not html:
        return []

    soup = BeautifulSoup(html,"lxml")

    links = []

    for a in soup.select("a"):

        h = a.get("href")

        if h and "http" in h:
            links.append(h)

    return links[:5]


def bing_search(q):

    html = fetch(f"https://www.bing.com/search?q={q}")

    if not html:
        return []

    soup = BeautifulSoup(html,"lxml")

    links = []

    for a in soup.select("li.b_algo h2 a"):
        links.append(a.get("href"))

    return links[:5]


def agent():

    print("🚀 ULTRA AGENT STARTED")

    while True:

        for q in queries():

            print("🔎", q)

            field = q.split()[0]

            links = google_search(q) + bing_search(q)

            for l in links:

                deep_scan(l, field)

                time.sleep(random.randint(4,7))

        print("😴 sleeping 2h")
        time.sleep(7200)


# ================= START =================

threading.Thread(target=agent).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
