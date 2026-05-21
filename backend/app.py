"""
Flask application wrapped for AWS Lambda via apig-wsgi.
Also runnable locally with `python app.py` for development.

Backend change: scikit-learn MLPClassifier (joblib) replaced with
PyTorch CNN exported to ONNX, served via onnxruntime.
"""
import io
import os
import base64

import numpy as np
import onnxruntime as ort
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

from preprocess import preprocess_image

# ── Initialise Flask ─────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the Amplify-hosted frontend

# ── Load ONNX model once (persists across warm Lambda invocations) ────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "my_cnn_model.onnx")

sess_options = ort.SessionOptions()
sess_options.intra_op_num_threads = 1   # Lambda is single-threaded
sess_options.inter_op_num_threads = 1

ort_session = ort.InferenceSession(
    MODEL_PATH,
    sess_options=sess_options,
    providers=["CPUExecutionProvider"],  # Lambda has no GPU
)

INPUT_NAME  = ort_session.get_inputs()[0].name    # "input"
OUTPUT_NAME = ort_session.get_outputs()[0].name   # "output"

print(f"ONNX model loaded. Input: '{INPUT_NAME}', Output: '{OUTPUT_NAME}'")


# ── Helpers ───────────────────────────────────────────────────────────────
def decode_base64_image(data_url: str) -> Image.Image:
    if "," in data_url:
        data_url = data_url.split(",")[1]
    return Image.open(io.BytesIO(base64.b64decode(data_url)))


def softmax(logits: np.ndarray) -> np.ndarray:
    e = np.exp(logits - np.max(logits))
    return e / e.sum()


def build_response(processed: np.ndarray) -> dict:
    """Run ONNX inference and return prediction + per-class confidence."""
    logits = ort_session.run([OUTPUT_NAME], {INPUT_NAME: processed})[0][0]
    probabilities = softmax(logits)
    prediction = int(np.argmax(probabilities))
    confidence = {str(i): round(float(p) * 100, 2) for i, p in enumerate(probabilities)}
    return {"prediction": prediction, "confidence": confidence}


# ── Routes ────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "CNN (ONNX Runtime)"})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts:
      • JSON: {"image": "<base64 data-URL>"}              (canvas mode)
      • Multipart form-data with file field named "file"   (upload mode)
    """
    try:
        # Reject oversized payloads (2 MB limit)
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

        processed = preprocess_image(image)   # → (1,1,28,28) float32
        return jsonify(build_response(processed))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Lambda handler (apig-wsgi bridges API Gateway → Flask) ───────────────
try:
    from apig_wsgi import make_lambda_handler
    lambda_handler = make_lambda_handler(app, binary_support=True)
except ImportError:
    lambda_handler = None  # Running locally

if __name__ == "__main__":
    app.run(debug=True, port=5000)
