from flask import Blueprint, jsonify, request

from utils.simplifier import make_patient_instructions
from utils.translator import translate_text

simplify_bp = Blueprint("simplify", __name__)


@simplify_bp.post("/simplify")
def simplify():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    target_language = data.get("target_language", "en")

    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400

    simplified = make_patient_instructions(text)
    translated = translate_text(simplified, target_language)
    return jsonify({"simplified": simplified, "translated": translated, "language": target_language})
