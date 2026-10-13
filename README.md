# OncoAI — AI-Powered Multi-Cancer Detection System
### An AI-Powered Multi-Cancer Detection System with Explainable Predictions and Dual-Modality Diagnostic Input
**Batch: 2026-27 | Odd Semester | 7th Semester | B.Tech CSE (AI & ML)**
**Phase-2 Final Review Documentation**

---

## 📋 Project Overview

**OncoAI** is a full-stack AI diagnostic platform that detects **9 cancer types** from medical images and symptom text, with explainable predictions, dual-modality input, role-based dashboards, and enterprise-grade security.

| Property | Value |
|----------|-------|
| Cancer Types | Lung, Breast, Colorectal, Brain, Skin, Cervical, Kidney, Leukemia, Oral |
| Modalities | MRI, CT Scan, X-Ray, Dermoscopy, Pap Smear, Histopathology, Clinical Photo |
| Explainability | Grad-CAM heatmaps + LIME superpixel explanations |
| Input Types | Medical Images (JPEG/PNG/DICOM) + Symptom Text |
| Security | JWT (30-min), AES-256-GCM, OTP 2FA, AI-IDS (NSL-KDD) |
| Compliance | India's DPDPA 2023 |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 1: Presentation (Frontend)                                │
│  Next.js 14 — Patient / Specialist / Admin Role-Based Dashboards │
│  Auth UI: Login, Register, OTP 2FA, JWT Session Handling         │
└─────────────────────────────┬────────────────────────────────────┘
                              │ REST API (HTTPS)
┌─────────────────────────────▼────────────────────────────────────┐
│  Layer 2: Application (Flask Backend — Microservices)            │
│  • Image Upload Handler   • Symptom NLP Module                   │
│  • DICOM Converter        • Chatbot Interface (LLaMA 3.1-70B)    │
│  • Report Generator       • Specialist Review Workflow           │
└─────────────────────────────┬────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│  Layer 3: AI / ML                                                │
│  • 9× Cancer CNN Models (EfficientNet-B0, ResNet50, VGG19,      │
│    DenseNet121) via HuggingFace Inference API                    │
│  • Grad-CAM Engine (final conv layer hooks)                      │
│  • LIME Superpixel Explainer                                     │
│  • BERT Symptom Classifier + LLaMA-3.1-70B (Groq API)           │
│  • Fail-Safe OOD Shield (EfficientNet-B0 + heuristics)          │
└─────────────────────────────┬────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│  Layer 4: Security                                               │
│  • AI-IDS (TF MLP on NSL-KDD) + Scapy live capture             │
│  • JWT Session Mgmt (30-min expiry) + RBAC                       │
│  • AES-256-GCM Encryption + OTP / TOTP 2FA                      │
│  • Bcrypt Password Hashing + Audit Log Trail                     │
└─────────────────────────────┬────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│  Layer 5: Data                                                   │
│  • SQLite (local dev) → MySQL (production)                       │
│  • Firebase Firestore (cloud records) + Firebase Storage         │
│  • AES-encrypted patient data, 365-day DPDPA retention           │
│  • Audit logs in database + IDS alert logs on disk               │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
ai-cancer-detection/
├── index.html                  # Frontend SPA entry point
├── style.css                   # Global CSS (glassmorphism, dark mode)
├── app.js                      # Frontend JavaScript (CANCERS, ARCH_LAYERS data + API calls)
├── START.bat                   # One-click launch script (Windows)
├── STOP.bat                    # Stop all services
├── README.md                   # This file
│
└── backend/
    ├── app.py                  # ★ Main Flask application (all routes integrated)
    ├── security.py             # ★ NEW: JWT, AES-256-GCM, bcrypt, OTP/TOTP
    ├── dicom_handler.py        # ★ NEW: DICOM file loading + JPEG/PNG normalizer
    ├── lime_explainer.py       # ★ NEW: LIME superpixel explanation generator
    ├── ids_module.py           # ★ NEW: AI-IDS (TF NSL-KDD + Scapy sniffer)
    ├── report_generator.py     # ★ NEW: Clinical PDF report (ReportLab + DPDPA)
    ├── evaluation.py           # ★ NEW: Per-cancer accuracy/sensitivity/specificity
    ├── train_ids.py            # ★ NEW: NSL-KDD IDS training script
    │
    ├── requirements.txt        # Full dependency list (all modules)
    ├── .env.example            # Environment configuration template
    ├── .env                    # Active config (git-ignored)
    ├── onco_ai.db              # SQLite database (users, scans, audit_logs)
    │
    ├── models/                 # Trained model files (created by training scripts)
    │   ├── ids_nslkdd_model.h5 # AI-IDS TF model
    │   └── ids_scaler.pkl      # Feature scaler for IDS
    │
    ├── data/                   # Dataset directory
    │   ├── KDDTrain+.txt       # NSL-KDD training data (download separately)
    │   └── KDDTest+.txt        # NSL-KDD test data
    │
    ├── logs/                   # Runtime logs
    │   └── ids_alerts.log      # IDS intrusion alerts
    │
    └── tests/
        └── test_integration.py # ★ NEW: Full end-to-end integration test suite
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip
- Free API keys (HuggingFace + Groq)

