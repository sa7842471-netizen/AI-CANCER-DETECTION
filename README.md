# AI-CANCER-DETECTION

> Can detect 9+ types of cancers and integrated into one software system.

## Quick Start

### Step 1 — Get free API keys
| Key | Where to get | Free tier |
|-----|-------------|-----------|
| **HuggingFace Token** | https://huggingface.co/settings/tokens → New token (read) | ✅ Free |
| **Groq API Key** | https://console.groq.com → API Keys | ✅ Free |

### Step 2 — Configure backend
```bash
cd backend
copy .env.example .env
# Edit .env and paste your keys
```

### Step 3 — Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4 — Start the Flask backend
```bash
cd backend
python app.py
```
Backend runs at **http://localhost:5000**

### Step 5 — Open the frontend
Open a new terminal:
```bash
python -m http.server 5500
```
Then open **http://localhost:5500** in your browser.

---

## Features

| Feature | Powered By |
|---------|-----------|
| 🔬 Cancer image analysis (8 types) | HuggingFace fine-tuned models |
| 🌡️ Grad-CAM heatmap overlay | Local EfficientNet-B0 (PyTorch) |
| 📋 Symptom risk checker | Groq LLaMA 3.1-70B |
| 💬 Oncology AI chatbot | Groq LLaMA 3.1-70B |

## Cancer Models Used

| Cancer Type | HuggingFace Model |
|------------|-------------------|
| Brain Tumor | Falconsai/brain_tumor_detection |
| Lung / Chest | nickmuchi/vit-finetuned-chest-xray-pneumonia |
| Breast | dima806/breast-cancer-ultrasound-image-detection |
| Colorectal | dima806/colon_cancer_cells_image_detection |
| Skin Cancer | Anwarkh1/Skin_Cancer-Image_Classification |
| Cervical | Devarshi/CervicalCancer_Classification |
| Kidney | dima806/kidney_cancer_image_detection |
| Oral | dima806/oral_cancer_image_detection |

> ⚠️ For research/educational purposes only. Not a medical diagnostic tool.
