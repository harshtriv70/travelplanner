import json
import requests
from flask import Flask, render_template, request

# === Configuration ===
API_KEY = "qq3gqgZTu51xwNhEa_poLd-CLcVR6w13QJ4uNgQ8gmi1"  # Replace later if needed
DEPLOYMENT_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/a2a09132-37be-40dd-a149-efd0dc18c9a7/ai_service?version=2021-05-01"

app = Flask(__name__)


def get_iam_token(api_key):
    """Fetch IAM token from IBM Cloud"""
    token_url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}"

    response = requests.post(token_url, headers=headers, data=data, timeout=30)
    response.raise_for_status()
    return response.json()["access_token"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plan", methods=["POST"])
def plan_trip():
    # 1. Get form inputs
    destination = request.form.get("destination", "").strip()
    budget = request.form.get("budget", "").strip()
    duration = request.form.get("duration", "").strip()
    preferences = request.form.get("preferences", "").strip()

    # 2. Construct user prompt
    user_prompt = (
        f"Plan a {duration}-day trip to {destination} with a budget of ${budget}. "
        f"Include transportation, hotels, food, daily itinerary, and costs. "
        f"Preferences: {preferences if preferences else 'None'}."
    )

    # 3. Format payload for Granite
    payload = {
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        },
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 500,
            "temperature": 0.7,
            "repetition_penalty": 1.05
        }
    }

    # 4. Get IAM token
    try:
        token = get_iam_token(API_KEY)
    except requests.HTTPError as e:
        return render_template("index.html", result=f"❌ Auth error: {e}")
    except Exception as e:
        return render_template("index.html", result=f"❌ Unexpected auth error: {e}")

    # 5. Call IBM Watsonx.ai Granite LLM
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(DEPLOYMENT_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        # Parse response
        ai_response = None
        if "results" in result:
            ai_response = result["results"][0].get("generated_text", "")
        elif "predictions" in result:
            ai_response = result["predictions"][0].get("generated_text", "")
        elif "generated_text" in result:
            ai_response = result["generated_text"]
        elif "output" in result:
            ai_response = result["output"]

        if not ai_response:
            return render_template("index.html", result="⚠️ No response received from model.")

        return render_template("index.html", result=ai_response.strip())

    except requests.exceptions.HTTPError as e:
        try:
            error_body = response.json()
        except Exception:
            error_body = response.text
        return render_template("index.html", result=f"❌ HTTP Error {e.response.status_code}: {error_body}")

    except Exception as e:
        return render_template("index.html", result=f"❌ Error during model call: {e}")


# Health check route (optional)
@app.route("/health")
def health():
    return {"status": "ok", "deployment_url": DEPLOYMENT_URL}


if __name__ == "__main__":
    app.run(debug=True)