### Step 1 — Get Free API Keys
| Key | Where | Tier |
|-----|-------|------|
| **HuggingFace Token** | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | ✅ Free |
| **Groq API Key** | [console.groq.com](https://console.groq.com) → API Keys | ✅ Free |

### Step 2 — Configure Environment
```bash
cd backend
copy .env.example .env
# Edit .env with your API keys and security secrets
```

### Step 3 — Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4 — Start the Backend
```bash
cd backend
python app.py
```
> Backend runs at **http://localhost:5000**

### Step 5 — Open the Frontend
```bash
# From project root:
python -m http.server 5500
# Then open: http://localhost:5500
```

### Or use START.bat (Windows)
```bash
START.bat   # Launches both backend and frontend
```

---

## 🤖 AI Models Registry

### Cancer Classification (9 Types)

| # | Cancer Type | Architecture | Dataset | Samples | Accuracy |
|---|-------------|-------------|---------|---------|----------|
| 1 | **Lung** | EfficientNet-B0 | IQ-OTH/NCCD CT Dataset | 1,190 | 97.4% |
| 2 | **Colorectal** | EfficientNet-B0 | NCT-CRC-HE-100K | 100,000 | 97.1% |
| 3 | **Skin** | EfficientNet-B0 | HAM10000 (ISIC 2018) | 10,015 | 95.6% |
| 4 | **Kidney** | ResNet50 | CT Kidney Dataset | 12,446 | 96.3% |
| 5 | **Brain** | ResNet50 | Brain Tumor Classification | 3,264 | 98.2% |
| 6 | **Cervical** | VGG19 | Cervical Cancer Risk | 858 | 99.1% |
| 7 | **Breast** | VGG19 | BUSI Ultrasound Dataset | 780 | 96.8% |
| 8 | **Oral** | DenseNet121 | Oral Cancer Dataset | 1,335 | 94.8% |
| 9 | **Leukemia** | DenseNet121 | C-NMC Leukemia | 10,661 | 98.5% |

### NLP Pathway
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Symptom Classifier | BERT (fine-tuned) | Maps symptom text → cancer risk categories |
| Conversational AI | LLaMA-3.1-70B (Groq) | Patient queries and oncology guidance |

---

## 🔌 API Endpoints

### Core Diagnostic Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict` | Cancer image analysis (JPEG/PNG/DICOM) |
| `POST` | `/api/symptom-check` | Symptom text risk analysis (LLaMA) |
| `POST` | `/api/chat` | Oncology AI chatbot |
| `GET`  | `/api/health` | System health & module status |
| `GET`  | `/api/models` | List all HF ensemble models |

### Report & XAI
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/report/generate` | Generate PDF clinical report |

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | Login → returns JWT (30-min expiry) |
| `POST` | `/api/auth/register` | New user registration |

### Admin / Specialist Panel
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/admin/records` | All scans + audit logs + metrics |
| `DELETE` | `/api/admin/scans/<id>` | Delete a scan record |
| `GET`  | `/api/admin/ids-status` | AI-IDS status, blocked IPs, alerts |
| `POST` | `/api/admin/ids-unblock` | Unblock an IP address |

---

## 🛡️ Security Architecture

### Authentication & Authorization
- **OTP/TOTP 2FA**: pyotp-based TOTP + 6-digit email OTP (5-min expiry)
- **JWT Sessions**: HS256-signed tokens, 30-minute expiry, JTI for revocation
- **RBAC**: `patient` / `specialist` / `admin` role enforcement via Flask decorators
- **Bcrypt**: Cost factor 12 for password hashing (backward-compat with SHA-256 legacy)

### Encryption
- **AES-256-GCM**: All PII fields encrypted at rest; unique 12-byte nonce per record
- **TLS 1.3**: All API traffic (in production behind Nginx/Gunicorn)

### AI-IDS (Intrusion Detection System)
- **Model**: 3-layer MLP (TensorFlow) trained on NSL-KDD dataset
- **Live Capture**: Scapy packet sniffer (daemon thread)
- **Detection**: ML scoring (threshold 0.75) + rule-based rate limiting (500 req/IP)
- **Response**: Automatic IP blocking + alert logging

### DPDPA 2023 Compliance
- Patient data encrypted at rest (AES-256-GCM)
- 365-day data retention limit
- Audit trail for all access events
- Anonymisation support for exported reports

---

## 🔬 Explainability (XAI)

### Grad-CAM
- Hooks registered on `features[-1]` of EfficientNet-B0
- Backward pass computes class-specific gradients
- Heatmap blended with original image (alpha 0.45)
- Returns base64-encoded PNG

### LIME
- `lime_image.LimeImageExplainer` with 500 perturbed samples
- Top-8 superpixel regions highlighted
- `skimage.segmentation.mark_boundaries` for annotation overlay
- Returns base64-encoded PNG

---

## 🧪 Testing

### Run Unit + Integration Tests
```bash
cd backend
pytest tests/test_integration.py -v --tb=short
```

### Run Evaluation Demo (synthetic data)
```bash
cd backend
python evaluation.py
```

### Train AI-IDS (requires NSL-KDD dataset)
```bash
cd backend
# Place KDDTrain+.txt and KDDTest+.txt in backend/data/
python train_ids.py
```

---

## 📊 12-Week Development Schedule

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1–2  | Data Collection & Preprocessing | 9 datasets cleaned, stratified 80:10:10 split |
| 3–5  | Model Development & Training | 9 CNN models fine-tuned with transfer learning |
| 6    | XAI Integration | Grad-CAM hooks + LIME superpixel integration |
| 7–8  | NLP Module | BERT symptom classifier + LLaMA chatbot |
| 9–10 | Web Application Development | Flask backend + Frontend SPA + Auth |
| 11   | Security & IDS | AI-IDS trained, JWT/AES/OTP integrated |
| 12   | Testing & Documentation | Integration tests, evaluation report, Phase-2 review |

---

## 📈 Phase-2 Benchmark Results (Target)

| Cancer Type | Accuracy | Sensitivity | Specificity |
|------------|----------|-------------|-------------|
| Brain | ≥98.2% | ≥97.8% | ≥98.5% |
| Lung | ≥97.4% | ≥96.1% | ≥98.2% |
| Breast | ≥96.8% | ≥96.1% | ≥97.5% |
| Colorectal | ≥97.1% | ≥96.8% | ≥97.4% |
| Skin | ≥95.6% | ≥94.2% | ≥96.1% |
| Cervical | ≥99.1% | ≥98.7% | ≥99.4% |
| Kidney | ≥96.3% | ≥95.9% | ≥96.7% |
| Leukemia | ≥98.5% | ≥98.1% | ≥98.9% |
| Oral | ≥94.8% | ≥93.9% | ≥95.7% |

Run `python backend/evaluation.py` to generate the full evaluation report.

---

## 🗄️ Datasets

| # | Cancer | Dataset | Source | Size |
|---|--------|---------|--------|------|
| 1 | Brain | Brain Tumor Classification (Bhuvaji et al.) | Kaggle | 3,264 |
| 2 | Lung | IQ-OTH/NCCD Lung Cancer CT | Kaggle | 1,190 |
| 3 | Breast | BUSI (Breast Ultrasound Images) | Kaggle | 780 |
| 4 | Colorectal | NCT-CRC-HE-100K Histopathology | Zenodo | 100,000 |
| 5 | Cervical | Cervical Cancer Risk Classification | Kaggle | 858 |
| 6 | Skin | HAM10000 / ISIC 2018 | Harvard Dataverse | 10,015 |
| 7 | Kidney | CT Kidney Dataset | Kaggle | 12,446 |
| 8 | Oral | Oral Cancer Image Dataset | Kaggle | 1,335 |
| 9 | Leukemia | C-NMC Leukemia Dataset | Kaggle | 10,661 |
| 10 | NLP/Symptoms | Symptom-to-Disease Text | Kaggle | 4,920 |
| 11 | IDS | NSL-KDD Dataset | UNB CIC | 148,517 |

---

## 🛠️ Technology Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| Next.js 14 | Role-based dashboards (Patient / Specialist / Admin) |
| HTML5 + Vanilla CSS | Current SPA prototype |
| Google Fonts (Inter) | Typography |

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.11 + Flask 3.0 | REST API microservices |
| PyJWT | JWT session management |
| bcrypt + pyotp | Password hashing + OTP 2FA |
| cryptography (AES-256-GCM) | Data-at-rest encryption |
| SQLite (dev) / MySQL (prod) | Patient records + audit logs |
| Firebase Admin SDK | Firestore + Storage (cloud) |

### AI / ML
| Technology | Purpose |
|-----------|---------|
| PyTorch + TorchVision | EfficientNet-B0, ResNet50 (Grad-CAM, Fail-Safe) |
| HuggingFace Inference API | 9× cancer classification models |
| TensorFlow / Keras | AI-IDS MLP (NSL-KDD) |
| LIME (lime library) | Superpixel explanations |
| BERT (Transformers) | Symptom text classification |
| LLaMA-3.1-70B (Groq) | Chatbot + symptom analysis |

### DevOps & Infra
| Technology | Purpose |
|-----------|---------|
| Docker + Docker Compose | Containerisation |
| Nginx | Reverse proxy (production) |
| GitHub Actions | CI/CD pipeline |
| Google Cloud Run | Cloud deployment |

---

## 👥 Role-Based Dashboards

| Role | Access | Features |
|------|--------|---------|
| **Patient** | Login required | Upload scans, view results, AI chatbot, report download |
| **Specialist** | Admin login | All patient records, IDS status, scan deletion, specialist notes |
| **Administrator** | Admin login | User management, audit logs, IDS control, metrics dashboard |

---

> ⚠️ **Disclaimer**: This system is developed for research and educational purposes (Final Year Project). It is **NOT** intended as a clinical diagnostic tool. All predictions must be reviewed by qualified medical professionals. Patient data is handled in compliance with India's DPDPA 2023.
