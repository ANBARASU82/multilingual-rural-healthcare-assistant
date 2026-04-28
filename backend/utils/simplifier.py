import re

from utils.medical_entities import lock_medical_entities, unlock_medical_entities


MEDICAL_GLOSSARY = {
    "hypertension": "high blood pressure",
    "hypotension": "low blood pressure",
    "myocardial infarction": "heart attack",
    "hyperglycemia": "high blood sugar",
    "hypoglycemia": "low blood sugar",
    "dyspnea": "breathing difficulty",
    "edema": "swelling",
    "pyrexia": "fever",
    "analgesic": "pain relief medicine",
    "antipyretic": "fever reducing medicine",
    "bid": "two times a day",
    "tid": "three times a day",
    "qid": "four times a day",
    "po": "by mouth",
    "prn": "only when needed",
}


def simplify_medical_text(text: str) -> str:
    locked = lock_medical_entities(text)
    simplified = locked.text

    for complex_term, simple_term in MEDICAL_GLOSSARY.items():
        simplified = re.sub(rf"\b{re.escape(complex_term)}\b", simple_term, simplified, flags=re.IGNORECASE)

    simplified = re.sub(r"\badminister\b", "give", simplified, flags=re.IGNORECASE)
    simplified = re.sub(r"\bconsume\b", "take", simplified, flags=re.IGNORECASE)
    simplified = re.sub(r"\bmonitor\b", "check", simplified, flags=re.IGNORECASE)
    simplified = re.sub(r"\s+", " ", simplified).strip()

    return unlock_medical_entities(simplified, locked.entities)


def make_patient_instructions(text: str) -> str:
    simplified = simplify_medical_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", simplified)
    cleaned = [sentence.strip() for sentence in sentences if sentence.strip()]
    if not cleaned:
        return "Please enter a medical report or symptom description."
    return " ".join(cleaned)
