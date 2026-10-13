"""
OncoAI — AI-IDS Training Script (NSL-KDD Dataset)
Trains a TensorFlow MLP classifier on the NSL-KDD dataset for network intrusion detection.

Usage:
    python backend/train_ids.py

Dataset:
    Download from: https://www.unb.ca/cic/datasets/nsl.html
    Place: backend/data/KDDTrain+.txt and backend/data/KDDTest+.txt

Output:
    backend/models/ids_nslkdd_model.h5   — saved TF model
    backend/models/ids_scaler.pkl        — feature scaler

Batch 2026-27 | Odd Semester | 7th Sem
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd

# ── Check TensorFlow ──────────────────────────────────────────────────────────
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
except ImportError:
    print("ERROR: TensorFlow not installed. Run: pip install tensorflow")
    sys.exit(1)

try:
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import (
        accuracy_score, classification_report, confusion_matrix,
        roc_auc_score
    )
    from sklearn.model_selection import train_test_split
except ImportError:
    print("ERROR: scikit-learn not installed. Run: pip install scikit-learn")
    sys.exit(1)


# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
MODEL_DIR   = os.path.join(BASE_DIR, "models")
TRAIN_PATH  = os.path.join(DATA_DIR, "KDDTrain+.txt")
TEST_PATH   = os.path.join(DATA_DIR, "KDDTest+.txt")
MODEL_OUT   = os.path.join(MODEL_DIR, "ids_nslkdd_model.h5")
SCALER_OUT  = os.path.join(MODEL_DIR, "ids_scaler.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

# ── NSL-KDD column names ───────────────────────────────────────────────────────
COLUMNS = [
    "duration","protocol_type","service","flag","src_bytes","dst_bytes",
    "land","wrong_fragment","urgent","hot","num_failed_logins","logged_in",
    "num_compromised","root_shell","su_attempted","num_root","num_file_creations",
    "num_shells","num_access_files","num_outbound_cmds","is_host_login",
    "is_guest_login","count","srv_count","serror_rate","srv_serror_rate",
    "rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate",
    "srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate","label","difficulty_level"
]

# ── Data Loading ──────────────────────────────────────────────────────────────

def load_nslkdd(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, names=COLUMNS, header=None)
    # Binary classification: 'normal' = 0, everything else = 1 (attack)
    df["label_binary"] = (df["label"] != "normal").astype(int)
    return df


def encode_features(df: pd.DataFrame) -> np.ndarray:
    """One-hot encode categorical features and return numeric array."""
    cat_cols = ["protocol_type", "service", "flag"]
    df = pd.get_dummies(df, columns=cat_cols)

    # Keep numeric columns only (drop label columns)
    drop_cols = ["label", "difficulty_level", "label_binary"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    return X.values.astype(np.float32)


# ── Model Architecture ────────────────────────────────────────────────────────

def build_ids_model(input_dim: int) -> keras.Model:
    """
    3-layer MLP for binary intrusion classification.
    Architecture: Dense(256) → BN → Dropout(0.3) → Dense(128) → BN → Dense(1, sigmoid)
    Optimiser: AdamW | Loss: BinaryCrossentropy | Metrics: Accuracy, AUC
    """
    model = keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(256, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(128, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.25),
        layers.Dense(64, activation="relu"),
        layers.Dense(1, activation="sigmoid"),
    ], name="OncoAI_IDS_NSL_KDD")

    model.compile(
        optimizer=keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=1e-5),
        loss="binary_crossentropy",
        metrics=["accuracy", keras.metrics.AUC(name="auc")],
    )
    return model


# ── Training Pipeline ─────────────────────────────────────────────────────────

def train():
    # 1. Check dataset
    if not os.path.exists(TRAIN_PATH):
        print(f"\n[IDS Training] ERROR: Dataset not found at {TRAIN_PATH}")
        print("Download NSL-KDD from: https://www.unb.ca/cic/datasets/nsl.html")
        print("Place KDDTrain+.txt and KDDTest+.txt in backend/data/\n")
        sys.exit(1)

    print("[IDS Training] Loading NSL-KDD dataset…")
    train_df = load_nslkdd(TRAIN_PATH)
    test_df  = load_nslkdd(TEST_PATH) if os.path.exists(TEST_PATH) else None

    # 2. Feature encoding
    print("[IDS Training] Encoding features…")
    X_train_raw = encode_features(train_df)
    y_train     = train_df["label_binary"].values

    if test_df is not None:
        X_test_raw = encode_features(test_df)
        y_test     = test_df["label_binary"].values
    else:
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X_train_raw, y_train, test_size=0.2, stratify=y_train, random_state=42
        )

    # Align columns (test may have different one-hot columns)
    n_cols = min(X_train_raw.shape[1], X_test_raw.shape[1])
    X_train_raw = X_train_raw[:, :n_cols]
    X_test_raw  = X_test_raw[:, :n_cols]

    # 3. Scaling
    print("[IDS Training] Scaling features (StandardScaler)…")
    scaler  = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test  = scaler.transform(X_test_raw)

    # Save scaler
    with open(SCALER_OUT, "wb") as f:
        pickle.dump(scaler, f)
    print(f"[IDS Training] Scaler saved → {SCALER_OUT}")

    # 4. Build model
    print(f"[IDS Training] Building model (input_dim={X_train.shape[1]})…")
    model = build_ids_model(input_dim=X_train.shape[1])
    model.summary()

    # 5. Train
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_auc", patience=5, restore_best_weights=True, mode="max"
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6
        ),
        keras.callbacks.ModelCheckpoint(
            MODEL_OUT, monitor="val_auc", save_best_only=True, mode="max"
        ),
    ]

    print("[IDS Training] Training MLP on NSL-KDD…")
    model.fit(
        X_train, y_train,
        validation_split=0.1,
        epochs=50,
        batch_size=512,
        callbacks=callbacks,
        class_weight={0: 1.0, 1: 2.0},   # Upweight attacks
        verbose=1,
    )

    # 6. Evaluate
    print("\n[IDS Training] Evaluation on test set…")
    y_pred_prob = model.predict(X_test, verbose=0).flatten()
    y_pred      = (y_pred_prob > 0.5).astype(int)

    acc   = accuracy_score(y_test, y_pred)
    auc   = roc_auc_score(y_test, y_pred_prob)
    cm    = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0  # Recall / Detection Rate
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0  # True Negative Rate

    print(f"\n{'='*50}")
    print(f"  AI-IDS NSL-KDD Evaluation Results")
    print(f"{'='*50}")
    print(f"  Accuracy    : {acc*100:.2f}%")
    print(f"  AUC-ROC     : {auc*100:.2f}%")
    print(f"  Sensitivity : {sensitivity*100:.2f}%  (attack detection rate)")
    print(f"  Specificity : {specificity*100:.2f}%  (false alarm rate)")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Normal','Attack'])}")
    print(f"[IDS Training] Model saved → {MODEL_OUT}\n")


if __name__ == "__main__":
    train()
