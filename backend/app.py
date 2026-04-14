import json
import time
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.claude_service import get_keywords
from tools.alg_scraper import search_alg
from tools.oer_commons import search_oer_commons
from tools.libretexts_scraper import search_libretexts
from tools.license_checker import check_license
from tools.scorer import score_resource

load_dotenv()

app = Flask(__name__)
CORS(app)


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

        # Step 2 — search ALG + OER Commons
        yield event({"step": 2, "message": "Searching ALG and OER Commons..."})
        alg_results = search_alg(keywords)
        oer_results = search_oer_commons(keywords)
        results = alg_results + oer_results

        # Step 3 — fallback to LibreTexts if weak results
        if len(results) < 3:
            yield event({"step": 3, "message": "Results limited — searching LibreTexts..."})
            results += search_libretexts(keywords)
        else:
            yield event({"step": 3, "message": "Sufficient results found, skipping fallback."})

        # Step 4 — license check + scoring + explanations
        yield event({"step": 4, "message": "Checking licenses and generating explanations..."})
        filtered = []
        for r in results:
            r["license"] = check_license(r.get("license_raw", ""))
            if r["license"]:
                score_resource(r)
                filtered.append(r)

        filtered.sort(key=lambda r: r["total_score"], reverse=True)

        # Step 5 — return final results
        yield event({"step": 5, "message": "Done.", "results": filtered})

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
