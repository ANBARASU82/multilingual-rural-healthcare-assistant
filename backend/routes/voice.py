from flask import Blueprint, jsonify, request, send_file

from utils.speech import text_to_speech

voice_bp = Blueprint("voice", __name__)


@voice_bp.post("/voice")
def voice():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    language = data.get("language", "en")

    if not text:
        return jsonify({"error": "Field 'text' is required."}), 400

    audio_path = text_to_speech(text, language)
    return send_file(audio_path, mimetype="audio/mpeg", as_attachment=False)
