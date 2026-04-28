import json
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from utils.config import CHECKPOINT_DIR


RULE_BASED_DISEASES = [
    ({"fever", "cough", "cold", "throat"}, "Flu"),
    ({"fever", "rash", "joint", "pain"}, "Dengue"),
    ({"chest", "pain", "breath"}, "Possible Heart Condition"),
    ({"thirst", "urination", "fatigue"}, "Possible Diabetes"),
    ({"headache", "nausea", "migraine"}, "Migraine"),
]


class DiseaseClassifier:
    def __init__(self, checkpoint_dir: Path = CHECKPOINT_DIR):
        self.checkpoint_dir = checkpoint_dir
        self.model = None
        self.tokenizer = None
        self.id_to_label = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_if_available()

    def _load_if_available(self):
        if not self.checkpoint_dir.exists():
            return
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint_dir)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.checkpoint_dir)
            self.model.to(self.device)
            self.model.eval()
            labels_path = self.checkpoint_dir / "labels.json"
            if labels_path.exists():
                self.id_to_label = {int(key): value for key, value in json.loads(labels_path.read_text()).items()}
        except Exception:
            self.model = None
            self.tokenizer = None

    def predict(self, text: str):
        if self.model and self.tokenizer:
            return self._predict_with_model(text)
        return self._predict_with_rules(text)

    def _predict_with_model(self, text: str):
        encoded = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
        encoded = {key: value.to(self.device) for key, value in encoded.items()}
        with torch.no_grad():
            logits = self.model(**encoded).logits
            probabilities = torch.softmax(logits, dim=-1)[0]
            confidence, predicted_id = torch.max(probabilities, dim=0)

        disease = self.id_to_label.get(int(predicted_id), str(int(predicted_id)))
        return {"disease": disease, "confidence": round(float(confidence), 4), "model": "distilbert"}

    def _predict_with_rules(self, text: str):
        words = set(text.lower().replace(",", " ").split())
        best_label = "General Consultation Recommended"
        best_score = 0

        for keywords, disease in RULE_BASED_DISEASES:
            score = len(words.intersection(keywords))
            if score > best_score:
                best_score = score
                best_label = disease

        confidence = min(0.55 + best_score * 0.12, 0.91) if best_score else 0.5
        return {"disease": best_label, "confidence": round(confidence, 4), "model": "rule-based fallback"}


classifier = DiseaseClassifier()
