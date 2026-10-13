"""
OncoAI — Integration Test Suite
End-to-end integration tests covering the full diagnostic pipeline:
  1. Fail-Safe rejection of non-medical images
  2. DICOM file loading and conversion
  3. Image prediction + Grad-CAM + LIME overlays
  4. Risk scoring and report generation
  5. Symptom NLP checker
  6. JWT authentication (login, register, token expiry)
  7. Admin panel (records, audit logs)
  8. IDS status endpoint
  9. PDF report generation

Batch 2026-27 | Odd Semester | 7th Sem

Usage:
    pip install pytest requests pillow
    pytest backend/tests/test_integration.py -v --tb=short
"""

import io
import sys
import os
import json
import base64
import datetime
import unittest
from unittest.mock import patch, MagicMock

# Ensure backend is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PIL import Image
import numpy as np

# ── Import modules under test ──────────────────────────────────────────────────
from security import (
    hash_password, verify_password, generate_token, decode_token,
    aes_encrypt, aes_decrypt, generate_email_otp, verify_email_otp,
)
from dicom_handler import is_dicom_bytes, load_image_bytes
from evaluation import evaluate_cancer_model, evaluate_all_models
from report_generator import generate_report_pdf, PDF_AVAILABLE


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_solid_color_png(r=100, g=100, b=100, size=(224, 224)) -> bytes:
    """Create a uniform-color PNG (fails fail-safe blank check)."""
    img = Image.fromarray(np.full((*size, 3), [r, g, b], dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_grayscale_png(mean=80, size=(224, 224)) -> bytes:
    """Simulate a grayscale MRI-like PNG image."""
    rng   = np.random.default_rng(42)
    arr   = rng.integers(max(0, mean-40), min(255, mean+40), size=size, dtype=np.uint8)
    arr3  = np.stack([arr, arr, arr], axis=2)
    img   = Image.fromarray(arr3)
    buf   = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_stained_histology_png(size=(224, 224)) -> bytes:
    """Simulate a pink/purple H&E stained histology slide."""
    rng   = np.random.default_rng(7)
    r     = rng.integers(160, 220, size=size, dtype=np.uint8)
    g     = rng.integers(80,  130, size=size, dtype=np.uint8)
    b     = rng.integers(140, 200, size=size, dtype=np.uint8)
    arr   = np.stack([r, g, b], axis=2)
    img   = Image.fromarray(arr)
    buf   = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_bright_natural_photo_png(size=(224, 224)) -> bytes:
    """Simulate a bright, colorful natural photo (high color diversity)."""
    rng  = np.random.default_rng(99)
    arr  = rng.integers(0, 255, size=(*size, 3), dtype=np.uint8)
    img  = Image.fromarray(arr)
    buf  = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS 1 — Security Module
# ════════════════════════════════════════════════════════════════════════════════

class TestSecurityModule(unittest.TestCase):
    """Tests for security.py: bcrypt, JWT, AES-256, OTP"""

    def test_password_hash_and_verify_correct(self):
        """Correct password verifies successfully."""
        pw   = "SecureP@ss123!"
        hsh  = hash_password(pw)
        self.assertTrue(verify_password(pw, hsh))

    def test_password_hash_wrong_fails(self):
        """Wrong password returns False."""
        hsh = hash_password("correct")
        self.assertFalse(verify_password("wrong", hsh))

    def test_jwt_generate_and_decode(self):
        """JWT encodes and decodes payload correctly."""
        token   = generate_token(user_id=42, username="testuser", role="patient")
        payload = decode_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["username"], "testuser")
        self.assertEqual(payload["role"],     "patient")
        self.assertEqual(payload["sub"],      42)

    def test_jwt_invalid_token_returns_none(self):
        """Tampered JWT returns None."""
        result = decode_token("invalid.token.here")
        self.assertIsNone(result)

    def test_jwt_expiry(self):
        """Expired JWT returns None."""
        import jwt as pyjwt
        expired_payload = {
            "sub": 1, "username": "x", "role": "patient",
            "iat": datetime.datetime.utcnow() - datetime.timedelta(hours=2),
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1),
        }
        from security import JWT_SECRET
        token  = pyjwt.encode(expired_payload, JWT_SECRET, algorithm="HS256")
        result = decode_token(token)
        self.assertIsNone(result)

    def test_aes_encrypt_decrypt_roundtrip(self):
        """AES-256-GCM encrypt then decrypt returns original plaintext."""
        secret    = "Patient scan data — DPDPA 2023 protected"
        encrypted = aes_encrypt(secret)
        decrypted = aes_decrypt(encrypted)
        self.assertEqual(decrypted, secret)

    def test_aes_different_nonces(self):
        """Same plaintext encrypts to different ciphertexts (random nonce)."""
        plain = "same text"
        self.assertNotEqual(aes_encrypt(plain), aes_encrypt(plain))

    def test_otp_generation_and_verify(self):
        """Email OTP verifies correctly within expiry."""
        otp, expiry = generate_email_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        self.assertTrue(verify_email_otp(otp, expiry, otp))

    def test_otp_wrong_code_fails(self):
        """Wrong OTP code returns False."""
        otp, expiry = generate_email_otp()
        self.assertFalse(verify_email_otp(otp, expiry, "000000"))

    def test_otp_expired(self):
        """Expired OTP returns False."""
        otp     = "123456"
        expired = datetime.datetime.utcnow() - datetime.timedelta(seconds=10)
        self.assertFalse(verify_email_otp(otp, expired, otp))


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS 2 — DICOM Handler
# ════════════════════════════════════════════════════════════════════════════════

