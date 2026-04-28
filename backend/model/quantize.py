import argparse
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def quantize(model_dir: str):
    source = Path(model_dir)
    output = source.with_name(source.name + "-quantized")
    output.mkdir(parents=True, exist_ok=True)

    model = AutoModelForSequenceClassification.from_pretrained(source)
    quantized = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
    tokenizer = AutoTokenizer.from_pretrained(source)

    quantized.save_pretrained(output)
    tokenizer.save_pretrained(output)

    labels = source / "labels.json"
    if labels.exists():
        (output / "labels.json").write_text(labels.read_text())

    print(f"Quantized model saved to: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a smaller CPU-friendly DistilBERT checkpoint.")
    parser.add_argument("--model-dir", required=True)
    args = parser.parse_args()
    quantize(args.model_dir)
