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


# ================== FLASK PORT FOR RENDER ==================

app = Flask(__name__)

@app.route("/")
def home():
    return "Academic Agent Running"


# ================== GOOGLE SHEET ==================

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


def write_row(data):

    sheet = connect_sheet()

    existing = sheet.col_values(11)

    if data["link"] in existing:
        return

    sheet.append_row([
        data["name"],
        data["field"],
        data["city"],
        data["venue"],
        data["country"],
        "",
        data["names"],
        "",
        "",
        "",
        data["link"],
        "",
        str(datetime.date.today())
    ])

    print("✅ SAVED:", data["name"])


# ================== REAL INTELLIGENCE AGENT ==================

FIELDS = [
    "medical",
    "engineering",
    "education",
    "pharmacy",
    "ai",
    "science"
]

COUNTRIES = [
    "italy",
    "germany",
    "france",
    "spain",
    "netherlands",
    "usa",
    "canada",
    "australia",
    "japan"
]


def generate_queries():

    queries = []

    for f in FIELDS:
        for c in COUNTRIES:
            queries.append(
                f"{f} international conference speakers {c} 2026"
            )

    random.shuffle(queries)

    return queries[:20]


def fetch(url):

    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=25
        )
        return r.text
    except:
        return None


def count_names(text):

    prof = re.findall(r"Prof\.?\s+[A-Z][a-z]+", text)
    dr = re.findall(r"Dr\.?\s+[A-Z][a-z]+", text)

    return len(prof) + len(dr)


def extract_country(text):

    m = re.search(
        r"Italy|Germany|France|Spain|Netherlands|USA|Canada|Australia|Japan",
        text
    )
    return m.group(0) if m else ""


def extract_city(text):

    m = re.search(
        r"Rome|Paris|Berlin|Madrid|Amsterdam|Toronto|Tokyo|Sydney",
        text
    )
    return m.group(0) if m else ""


def extract_duration(text):

    days = re.findall(
        r"\d{1,2}\s+(June|July|August|September)",
        text
    )

    return len(days)


def deep_analyze(url, field):

    html = fetch(url)

    if not html:
        return

    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(" ", strip=True)

    names = count_names(text)

    if names < 10:
        return

    duration = extract_duration(text)

    if duration < 3:
        return

    country = extract_country(text)
    city = extract_city(text)

    title = soup.title.string if soup.title else "Conference"

    data = {
        "name": title[:80],
        "field": field,
        "city": city,
        "venue": "",
        "country": country,
        "names": names,
        "link": url
    }

    write_row(data)

    # ======= FOLLOW INTERNAL LINKS (REAL AGENT FEATURE)

    for a in soup.select("a"):

        href = a.get("href")

        if not href:
            continue

        if "speaker" in href or "faculty" in href or "participant" in href:

            if href.startswith("/"):
                base = "/".join(url.split("/")[:3])
                href = base + href

            html2 = fetch(href)

            if not html2:
                continue

            text2 = BeautifulSoup(html2, "lxml").get_text(" ", strip=True)

            names2 = count_names(text2)

            if names2 >= 10:
                data["link"] = href
                data["names"] = names2
                write_row(data)

            time.sleep(3)


def search_cycle():

    queries = generate_queries()

    for q in queries:

        print("🔎", q)

        google = f"https://www.google.com/search?q={q}"

        html = fetch(google)

        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")

        for a in soup.select("a"):

            link = a.get("href")

            if not link:
                continue

            if "http" not in link:
                continue

            field = q.split()[0]

            deep_analyze(link, field)

            time.sleep(random.randint(4, 8))


def agent_loop():

    print("🚀 REAL Academic Agent Started")

    search_cycle()

    schedule.every(3).hours.do(search_cycle)

    while True:
        schedule.run_pending()
        time.sleep(60)


# ================== START BOTH ==================

threading.Thread(target=agent_loop).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