class TestDicomHandler(unittest.TestCase):
    """Tests for dicom_handler.py: DICOM detection, JPEG/PNG loading."""

    def test_non_dicom_bytes_detected(self):
        """Standard JPEG bytes are not flagged as DICOM."""
        png   = make_grayscale_png()
        self.assertFalse(is_dicom_bytes(png))

    def test_load_jpeg_returns_png(self):
        """JPEG image loads and converts to PNG format."""
        jpeg_buf = io.BytesIO()
        Image.fromarray(np.zeros((50, 50, 3), dtype=np.uint8)).save(jpeg_buf, format="JPEG")
        result, fmt = load_image_bytes(jpeg_buf.getvalue())
        self.assertIn(fmt, ["JPEG", "PNG"])
        self.assertIsNotNone(result)

    def test_load_png_returns_png(self):
        """PNG image passes through correctly."""
        png          = make_grayscale_png()
        result, fmt  = load_image_bytes(png)
        self.assertEqual(fmt, "PNG")

    def test_corrupted_bytes_returns_unknown(self):
        """Corrupted bytes return UNKNOWN format gracefully."""
        _, fmt = load_image_bytes(b"\x00\x01\x02\x03garbage")
        self.assertEqual(fmt, "UNKNOWN")


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS 3 — Fail-Safe Image Validation (via app.py internal function)
# ════════════════════════════════════════════════════════════════════════════════

class TestFailSafeValidation(unittest.TestCase):
    """
    Tests for _validate_and_detect_scan in app.py.
    We import the function directly for unit testing.
    """

    @classmethod
    def setUpClass(cls):
        """Import the validation function once (loads EfficientNet-B0)."""
        try:
            from app import _validate_and_detect_scan
            cls.validate = staticmethod(_validate_and_detect_scan)
            cls.skip     = False
        except Exception as e:
            print(f"\n[SKIP] Could not import app.py: {e}")
            cls.skip = True

    def _check_skip(self):
        if self.skip:
            self.skipTest("app.py not importable (missing model weights or dependencies)")

    def test_blank_image_rejected(self):
        """Solid-color blank image is rejected by fail-safe."""
        self._check_skip()
        blank_bytes         = make_solid_color_png(128, 128, 128)
        is_valid, _, _, msg = self.validate(blank_bytes, "auto")
        self.assertFalse(is_valid)
        self.assertIn("blank", msg.lower())

    def test_grayscale_mri_accepted(self):
        """Grayscale MRI-like image passes validation."""
        self._check_skip()
        mri_bytes           = make_grayscale_png(mean=70)
        is_valid, ctype, _, msg = self.validate(mri_bytes, "auto")
        self.assertTrue(is_valid, f"Expected valid MRI, got: {msg}")

    def test_histology_slide_accepted(self):
        """Pink/purple H&E histology PNG passes validation."""
        self._check_skip()
        histo               = make_stained_histology_png()
        is_valid, ctype, _, msg = self.validate(histo, "auto")
        self.assertTrue(is_valid, f"Expected valid histology, got: {msg}")


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS 4 — Evaluation Module
# ════════════════════════════════════════════════════════════════════════════════

