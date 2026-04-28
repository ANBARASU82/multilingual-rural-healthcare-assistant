from flask import Blueprint, jsonify, request

from utils.translator import translate_text

translate_bp = Blueprint("translate", __name__)


@translate_bp.post("/translate")
def translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    target_language = data.get("target_language", "en")

    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400

    try:
        translated = translate_text(text, target_language)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"translated": translated, "language": target_language})
