from deep_translator import GoogleTranslator

from utils.config import SUPPORTED_LANGUAGES
from utils.medical_entities import lock_medical_entities, unlock_medical_entities


TRANSLATOR_LANGUAGE_CODES = {
    "hi": "hindi",
    "ta": "tamil",
}

OFFLINE_SENTENCES = {
    "hi": {
        "Drink more water.": "अधिक पानी पिएं।",
        "Take rest.": "आराम करें।",
        "Please consult a doctor.": "कृपया डॉक्टर से मिलें।",
    },
    "ta": {
        "Drink more water.": "அதிகமாக தண்ணீர் குடிக்கவும்.",
        "Take rest.": "ஓய்வு எடுக்கவும்.",
        "Please consult a doctor.": "தயவு செய்து மருத்துவரை அணுகவும்.",
    },
}

OFFLINE_PHRASES = {
    "hi": {
        "high blood pressure": "उच्च रक्तचाप",
        "low blood pressure": "निम्न रक्तचाप",
        "heart attack": "दिल का दौरा",
        "high blood sugar": "उच्च रक्त शर्करा",
        "low blood sugar": "कम रक्त शर्करा",
        "breathing difficulty": "सांस लेने में कठिनाई",
        "swelling": "सूजन",
        "fever": "बुखार",
        "pain relief medicine": "दर्द कम करने की दवा",
        "fever reducing medicine": "बुखार कम करने की दवा",
        "two times a day": "दिन में दो बार",
        "three times a day": "दिन में तीन बार",
        "four times a day": "दिन में चार बार",
        "by mouth": "मुंह से",
        "only when needed": "जरूरत पड़ने पर ही",
        "take": "लें",
        "give": "दें",
        "check": "जांचें",
        "patient has": "रोगी को है",
        "doctor": "डॉक्टर",
        "medicine": "दवा",
        "daily": "रोजाना",
        "after food": "खाने के बाद",
        "before food": "खाने से पहले",
        "morning": "सुबह",
        "night": "रात",
        "drink more water": "अधिक पानी पिएं",
        "take rest": "आराम करें",
        "consult a doctor": "डॉक्टर से मिलें",
    },
    "ta": {
        "high blood pressure": "உயர் இரத்த அழுத்தம்",
        "low blood pressure": "குறைந்த இரத்த அழுத்தம்",
        "heart attack": "இதயத் தாக்கம்",
        "high blood sugar": "அதிக இரத்த சர்க்கரை",
        "low blood sugar": "குறைந்த இரத்த சர்க்கரை",
        "breathing difficulty": "மூச்சு விட சிரமம்",
        "swelling": "வீக்கம்",
        "fever": "காய்ச்சல்",
        "pain relief medicine": "வலி குறைக்கும் மருந்து",
        "fever reducing medicine": "காய்ச்சல் குறைக்கும் மருந்து",
        "two times a day": "ஒரு நாளில் இரண்டு முறை",
        "three times a day": "ஒரு நாளில் மூன்று முறை",
        "four times a day": "ஒரு நாளில் நான்கு முறை",
        "by mouth": "வாய் வழியாக",
        "only when needed": "தேவையான போது மட்டும்",
        "take": "எடுக்கவும்",
        "give": "கொடுக்கவும்",
        "check": "சரிபார்க்கவும்",
        "patient has": "நோயாளிக்கு உள்ளது",
        "doctor": "மருத்துவர்",
        "medicine": "மருந்து",
        "daily": "தினமும்",
        "after food": "உணவுக்குப் பிறகு",
        "before food": "உணவுக்கு முன்",
        "morning": "காலை",
        "night": "இரவு",
        "drink more water": "அதிகமாக தண்ணீர் குடிக்கவும்",
        "take rest": "ஓய்வு எடுக்கவும்",
        "consult a doctor": "மருத்துவரை அணுகவும்",
    },
}


def _offline_translate(text: str, target_language: str) -> str:
    sentence_translation = OFFLINE_SENTENCES.get(target_language, {}).get(text)
    if sentence_translation:
        return sentence_translation

    translated = text
    phrases = OFFLINE_PHRASES.get(target_language, {})
    for phrase in sorted(phrases, key=len, reverse=True):
        translated = translated.replace(phrase, phrases[phrase])
        translated = translated.replace(phrase.title(), phrases[phrase])
        translated = translated.replace(phrase.capitalize(), phrases[phrase])

    return translated


def translate_text(text: str, target_language: str = "en") -> str:
    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {target_language}")
    if target_language == "en":
        return text

    locked = lock_medical_entities(text)
    try:
        target = TRANSLATOR_LANGUAGE_CODES.get(target_language, target_language)
        translated = GoogleTranslator(source="auto", target=target).translate(locked.text)
    except Exception:
        translated = _offline_translate(locked.text, target_language)

    return unlock_medical_entities(translated, locked.entities)