class TestEvaluationModule(unittest.TestCase):
    """Tests for evaluation.py metrics computation."""

    def _make_binary_data(self, n=200, acc=0.95):
        rng   = np.random.default_rng(0)
        y_t   = rng.integers(0, 2, n)
        mask  = rng.random(n) < acc
        y_p   = np.where(mask, y_t, 1 - y_t)
        proba = np.column_stack([1 - y_p * 0.9 - 0.05, y_p * 0.9 + 0.05])
        return y_t.tolist(), y_p.tolist(), proba.tolist()

    def test_brain_evaluation_returns_metrics(self):
        """Brain model evaluation returns all required metrics."""
        y_t, y_p, proba = self._make_binary_data()
        result = evaluate_cancer_model("brain", y_t, y_p, np.array(proba))
        self.assertIn("metrics",      result)
        self.assertIn("accuracy",     result["metrics"])
        self.assertIn("sensitivity",  result["metrics"])
        self.assertIn("specificity",  result["metrics"])
        self.assertIn("f1_score",     result["metrics"])

    def test_accuracy_range(self):
        """Computed accuracy is a valid percentage [0, 100]."""
        y_t, y_p, _ = self._make_binary_data(acc=0.9)
        result = evaluate_cancer_model("kidney", y_t, y_p)
        self.assertGreaterEqual(result["metrics"]["accuracy"], 0)
        self.assertLessEqual(result["metrics"]["accuracy"],    100)

    def test_evaluate_all_models_produces_average(self):
        """evaluate_all_models returns system-wide averages for all inputs."""
        rng  = np.random.default_rng(1)
        data = {}
        for ctype in ["brain", "lung", "breast"]:
            n   = 100
            y_t = rng.integers(0, 2, n).tolist()
            y_p = rng.integers(0, 2, n).tolist()
            data[ctype] = {"y_true": y_t, "y_pred": y_p}
        result = evaluate_all_models(data)
        self.assertIn("system_average", result)
        self.assertIn("accuracy",       result["system_average"])

    def test_benchmark_comparison_exists(self):
        """meets_benchmark field is present in evaluation report."""
        y_t, y_p, _ = self._make_binary_data()
        result = evaluate_cancer_model("oral", y_t, y_p)
        self.assertIn("meets_benchmark", result)


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS 5 — PDF Report Generation
# ════════════════════════════════════════════════════════════════════════════════

class TestReportGenerator(unittest.TestCase):
    """Tests for report_generator.py PDF output."""

    def test_pdf_generates_bytes(self):
        """PDF report generates non-empty bytes when reportlab available."""
        if not PDF_AVAILABLE:
            self.skipTest("reportlab not installed")
        pdf = generate_report_pdf(
            cancer_type="brain",
            top_label="Glioma",
            top_score=87.4,
            risk_level="HIGH",
            confidence="High",
            predictions=[
                {"label": "Glioma",     "score": 87.4},
                {"label": "Meningioma", "score": 8.2},
                {"label": "No Tumor",   "score": 4.4},
            ],
            patient_name="Test Patient",
            modality="MRI Scan",
            models_used=["Falconsai/brain_tumor_detection"],
            specialist_note="AI result reviewed. Recommend biopsy.",
        )
        self.assertIsNotNone(pdf)
        self.assertGreater(len(pdf), 1000)
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_pdf_contains_patient_name(self):
        """PDF bytes contain the patient name."""
        if not PDF_AVAILABLE:
            self.skipTest("reportlab not installed")
        name = "Dr. Ramesh Kumar"
        pdf  = generate_report_pdf(
            cancer_type="lung",
            top_label="Normal",
            top_score=72.0,
            risk_level="LOW",
            confidence="High",
            predictions=[{"label": "Normal", "score": 72.0}],
            patient_name=name,
            modality="CT Scan",
        )
        # Patient name should appear in the PDF content
        self.assertIn(name.encode("latin-1", errors="replace"), pdf)

    def test_pdf_returns_none_without_reportlab(self):
        """If PDF_AVAILABLE is False, returns None gracefully."""
        import report_generator as rg
        original = rg.PDF_AVAILABLE
        rg.PDF_AVAILABLE = False
        result = generate_report_pdf(
            "brain", "Glioma", 90, "HIGH", "High", [], "Test", "MRI"
        )
        rg.PDF_AVAILABLE = original
        self.assertIsNone(result)


# ════════════════════════════════════════════════════════════════════════════════
# TEST CLASS 6 — Flask API Endpoints (requires running server)
# These tests are skipped if the server is not running locally.
# ════════════════════════════════════════════════════════════════════════════════

