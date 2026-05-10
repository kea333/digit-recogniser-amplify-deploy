"""
Flask application wrapped for AWS Lambda via apig-wsgi.
Also runnable locally with `python app.py` for development.
"""
import io
import os
import base64

import numpy as np
import joblib
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

from preprocess import preprocess_image

# ── Initialise Flask ────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the Amplify-hosted frontend

# ── Load model once (persists across warm Lambda invocations) ───────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "my_sklearn_model.joblib")
model = joblib.load(MODEL_PATH)
print(f"Model loaded: {type(model).__name__}")


# ── Helpers ─────────────────────────────────────────────────────────────
def decode_base64_image(data_url: str) -> Image.Image:
    if "," in data_url:
        data_url = data_url.split(",")[1]
    return Image.open(io.BytesIO(base64.b64decode(data_url)))


def build_response(processed: np.ndarray) -> dict:
    prediction = model.predict(processed)[0]

    confidence = {}
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(processed)[0]
        confidence = {str(i): round(float(p) * 100, 2) for i, p in enumerate(proba)}
    elif hasattr(model, "decision_function"):
        decision = model.decision_function(processed)[0]
        if hasattr(decision, "__len__"):
            exp_scores = np.exp(decision - np.max(decision))
            softmax = exp_scores / exp_scores.sum()
            confidence = {str(i): round(float(p) * 100, 2) for i, p in enumerate(softmax)}

    return {"prediction": int(prediction), "confidence": confidence}


# ── Routes ──────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": type(model).__name__})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts:
      • JSON: {"image": "<base64 data-URL>"}              (canvas mode)
      • Multipart form-data with file field named "file"   (upload mode)
    """
    try:
        # Reject oversized payloads (2MB limit)
        if request.content_length and request.content_length > 2 * 1024 * 1024:
            return jsonify({"error": "Payload too large. Maximum size is 2MB."}), 413

        if "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400
            image = Image.open(file.stream)
        else:
            data = request.get_json(silent=True)
            if not data or "image" not in data:
                return jsonify({"error": "No image data provided"}), 400
            image = decode_base64_image(data["image"])

        processed = preprocess_image(image)
        return jsonify(build_response(processed))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Lambda handler (apig-wsgi bridges API Gateway → Flask) ──────────────
# This is what Lambda calls.
try:
    from apig_wsgi import make_lambda_handler
    lambda_handler = make_lambda_handler(app, binary_support=True)
except ImportError:
    # Running locally, not on Lambda
    lambda_handler = None

if __name__ == "__main__":
    app.run(debug=True, port=5000)
