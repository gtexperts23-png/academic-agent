from flask import Flask
import threading
import time
import os

from agent.query_gen import generate_queries
from agent.search_engines import duckduckgo_search
from agent.conference_ai import analyze_link
from agent.sheet_writer import write_row

app = Flask(__name__)

def agent_loop():
    while True:
        print("========== AGENT CYCLE STARTED ==========")

        queries = generate_queries(10)

        for q in queries:
            print("Searching:", q)

            links = duckduckgo_search(q)

            for link in links:
                print("Checking:", link)

                result = analyze_link(link)

                if result:
                    print("GOOD CONFERENCE FOUND:", result)

                    try:
                        write_row(result)
                        print("Written to sheet")
                    except Exception as e:
                        print("Sheet error:", e)

                time.sleep(3)

        print("Sleeping 3 hours...")
        time.sleep(10800)


threading.Thread(target=agent_loop).start()


@app.route("/")
def home():
    return "Academic Agent Alive"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
