"""
OncoAI — Evaluation & Metrics Module
Computes per-cancer-type accuracy, sensitivity (recall), specificity, F1, AUC-ROC.
Used for Phase-2 final review benchmarking and research paper data.

Batch 2026-27 | Odd Semester | 7th Sem

Usage:
    # Run the built-in demo with synthetic data:
    python backend/evaluation.py

    # Or import and call in tests:
    from backend.evaluation import evaluate_cancer_model, print_evaluation_report
"""

import json
import numpy as np
from typing import Optional

try:
    from sklearn.metrics import (
        accuracy_score, recall_score, f1_score,
        confusion_matrix, classification_report,
        roc_auc_score, average_precision_score,
    )
    SK_AVAILABLE = True
except ImportError:
    SK_AVAILABLE = False


# ── Per-Cancer Model Metadata ─────────────────────────────────────────────────
CANCER_MODEL_MAP = {
    "lung":       {"model": "EfficientNet-B0",  "dataset": "IQ-OTH/NCCD Lung Cancer CT",       "samples": 1190,  "classes": ["Normal","Pneumonia","COVID"]},
    "colorectal": {"model": "EfficientNet-B0",  "dataset": "NCT-CRC-HE-100K Histopathology",    "samples": 100000,"classes": ["colon_aca","colon_n"]},
    "skin":       {"model": "EfficientNet-B0",  "dataset": "HAM10000 (ISIC 2018)",              "samples": 10015, "classes": ["akiec","bcc","bkl","df","mel","nv","vasc"]},
    "kidney":     {"model": "ResNet50",          "dataset": "CT Kidney Dataset – Kaggle",        "samples": 12446, "classes": ["Normal","Tumor"]},
    "brain":      {"model": "ResNet50",          "dataset": "Brain Tumor Classification – Kaggle","samples": 3264,  "classes": ["glioma","meningioma","no_tumor","pituitary"]},
    "cervical":   {"model": "VGG19",             "dataset": "Cervical Cancer Risk Classification","samples": 858,   "classes": ["Dyskeratotic","Koilocytotic","Metaplastic","Parabasal","Superficial-Intermediate"]},
    "breast":     {"model": "VGG19",             "dataset": "BUSI Breast Ultrasound Dataset",    "samples": 780,   "classes": ["benign","malignant","normal"]},
    "oral":       {"model": "DenseNet121",        "dataset": "Oral Cancer Image Dataset",         "samples": 1335,  "classes": ["Normal","OSCC"]},
    "leukemia":   {"model": "DenseNet121",        "dataset": "C-NMC Leukemia Dataset",            "samples": 10661, "classes": ["all","hem"]},
}

# ── Target benchmark metrics (from literature / project proposal) ─────────────
TARGET_BENCHMARKS = {
    "lung":       {"accuracy": 97.4, "sensitivity": 96.1, "specificity": 98.2},
    "colorectal": {"accuracy": 97.1, "sensitivity": 96.8, "specificity": 97.4},
    "skin":       {"accuracy": 95.6, "sensitivity": 94.2, "specificity": 96.1},
    "kidney":     {"accuracy": 96.3, "sensitivity": 95.9, "specificity": 96.7},
    "brain":      {"accuracy": 98.2, "sensitivity": 97.8, "specificity": 98.5},
    "cervical":   {"accuracy": 99.1, "sensitivity": 98.7, "specificity": 99.4},
    "breast":     {"accuracy": 96.8, "sensitivity": 96.1, "specificity": 97.5},
    "oral":       {"accuracy": 94.8, "sensitivity": 93.9, "specificity": 95.7},
    "leukemia":   {"accuracy": 98.5, "sensitivity": 98.1, "specificity": 98.9},
}


def compute_specificity(y_true: np.ndarray, y_pred: np.ndarray, classes: list) -> float:
    """
    Macro-averaged specificity = TN / (TN + FP) across all classes.
    Computed via confusion matrix for multi-class scenarios.
    """
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(classes))))
    specificities = []
    for i in range(len(classes)):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        tn = cm.sum() - tp - fp - fn
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        specificities.append(spec)
    return float(np.mean(specificities))


