# app.py
from flask import Flask, request, jsonify
from model_logic import analyze_body
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        url = data.get("urlImg")
        gender = data.get("gender")

        if not url or not gender:
            return jsonify({"error": "Missing urlImg or gender"}), 400

        response = requests.get(url)
        image = Image.open(BytesIO(response.content)).convert("RGB")

        result = analyze_body(image, gender.lower())
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
