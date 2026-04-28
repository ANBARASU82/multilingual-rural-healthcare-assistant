# Multilingual Rural Healthcare Assistant

A beginner-friendly full-stack AI project for converting medical reports, symptoms, and report images into simple regional-language health guidance.

Supported languages in this starter: English, Hindi, Tamil. The language layer is expandable.

> Medical safety note: this project is for education and triage assistance. It must not replace a licensed doctor. Always validate predictions and outputs before real clinical use.

## Features

- Symptom to disease prediction with a DistilBERT-ready Flask API.
- Knowledge distillation training script with BERT teacher and DistilBERT student.
- Medical Entity Recognition and Alignment layer that preserves drug names and dosages.
- Semantic simplification for complex medical report terms.
- Translation to Hindi and Tamil using Google Translate-compatible libraries, with offline dictionary fallback.
- Text-to-speech endpoint.
- OCR support for uploaded report images.
- React patient chatbot and doctor dashboard.
- Optional offline optimization through dynamic quantization.

## Project Structure

```text
backend/
  app.py
  model/
    disease_classifier.py
    train_distilbert.py
    quantize.py
  routes/
    predict.py
    simplify.py
    translate.py
    voice.py
    ocr.py
  utils/
    config.py
    medical_entities.py
    simplifier.py
    translator.py
    speech.py
    ocr.py
frontend/
  package.json
  index.html
  src/
    App.jsx
    main.jsx
    api.js
    components/
    pages/
requirements.txt
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r ..\requirements.txt
python app.py
```

The API runs at `http://127.0.0.1:5000`.

If you want OCR from images, install Tesseract OCR on your computer and add it to PATH.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://127.0.0.1:5173`.

## Training The Model

Prepare a CSV from the Kaggle Disease Diagnosis Dataset:

```csv
symptoms,disease
"fever cough headache","Flu"
"chest pain shortness of breath","Heart Disease"
```

Then run:

```bash
cd backend
python model/train_distilbert.py --data data/disease_dataset.csv --output model/checkpoints/distilbert-disease
```

The script:

1. Loads `bert-base-uncased` as the teacher.
2. Loads `distilbert-base-uncased` as the student.
3. Trains the student with cross-entropy and KL-divergence distillation loss.
4. Saves the student model, tokenizer, and label map.

## Optional Quantization

```bash
cd backend
python model/quantize.py --model-dir model/checkpoints/distilbert-disease
```

Quantization helps offline mode and lower-resource devices.

## API Endpoints

### `POST /predict`

```json
{
  "text": "fever cough body pain"
}
```

### `POST /simplify`

```json
{
  "text": "Patient has hypertension. Take Paracetamol 500 mg twice daily.",
  "target_language": "ta"
}
```

### `POST /translate`

```json
{
  "text": "Drink more water",
  "target_language": "hi"
}
```

### `POST /voice`

```json
{
  "text": "Drink water and rest",
  "language": "en"
}
```

Returns an MP3 audio file.

### `POST /ocr`

Upload a report image with form field name `file`.

### `POST /report-image`

Upload a report image and `target_language`. The API extracts text, simplifies it, translates it, and returns the final patient-friendly output.

## Performance Targets

The architecture is designed for:

- Accuracy target: about 94% after dataset-specific fine-tuning and validation.
- Latency target: under 50ms for cached/quantized inference on suitable hardware.
- Model size target: under 300MB with DistilBERT and quantization.

Actual values depend on dataset quality, hardware, sequence length, and deployment settings.

For image report upload, Tesseract must be installed at:

C:\Program Files\Tesseract-OCR\tesseract.exe
