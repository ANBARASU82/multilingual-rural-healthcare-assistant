from pathlib import Path
from uuid import uuid4

from flask import Blueprint, jsonify, request

from utils.config import UPLOAD_DIR
from utils.ocr import extract_text_from_image
from utils.simplifier import make_patient_instructions
from utils.translator import translate_text

ocr_bp = Blueprint("ocr", __name__)


def _save_upload():
    if "file" not in request.files:
        return None, ("Image file field 'file' is required.", 400)
    uploaded = request.files["file"]
    if uploaded.filename == "":
        return None, ("Uploaded file must have a name.", 400)
    suffix = Path(uploaded.filename).suffix or ".png"
    path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"
    uploaded.save(path)
    return path, None


@ocr_bp.post("/ocr")
def ocr():
    path, error = _save_upload()
    if error:
        return jsonify({"error": error[0]}), error[1]
    try:
        text = extract_text_from_image(str(path))
    except Exception as exc:
        return jsonify({"error": f"OCR failed: {exc}"}), 500
    return jsonify({"text": text})


@ocr_bp.post("/report-image")
def report_image():
    path, error = _save_upload()
    if error:
        return jsonify({"error": error[0]}), error[1]

    target_language = request.form.get("target_language", "en")
    try:
        extracted_text = extract_text_from_image(str(path))
    except Exception as exc:
        return jsonify({"error": f"OCR failed: {exc}"}), 500

    simplified = make_patient_instructions(extracted_text)
    translated = translate_text(simplified, target_language)

    return jsonify(
        {
            "extracted_text": extracted_text,
            "simplified": simplified,
            "translated": translated,
            "language": target_language,
        }
    )
