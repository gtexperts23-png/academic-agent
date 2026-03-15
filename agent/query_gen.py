import random

BASE_TERMS = [
    "conference speakers",
    "congress faculty",
    "symposium programme",
    "workshop participants",
    "summit invited speakers"
]

FIELDS = [
    "medical",
    "engineering",
    "education",
    "science",
    "technology",
    "business",
    "pharmacy",
    "dentistry"
]

YEARS = ["2026","2027"]

def generate_queries(n=20):
    queries = []
    for _ in range(n):
        q = f"{random.choice(FIELDS)} {random.choice(BASE_TERMS)} {random.choice(YEARS)}"
        queries.append(q)
    return queries