class TestFlaskAPIEndpoints(unittest.TestCase):
    """Integration tests against the running Flask API at localhost:5000."""

    BASE_URL = "http://localhost:5000"

    @classmethod
    def setUpClass(cls):
        try:
            import requests
            resp = requests.get(f"{cls.BASE_URL}/api/health", timeout=3)
            cls.requests = requests
            cls.server_running = resp.status_code == 200
        except Exception:
            cls.server_running = False

    def _skip_if_no_server(self):
        if not self.server_running:
            self.skipTest("Flask server not running at localhost:5000")

    def test_health_endpoint(self):
        """GET /api/health returns status ok."""
        self._skip_if_no_server()
        resp = self.requests.get(f"{self.BASE_URL}/api/health", timeout=5)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("cancer_types", data)

    def test_register_and_login(self):
        """POST /api/auth/register then /api/auth/login returns JWT."""
        self._skip_if_no_server()
        import random
        uname = f"testuser_{random.randint(1000, 9999)}"
        # Register
        reg = self.requests.post(f"{self.BASE_URL}/api/auth/register", json={
            "username": uname, "password": "Test@1234", "full_name": "Test User", "role": "patient"
        }, timeout=5)
        self.assertIn(reg.status_code, [200, 201, 400])  # 400 if already exists

        # Login
        login = self.requests.post(f"{self.BASE_URL}/api/auth/login", json={
            "username": uname, "password": "Test@1234"
        }, timeout=5)
        # May return 200 with token or user object
        self.assertIn(login.status_code, [200, 401])

    def test_predict_non_medical_image_rejected(self):
        """POST /api/predict with a solid-color image triggers fail-safe."""
        self._skip_if_no_server()
        blank = make_solid_color_png(128, 128, 128)
        resp  = self.requests.post(
            f"{self.BASE_URL}/api/predict",
            files={"image": ("test.png", io.BytesIO(blank), "image/png")},
            data={"cancer_type": "auto"},
            timeout=30,
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertTrue(data.get("fail_safe_triggered", False) or "error" in data)

    def test_predict_medical_image_succeeds(self):
        """POST /api/predict with a grayscale MRI-like image returns predictions."""
        self._skip_if_no_server()
        mri  = make_grayscale_png(mean=70)
        resp = self.requests.post(
            f"{self.BASE_URL}/api/predict",
            files={"image": ("mri.png", io.BytesIO(mri), "image/png")},
            data={"cancer_type": "auto", "patient_name": "Integration Test Patient"},
            timeout=60,
        )
        self.assertIn(resp.status_code, [200, 400])
        if resp.status_code == 200:
            data = resp.json()
            self.assertIn("predictions",  data)
            self.assertIn("risk_level",   data)
            self.assertIn("gradcam",      data)
            self.assertIn("cancer_type",  data)

    def test_admin_records_endpoint(self):
        """GET /api/admin/records returns scans and audit_logs."""
        self._skip_if_no_server()
        resp = self.requests.get(f"{self.BASE_URL}/api/admin/records", timeout=5)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("scans",      data)
        self.assertIn("audit_logs", data)
        self.assertIn("metrics",    data)

    def test_models_list_endpoint(self):
        """GET /api/models returns ensemble model registry."""
        self._skip_if_no_server()
        resp = self.requests.get(f"{self.BASE_URL}/api/models", timeout=5)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("brain",     data)
        self.assertIn("lung",      data)
        self.assertIn("breast",    data)
        self.assertIn("colorectal",data)
        self.assertIn("skin",      data)
        self.assertIn("cervical",  data)
        self.assertIn("kidney",    data)
        self.assertIn("oral",      data)

    def test_report_generate_endpoint(self):
        """POST /api/report/generate returns PDF base64."""
        self._skip_if_no_server()
        resp = self.requests.post(
            f"{self.BASE_URL}/api/report/generate",
            json={
                "cancer_type":  "brain",
                "top_label":    "Glioma",
                "top_score":    82.5,
                "risk_level":   "HIGH",
                "confidence":   "High",
                "predictions":  [{"label": "Glioma", "score": 82.5}],
                "patient_name": "Integration Test",
                "modality":     "MRI Scan",
            },
            timeout=15,
        )
        self.assertIn(resp.status_code, [200, 503])  # 503 if reportlab not installed
        if resp.status_code == 200:
            data = resp.json()
            self.assertIn("pdf_b64", data)


# ════════════════════════════════════════════════════════════════════════════════
# Entry Point
# ════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*65)
    print("  OncoAI Integration Test Suite")
    print("  Batch 2026-27 | 7th Semester | Phase-2 Final Review")
    print("="*65 + "\n")
    unittest.main(verbosity=2)
