from flask import Flask
import threading
import time

from agent.query_gen import generate_queries
from agent.search_engines import duckduckgo_search
from agent.conference_ai import analyze_link

app = Flask(__name__)

def agent_loop():
    while True:
        print("Agent cycle started")

        queries = generate_queries(10)

        for q in queries:
            print("Searching:", q)

            links = duckduckgo_search(q)

            for link in links:
                result = analyze_link(link)

                if result:
                    print("GOOD:", result)

        print("Sleeping 3 hours")
        time.sleep(10800)

threading.Thread(target=agent_loop).start()

@app.route("/")
def home():
    return "Agent Alive"
