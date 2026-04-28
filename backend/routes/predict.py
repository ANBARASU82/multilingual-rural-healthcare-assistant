from flask import Blueprint, jsonify, request

from model.disease_classifier import classifier

predict_bp = Blueprint("predict", __name__)


@predict_bp.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400

    result = classifier.predict(text)
    return jsonify(result)
