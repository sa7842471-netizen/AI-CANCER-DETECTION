"""
OncoAI — AI-Based Intrusion Detection System (AI-IDS)
TensorFlow model trained on the NSL-KDD dataset with real-time Scapy packet
capture for production deployment.

Security Compliance: India's DPDPA 2023
Batch 2026-27 | Odd Semester | 7th Sem

Architecture:
    - NSL-KDD feature extraction (41 features → 38 normalised numeric features)
    - 3-layer MLP in TensorFlow (Dense + BatchNorm + Dropout) — binary classifier
    - Scapy sniffer thread captures live packets, extracts features, scores each
    - Alerts logged to backend/logs/ids_alerts.log and SQLite audit_logs table
    - Blocked IPs tracked in an in-memory set (extend to Redis for production)

Training (offline, on full NSL-KDD dataset):
    Run `python backend/train_ids.py` to train and save ids_nslkdd_model.h5
"""

import os
import json
import logging
import threading
import datetime
from collections import defaultdict
from typing import Optional

import numpy as np

# ── Optional heavy dependencies (graceful degradation) ────────────────────────
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    from scapy.all import sniff, IP, TCP, UDP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler
    SK_AVAILABLE = True
except ImportError:
    SK_AVAILABLE = False


# ── Configuration ──────────────────────────────────────────────────────────────
IDS_MODEL_PATH = os.getenv("IDS_MODEL_PATH", "backend/models/ids_nslkdd_model.h5")
IDS_ALERT_LOG  = os.getenv("IDS_ALERT_LOG_PATH", "backend/logs/ids_alerts.log")
IFACE          = os.getenv("IDS_NETWORK_INTERFACE", "lo")

os.makedirs(os.path.dirname(IDS_ALERT_LOG), exist_ok=True)

logging.basicConfig(
    filename=IDS_ALERT_LOG,
    level=logging.WARNING,
    format="%(asctime)s [IDS-ALERT] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
ids_logger = logging.getLogger("oncoai_ids")

# ── Global State ───────────────────────────────────────────────────────────────
_ids_model: Optional[object]    = None   # TF model
_ids_scaler: Optional[object]   = None   # sklearn StandardScaler
_blocked_ips: set                = set()
_ip_request_count                = defaultdict(int)
_ip_last_seen: dict              = {}
_ids_thread: Optional[threading.Thread] = None
_ids_running: bool               = False

# Alert buffer (last 100 alerts accessible via API)
_alert_buffer: list[dict]        = []
_ALERT_BUFFER_MAX                = 100


# ── NSL-KDD Feature Names (38 numeric features used) ──────────────────────────
NSLKDD_NUMERIC_FEATURES = [
    "duration", "protocol_type", "service", "flag",
    "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
    "hot", "num_failed_logins", "logged_in", "num_compromised",
    "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count",
    "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
    "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
    "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
]


def _extract_packet_features(pkt) -> Optional[np.ndarray]:
    """
    Extract an NSL-KDD-compatible feature vector from a Scapy packet.
    Returns a (1, 38) numpy array for model inference, or None if unsupported.

    Note: This is a simplified real-time feature extraction.
    Full NSL-KDD features require connection-level aggregation.
    This implementation extracts per-packet features suitable for
    lightweight anomaly scoring.
    """
    if not (pkt.haslayer(IP) and (pkt.haslayer(TCP) or pkt.haslayer(UDP))):
        return None

    ip   = pkt[IP]
    proto = 1 if pkt.haslayer(TCP) else 2  # 0=icmp, 1=tcp, 2=udp

    src_port = pkt[TCP].sport if pkt.haslayer(TCP) else pkt[UDP].sport
    dst_port = pkt[TCP].dport if pkt.haslayer(TCP) else pkt[UDP].dport
    flags    = int(pkt[TCP].flags) if pkt.haslayer(TCP) else 0
    pkt_len  = len(pkt)

    # Build a 38-element feature vector matching NSLKDD_NUMERIC_FEATURES order
    features = np.zeros(38, dtype=np.float32)
    features[0]  = 0                # duration (connection-level, unknown per-pkt)
    features[1]  = proto            # protocol_type (encoded)
    features[2]  = dst_port / 65535 # service (normalised port)
    features[3]  = flags / 63       # flag (TCP flags)
    features[4]  = pkt_len          # src_bytes
    features[5]  = 0                # dst_bytes (unknown per-pkt)
    features[22] = _ip_request_count[ip.src] / 100.0  # count (request rate)
    features[32] = dst_port / 65535 # dst_host_srv_count proxy

    return features.reshape(1, -1)


def load_ids_model() -> bool:
    """
    Load the pre-trained TF IDS model from disk.
    Returns True if loaded successfully, False otherwise.
    """
    global _ids_model
    if not TF_AVAILABLE:
        print("[IDS] TensorFlow not available — IDS disabled.")
        return False
    if not os.path.exists(IDS_MODEL_PATH):
        print(f"[IDS] Model not found at {IDS_MODEL_PATH}. Run train_ids.py first.")
        return False
    try:
        _ids_model = tf.keras.models.load_model(IDS_MODEL_PATH)
        print(f"[IDS] Model loaded from {IDS_MODEL_PATH}")
        return True
    except Exception as e:
        print(f"[IDS] Failed to load model: {e}")
        return False


def score_packet(pkt) -> None:
    """
    Process a single Scapy packet: extract features, run IDS model,
    and alert if intrusion detected.
    """
    global _alert_buffer

    if not pkt.haslayer(IP):
        return

    ip_src = pkt[IP].src
    _ip_request_count[ip_src] += 1
    _ip_last_seen[ip_src] = datetime.datetime.utcnow().isoformat()

    # Rule-based rate limiting (fast path — no ML needed)
    if _ip_request_count[ip_src] > 500:
        _trigger_alert(ip_src, "RATE_LIMIT", score=1.0, method="rule-based")
        _blocked_ips.add(ip_src)
        return

    # ML-based scoring
    if _ids_model is None:
        return

    feats = _extract_packet_features(pkt)
    if feats is None:
        return

    try:
        score = float(_ids_model.predict(feats, verbose=0)[0][0])
        if score > 0.75:  # Threshold for intrusion detection
            _trigger_alert(ip_src, "ML_INTRUSION", score=score, method="tensorflow-ids")
    except Exception:
        pass


def _trigger_alert(ip: str, alert_type: str, score: float, method: str) -> None:
    """Log an IDS alert to file and in-memory buffer."""
    global _alert_buffer
    alert = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "src_ip":    ip,
        "type":      alert_type,
        "score":     round(score, 4),
        "method":    method,
        "blocked":   ip in _blocked_ips,
    }
    ids_logger.warning(json.dumps(alert))
    _alert_buffer.append(alert)
    if len(_alert_buffer) > _ALERT_BUFFER_MAX:
        _alert_buffer = _alert_buffer[-_ALERT_BUFFER_MAX:]


