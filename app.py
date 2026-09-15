from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Load schemes from database file
with open("schemes.json", "r", encoding="utf-8") as file:
    schemes = json.load(file)


@app.route("/")
def home():
    return jsonify({
        "message": "SchemeAI Backend is running",
        "status": "success"
    })


@app.route("/api/schemes", methods=["GET"])
def get_schemes():

    return jsonify({
        "count": len(schemes),
        "schemes": schemes
    })


@app.route("/api/match", methods=["POST"])
def match_schemes():

    data = request.get_json()

    age = int(data.get("age", 0))
    gender = data.get("gender", "")
    category = data.get("category", "")
    purpose = data.get("purpose", "")
    cost = float(data.get("cost", 0))
    business = data.get("business", "")

    results = []

    for scheme in schemes:

        score = 0
        reasons = []
        eligible = True

        # AGE
        if scheme.get("minAge"):

            if age >= scheme["minAge"]:
                score += 15
                reasons.append("Age requirement is satisfied.")
            else:
                eligible = False
                reasons.append("Applicant is below the minimum age.")

        else:
            score += 10


        # CATEGORY
        target = scheme.get("target", "ANY")

        if target == "ANY":

            score += 20
            reasons.append(
                "Scheme is open to multiple social categories."
            )

        elif category == target:

            score += 30
            reasons.append(
                "Social category matches the target group."
            )

        else:

            eligible = False
            reasons.append(
                "Social category does not match the target group."
            )


        # GENDER
        if scheme.get("gender"):

            if gender == scheme["gender"]:

                score += 15
                reasons.append(
                    "Gender requirement is satisfied."
                )

            else:

                eligible = False
                reasons.append(
                    "This scheme has a specific gender requirement."
                )


        # PURPOSE
        if purpose == scheme.get("purpose"):

            score += 20
            reasons.append(
                "Purpose matches the scheme."
            )

        else:

            eligible = False
            reasons.append(
                "Purpose does not match the scheme."
            )


        # PROJECT COST
        min_project = scheme.get("minProject")
        max_project = scheme.get("maxProject")

        if min_project and cost < min_project:

            eligible = False
            reasons.append(
                "Project cost is below the scheme range."
            )

        elif max_project and cost > max_project:

            eligible = False
            reasons.append(
                "Project cost exceeds the scheme range."
            )

        else:

            score += 20
            reasons.append(
                "Project cost fits the scheme range."
            )


        # BUSINESS ACTIVITY
        if business:

            reasons.append(
                f"Activity recorded: {business}"
            )


        results.append({
            "name": scheme["name"],
            "target": scheme["target"],
            "purpose": scheme["purpose"],
            "maxLoan": scheme.get("maxLoan"),
            "interest": scheme.get("interest"),
            "years": scheme.get("years"),
            "reason": scheme.get("reason"),
            "source": scheme.get("source"),
            "score": score,
            "eligible": eligible,
            "reasons": reasons
        })


    # Eligible schemes first
    results.sort(
        key=lambda x: (
            x["eligible"],
            x["score"]
        ),
        reverse=True
    )


    return jsonify({
        "success": True,
        "total": len(results),
        "eligibleCount": len(
            [x for x in results if x["eligible"]]
        ),
        "results": results
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
