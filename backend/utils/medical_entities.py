import re
from dataclasses import dataclass


COMMON_DRUGS = {
    "paracetamol",
    "acetaminophen",
    "ibuprofen",
    "amoxicillin",
    "azithromycin",
    "metformin",
    "atorvastatin",
    "amlodipine",
    "insulin",
    "aspirin",
    "cetirizine",
    "omeprazole",
    "salbutamol",
}

DOSAGE_PATTERN = re.compile(
    r"\b\d+(\.\d+)?\s?(mg|mcg|g|ml|iu|units|tablet|tablets|capsule|capsules|drops)\b",
    flags=re.IGNORECASE,
)


@dataclass
class LockedText:
    text: str
    entities: dict


def detect_medical_entities(text: str):
    entities = []

    for match in DOSAGE_PATTERN.finditer(text):
        entities.append({"type": "dosage", "text": match.group(), "start": match.start(), "end": match.end()})

    for drug in COMMON_DRUGS:
        for match in re.finditer(rf"\b{re.escape(drug)}\b", text, flags=re.IGNORECASE):
            entities.append({"type": "drug", "text": match.group(), "start": match.start(), "end": match.end()})

    entities.sort(key=lambda item: item["start"])
    return entities


def lock_medical_entities(text: str) -> LockedText:
    entities = detect_medical_entities(text)
    locked_text = text
    replacements = {}

    for index, entity in enumerate(reversed(entities)):
        token = f"__MED_ENTITY_{len(entities) - index - 1}__"
        replacements[token] = entity["text"]
        locked_text = locked_text[: entity["start"]] + token + locked_text[entity["end"] :]

    return LockedText(text=locked_text, entities=replacements)


def unlock_medical_entities(text: str, entities: dict) -> str:
    restored = text
    for token, value in entities.items():
        restored = restored.replace(token, value)
    return restored