def _sniffer_loop() -> None:
    """Scapy packet sniffer main loop — runs in a background daemon thread."""
    global _ids_running
    if not SCAPY_AVAILABLE:
        print("[IDS] Scapy not available — live capture disabled.")
        return
    print(f"[IDS] Starting Scapy sniffer on interface '{IFACE}'…")
    try:
        sniff(
            iface=IFACE,
            prn=score_packet,
            store=False,
            stop_filter=lambda _: not _ids_running,
        )
    except Exception as e:
        print(f"[IDS] Sniffer error: {e}")


def start_ids() -> bool:
    """
    Start the AI-IDS background thread.
    Returns True if started, False if prerequisites are missing.
    """
    global _ids_thread, _ids_running
    if not load_ids_model():
        return False
    _ids_running = True
    _ids_thread  = threading.Thread(target=_sniffer_loop, daemon=True)
    _ids_thread.start()
    print("[IDS] Intrusion Detection System started.")
    return True


def stop_ids() -> None:
    """Stop the IDS background thread gracefully."""
    global _ids_running
    _ids_running = False
    print("[IDS] Intrusion Detection System stopped.")


def get_ids_status() -> dict:
    """Return current IDS status — exposed via /api/admin/ids-status endpoint."""
    return {
        "running":          _ids_running,
        "scapy_available":  SCAPY_AVAILABLE,
        "tf_available":     TF_AVAILABLE,
        "model_loaded":     _ids_model is not None,
        "blocked_ips":      list(_blocked_ips),
        "total_blocked":    len(_blocked_ips),
        "recent_alerts":    _alert_buffer[-20:],   # last 20
        "request_counts":   dict(sorted(
            _ip_request_count.items(), key=lambda x: -x[1]
        )[:10]),                                   # top 10 IPs
    }


def is_ip_blocked(ip: str) -> bool:
    """Check if a source IP is in the block list."""
    return ip in _blocked_ips


def unblock_ip(ip: str) -> None:
    """Manually unblock an IP address."""
    _blocked_ips.discard(ip)
    _ip_request_count[ip] = 0