def evaluate_cancer_model(
    cancer_type: str,
    y_true: list | np.ndarray,
    y_pred: list | np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
) -> dict:
    """
    Full evaluation of a cancer classification model.

    Args:
        cancer_type:   One of the 9 cancer types (e.g. 'brain', 'lung').
        y_true:        Ground-truth class indices.
        y_pred:        Predicted class indices.
        y_pred_proba:  (Optional) Softmax probability matrix (N, C) for AUC computation.

    Returns:
        Evaluation report dict with accuracy, sensitivity, specificity, F1, AUC.
    """
    if not SK_AVAILABLE:
        return {"error": "scikit-learn not installed"}

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    meta    = CANCER_MODEL_MAP.get(cancer_type, {})
    classes = meta.get("classes", [str(i) for i in np.unique(y_true)])
    n_cls   = len(classes)
    avg_fn  = "binary" if n_cls == 2 else "macro"

    accuracy    = float(accuracy_score(y_true, y_pred) * 100)
    sensitivity = float(recall_score(y_true, y_pred, average=avg_fn, zero_division=0) * 100)
    specificity = float(compute_specificity(y_true, y_pred, classes) * 100)
    f1          = float(f1_score(y_true, y_pred, average=avg_fn, zero_division=0) * 100)

    auc = None
    if y_pred_proba is not None:
        try:
            mc = "ovr" if n_cls > 2 else "raise"
            auc = float(roc_auc_score(
                y_true, y_pred_proba,
                multi_class=mc,
                average="macro",
            ) * 100)
        except Exception:
            auc = None

    benchmark = TARGET_BENCHMARKS.get(cancer_type, {})
    report = {
        "cancer_type":     cancer_type,
        "model_arch":      meta.get("model", "Unknown"),
        "dataset":         meta.get("dataset", "Unknown"),
        "n_samples":       meta.get("samples", 0),
        "n_classes":       n_cls,
        "classes":         classes,
        "metrics": {
            "accuracy":    round(accuracy, 2),
            "sensitivity": round(sensitivity, 2),
            "specificity": round(specificity, 2),
            "f1_score":    round(f1, 2),
            "auc_roc":     round(auc, 2) if auc is not None else "N/A",
        },
        "benchmark": benchmark,
        "meets_benchmark": {
            "accuracy":    accuracy >= benchmark.get("accuracy", 0),
            "sensitivity": sensitivity >= benchmark.get("sensitivity", 0),
            "specificity": specificity >= benchmark.get("specificity", 0),
        },
        "class_report": classification_report(
            y_true, y_pred,
            target_names=classes[:n_cls],
            output_dict=True,
            zero_division=0,
        ),
    }
    return report


def evaluate_all_models(model_results: dict) -> dict:
    """
    Evaluate all 9 cancer models and produce a consolidated report.

    Args:
        model_results: {
            "brain": {"y_true": [...], "y_pred": [...], "y_pred_proba": [...]},
            ...
        }

    Returns:
        Consolidated report with per-cancer metrics and system-level averages.
    """
    results = {}
    for cancer_type, data in model_results.items():
        results[cancer_type] = evaluate_cancer_model(
            cancer_type,
            data["y_true"],
            data["y_pred"],
            data.get("y_pred_proba"),
        )

    # System-wide averages
    accs  = [r["metrics"]["accuracy"]    for r in results.values() if "error" not in r]
    sens  = [r["metrics"]["sensitivity"] for r in results.values() if "error" not in r]
    specs = [r["metrics"]["specificity"] for r in results.values() if "error" not in r]

    return {
        "per_cancer": results,
        "system_average": {
            "accuracy":    round(float(np.mean(accs)),  2) if accs  else 0,
            "sensitivity": round(float(np.mean(sens)),  2) if sens  else 0,
            "specificity": round(float(np.mean(specs)), 2) if specs else 0,
        },
        "n_cancer_types": len(results),
    }


def print_evaluation_report(report: dict) -> None:
    """Pretty-print a single cancer model evaluation report."""
    m = report.get("metrics", {})
    b = report.get("benchmark", {})
    print(f"\n{'='*60}")
    print(f"  Cancer Type : {report.get('cancer_type','').upper()}")
    print(f"  Model       : {report.get('model_arch')}")
    print(f"  Dataset     : {report.get('dataset')}")
    print(f"{'='*60}")
    print(f"  Accuracy    : {m.get('accuracy'):.2f}%   (target: ≥{b.get('accuracy',0):.1f}%)")
    print(f"  Sensitivity : {m.get('sensitivity'):.2f}%   (target: ≥{b.get('sensitivity',0):.1f}%)")
    print(f"  Specificity : {m.get('specificity'):.2f}%   (target: ≥{b.get('specificity',0):.1f}%)")
    print(f"  F1-Score    : {m.get('f1_score'):.2f}%")
    print(f"  AUC-ROC     : {m.get('auc_roc')}")
    meets = report.get("meets_benchmark", {})
    status = "✅ PASS" if all(meets.values()) else "⚠️  PARTIAL"
    print(f"  Benchmark   : {status}")
    print(f"{'='*60}\n")


# ── Standalone Demo ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    """
    Demo: generate synthetic evaluation data for all 9 cancer types
    and print the consolidated report.
    Replace with real y_true / y_pred from your test sets.
    """
    import random

    rng = np.random.default_rng(42)
    demo_results = {}

    for cancer, meta in CANCER_MODEL_MAP.items():
        n_cls = len(meta["classes"])
        n     = 200
        y_t   = rng.integers(0, n_cls, size=n)
        # Simulate ~96% accuracy
        y_p   = np.where(rng.random(n) < 0.96, y_t, rng.integers(0, n_cls, n))
        # Softmax probabilities (random, just for demo)
        proba = rng.dirichlet(np.ones(n_cls), size=n)
        demo_results[cancer] = {"y_true": y_t.tolist(), "y_pred": y_p.tolist(),
                                "y_pred_proba": proba.tolist()}

    report = evaluate_all_models(demo_results)

    print("\n" + "="*60)
    print("  OncoAI — Phase-2 Final Review: Evaluation Report")
    print("  Batch 2026-27 | 7th Sem | Odd Semester")
    print("="*60)

    for cancer, r in report["per_cancer"].items():
        print_evaluation_report(r)

    avg = report["system_average"]
    print(f"\n{'='*60}")
    print(f"  SYSTEM-WIDE AVERAGE (9 Cancer Types)")
    print(f"{'='*60}")
    print(f"  Mean Accuracy    : {avg['accuracy']:.2f}%")
    print(f"  Mean Sensitivity : {avg['sensitivity']:.2f}%")
    print(f"  Mean Specificity : {avg['specificity']:.2f}%")
    print(f"{'='*60}\n")
