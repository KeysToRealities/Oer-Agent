import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.claude_service import get_keywords
from tools.alg_scraper import search_alg
from tools.openstax_scraper import search_openstax
from tools.open_textbook_library import search_open_textbook_library
from tools.license_checker import check_license
from tools.scorer import score_resource

load_dotenv()

app = Flask(__name__)
CORS(app)

SCRAPERS = [
    ("ALG",                   search_alg),
    ("OpenStax",              search_openstax),
    ("Open Textbook Library", search_open_textbook_library),
]


def event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@app.route("/api/search")
def search():
    course = request.args.get("course", "").strip()
    if not course:
        return jsonify({"error": "course parameter is required"}), 400

    def stream():
        # Step 1 — keyword mapping
        yield event({"step": 1, "message": "Mapping course to search keywords..."})
        keywords = get_keywords(course)

        # Step 2 — search all sources in parallel across all keywords
        yield event({"step": 2, "message": "Claude is searching for resources..."})

        results = []
        seen: set[str] = set()
        with ThreadPoolExecutor(max_workers=len(SCRAPERS) * len(keywords)) as pool:
            futures = {pool.submit(fn, kw): name for kw in keywords for name, fn in SCRAPERS}
            for future in as_completed(futures):
                try:
                    for r in future.result():
                        key = r.get("url") or r.get("title", "")
                        if key and key not in seen:
                            seen.add(key)
                            results.append(r)
                except Exception as e:
                    print(f"[{futures[future]}] Scraper error: {e}")

        # Step 3 — license filter
        licensed = []
        for r in results:
            r["license"] = check_license(r.get("license_raw", ""))
            if r["license"]:
                licensed.append(r)

        # Step 4 — parallel Claude scoring (cap at 20, 3 workers to stay within rate limits)
        licensed = licensed[:20]
        yield event({"step": 4, "message": f"Claude is evaluating {len(licensed)} resources..."})

        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(score_resource, r, course) for r in licensed]
            scored = [f.result() for f in as_completed(futures)]

        scored = [r for r in scored if r.get("relevance_score", 0) >= 2.0]
        scored.sort(key=lambda r: r["total_score"], reverse=True)

        # Step 5 — done
        yield event({"step": 5, "message": "Done.", "results": scored})

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
