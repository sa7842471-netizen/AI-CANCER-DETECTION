"""
OncoAI — LIME Explainability Module
Generates LIME superpixel explanations for cancer image predictions.
Complements Grad-CAM heatmaps for dual-layer XAI.

Batch 2026-27 | Odd Semester | 7th Sem
"""

import io
import base64
import numpy as np
from PIL import Image

try:
    from lime import lime_image
    from skimage.segmentation import mark_boundaries
    LIME_AVAILABLE = True
except ImportError:
    LIME_AVAILABLE = False

import torch
import torchvision.transforms as transforms
import torchvision.models as tv_models


# ── Shared classifier (EfficientNet-B0) — reused from app.py ──────────────────
_preprocess_lime = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _predict_fn(images_np: np.ndarray, model) -> np.ndarray:
    """
    LIME classifier function.
    Accepts a batch of (H, W, C) uint8 images, returns probability arrays.
    """
    batch = []
    for img_np in images_np:
        pil = Image.fromarray(img_np.astype(np.uint8))
        batch.append(_preprocess_lime(pil))
    tensor = torch.stack(batch)
    with torch.no_grad():
        out   = model(tensor)
        probs = torch.nn.functional.softmax(out, dim=1)
    return probs.numpy()


def generate_lime_explanation(
    img_bytes: bytes,
    model,
    num_samples: int = 500,
    num_features: int = 8,
    positive_only: bool = True,
) -> str | None:
    """
    Generate a LIME superpixel explanation image.

    Args:
        img_bytes:     Raw image bytes (JPEG/PNG).
        model:         PyTorch model (EfficientNet-B0 or similar) in eval mode.
        num_samples:   Number of perturbed samples for LIME (default 500).
        num_features:  Top-K superpixel regions to highlight (default 8).
        positive_only: Show only regions that positively contribute.

    Returns:
        Base64-encoded PNG of the LIME-annotated image, or None on failure.
    """
    if not LIME_AVAILABLE:
        return None

    try:
        # Convert to numpy (H, W, C)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((224, 224))
        img_np = np.array(img)

        explainer    = lime_image.LimeImageExplainer()
        explanation  = explainer.explain_instance(
            img_np,
            classifier_fn=lambda imgs: _predict_fn(imgs, model),
            top_labels=1,
            hide_color=0,
            num_samples=num_samples,
            random_seed=42,
        )

        top_label = explanation.top_labels[0]
        temp, mask = explanation.get_image_and_mask(
            top_label,
            positive_only=positive_only,
            num_features=num_features,
            hide_rest=False,
        )

        # Overlay boundaries onto original image
        annotated = mark_boundaries(temp / 255.0, mask)
        annotated = (annotated * 255).clip(0, 255).astype(np.uint8)

        pil_out = Image.fromarray(annotated)
        buf     = io.BytesIO()
        pil_out.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    except Exception as e:
        print(f"[LIME] Error generating explanation: {e}")
        return None


def generate_lime_heatmap(img_bytes: bytes, model) -> dict:
    """
    Wrapper that returns a structured dict for the API response.
    Compatible with the existing Grad-CAM response format.
    """
    b64 = generate_lime_explanation(img_bytes, model)
    return {
        "lime_available": LIME_AVAILABLE,
        "lime_image":     b64,
        "method":         "LIME (Local Interpretable Model-Agnostic Explanations)",
        "description":    "Highlighted superpixel regions that most influenced the cancer prediction.",
    }
