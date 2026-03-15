import requests
from bs4 import BeautifulSoup
import re
import time
import random
import schedule
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_NAME = "Academic Conferences Agent"


# ================= GOOGLE SHEET =================

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

    existing_links = sheet.col_values(11)

    if data["link"] in existing_links:
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

    print("✅ WRITTEN:", data["name"])


# ================= AI PART =================

FIELDS = [
    "medical",
    "engineering",
    "education",
    "science",
    "pharmacy",
    "dentistry",
    "ai",
    "public health"
]

COUNTRIES = [
    "italy",
    "germany",
    "france",
    "spain",
    "netherlands",
    "switzerland",
    "usa",
    "canada",
    "australia",
    "japan"
]


def generate_queries():

    queries = []

    year = 2026

    for f in FIELDS:
        for c in COUNTRIES:
            queries.append(
                f"{f} international conference {c} {year} speakers"
            )

    random.shuffle(queries)

    return queries[:15]


def fetch(url):

    try:
        r = requests.get(url, timeout=20, headers={
            "User-Agent": "Mozilla/5.0"
        })
        return r.text
    except:
        return None


def extract_names(text):

    names = re.findall(r"Prof\.?\s+[A-Z][a-z]+", text)

    return len(names)


def extract_city(text):

    m = re.search(r"(Rome|Paris|Berlin|Madrid|Toronto|Tokyo|Sydney)", text)
    return m.group(1) if m else ""


def extract_country(text):

    m = re.search(r"(Italy|France|Germany|Spain|Canada|Japan|Australia)", text)
    return m.group(1) if m else ""


def extract_duration(text):

    days = re.findall(r"\d{1,2}\s+(June|July|August)", text)

    return len(days)


def analyze(url, field):

    html = fetch(url)

    if not html:
        return

    soup = BeautifulSoup(html, "lxml")

    text = soup.get_text(" ", strip=True)

    names = extract_names(text)

    if names < 10:
        return

    duration = extract_duration(text)

    if duration < 3:
        return

    city = extract_city(text)
    country = extract_country(text)

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


def search_cycle():

    queries = generate_queries()

    for q in queries:

        print("🔎 Searching:", q)

        url = f"https://www.google.com/search?q={q}"

        html = fetch(url)

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

            analyze(link, field)

            time.sleep(random.randint(5, 9))


# ================= SCHEDULER =================

schedule.every(3).hours.do(search_cycle)

print("🚀 Academic Agent Started")

search_cycle()

while True:
    schedule.run_pending()
    time.sleep(60)
