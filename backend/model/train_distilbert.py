import argparse
import json
from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup


class DiseaseDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, index):
        encoded = self.tokenizer(
            self.texts[index],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        item = {key: value.squeeze(0) for key, value in encoded.items()}
        item["labels"] = torch.tensor(self.labels[index], dtype=torch.long)
        return item


def distillation_loss(student_logits, teacher_logits, labels, alpha=0.5, temperature=2.0):
    hard_loss = F.cross_entropy(student_logits, labels)
    soft_teacher = F.softmax(teacher_logits / temperature, dim=-1)
    soft_student = F.log_softmax(student_logits / temperature, dim=-1)
    soft_loss = F.kl_div(soft_student, soft_teacher, reduction="batchmean") * (temperature**2)
    return alpha * hard_loss + (1 - alpha) * soft_loss


def evaluate(model, loader, device):
    model.eval()
    predictions = []
    actual = []
    with torch.no_grad():
        for batch in loader:
            labels = batch.pop("labels").to(device)
            batch = {key: value.to(device) for key, value in batch.items()}
            logits = model(**batch).logits
            predictions.extend(torch.argmax(logits, dim=-1).cpu().tolist())
            actual.extend(labels.cpu().tolist())
    return accuracy_score(actual, predictions)


def train(args):
    data = pd.read_csv(args.data)
    if "symptoms" not in data.columns or "disease" not in data.columns:
        raise ValueError("Dataset must contain 'symptoms' and 'disease' columns.")

    labels = sorted(data["disease"].astype(str).unique())
    label_to_id = {label: index for index, label in enumerate(labels)}
    id_to_label = {index: label for label, index in label_to_id.items()}

    data["label"] = data["disease"].astype(str).map(label_to_id)
    train_df, valid_df = train_test_split(data, test_size=0.15, random_state=42, stratify=data["label"])

    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    train_dataset = DiseaseDataset(train_df["symptoms"].astype(str).tolist(), train_df["label"].tolist(), tokenizer)
    valid_dataset = DiseaseDataset(valid_df["symptoms"].astype(str).tolist(), valid_df["label"].tolist(), tokenizer)

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=args.batch_size)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    teacher = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(labels))
    student = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=len(labels))
    teacher.to(device)
    student.to(device)

    optimizer = torch.optim.AdamW(student.parameters(), lr=args.learning_rate)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=int(total_steps * 0.1), num_training_steps=total_steps)

    best_accuracy = 0.0
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    teacher.eval()
    for epoch in range(args.epochs):
        student.train()
        running_loss = 0.0

        for batch in train_loader:
            labels_tensor = batch.pop("labels").to(device)
            batch = {key: value.to(device) for key, value in batch.items()}

            with torch.no_grad():
                teacher_logits = teacher(**batch).logits

            student_logits = student(**batch).logits
            loss = distillation_loss(student_logits, teacher_logits, labels_tensor, args.alpha, args.temperature)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()
            running_loss += loss.item()

        accuracy = evaluate(student, valid_loader, device)
        print(f"Epoch {epoch + 1}/{args.epochs} - loss={running_loss / len(train_loader):.4f} - val_accuracy={accuracy:.4f}")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            student.save_pretrained(output_dir)
            tokenizer.save_pretrained(output_dir)
            (output_dir / "labels.json").write_text(json.dumps(id_to_label, indent=2))

    print(f"Best validation accuracy: {best_accuracy:.4f}")
    print(f"Saved model to: {output_dir}")


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tune DistilBERT with BERT knowledge distillation.")
    parser.add_argument("--data", required=True, help="CSV with columns: symptoms,disease")
    parser.add_argument("--output", default="model/checkpoints/distilbert-disease", help="Output checkpoint directory")
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight for hard-label loss")
    parser.add_argument("--temperature", type=float, default=2.0)
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
