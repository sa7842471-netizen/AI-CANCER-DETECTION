"""
OncoAI — Security Module
Handles JWT session management, AES-256 encryption, OTP/2FA, and bcrypt password hashing.
Batch 2026-27 | Odd Semester | 7th Sem

Compliance: India's DPDPA 2023
"""

import os
import hashlib
import base64
import hmac
import secrets
import datetime
from functools import wraps

import pyotp
import bcrypt
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Configuration ──────────────────────────────────────────────────────────────
JWT_SECRET       = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
JWT_EXPIRY_MINS  = int(os.getenv("JWT_EXPIRY_MINUTES", "30"))
AES_KEY_HEX      = os.getenv("AES_ENCRYPTION_KEY", "")

# Derive a 32-byte AES key from the hex string, or generate one if not set
try:
    AES_KEY = bytes.fromhex(AES_KEY_HEX) if len(AES_KEY_HEX) == 64 else os.urandom(32)
except ValueError:
    AES_KEY = os.urandom(32)


# ── Password Hashing (bcrypt) ──────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Bcrypt-hash a password with auto salt. Returns hex-encoded hash."""
    pw_bytes = plain_password.encode("utf-8")
    hashed   = bcrypt.hashpw(pw_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )
    except Exception:
        return False


def sha256_hash(text: str) -> str:
    """Legacy SHA-256 hash — kept for backward-compat with existing records."""
    return hashlib.sha256(text.encode()).hexdigest()


# ── JWT Token Management ───────────────────────────────────────────────────────

def generate_token(user_id: int, username: str, role: str) -> str:
    """
    Create a signed JWT with 30-minute expiry.
    Payload: sub (user_id), username, role, iat, exp.
    """
    now = datetime.datetime.utcnow()
    payload = {
        "sub":      user_id,
        "username": username,
        "role":     role,
        "iat":      now,
        "exp":      now + datetime.timedelta(minutes=JWT_EXPIRY_MINS),
        "jti":      secrets.token_hex(16),   # JWT ID for revocation
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT.
    Returns payload dict on success, None on failure / expiry.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Flask decorator: validates Bearer JWT token in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token   = auth_header.split(" ", 1)[1]
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Token expired or invalid. Please sign in again."}), 401
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    """Flask decorator: restricts endpoint to specific roles (admin, specialist, patient)."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            user_role = getattr(request, "current_user", {}).get("role", "")
            if user_role not in roles:
                return jsonify({"error": f"Access denied. Required role(s): {', '.join(roles)}"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ── AES-256-GCM Encryption ─────────────────────────────────────────────────────

def aes_encrypt(plaintext: str) -> str:
    """
    Encrypt a string with AES-256-GCM.
    Returns base64-encoded nonce+ciphertext (nonce prepended, 12 bytes).
    Compliant with DPDPA 2023 data-at-rest encryption requirements.
    """
    aesgcm = AESGCM(AES_KEY)
    nonce  = os.urandom(12)
    ct     = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("utf-8")


def aes_decrypt(blob: str) -> str:
    """
    Decrypt a base64-encoded AES-256-GCM blob.
    Returns plaintext string, or empty string on failure.
    """
    try:
        raw    = base64.b64decode(blob.encode("utf-8"))
        nonce  = raw[:12]
        ct     = raw[12:]
        aesgcm = AESGCM(AES_KEY)
        return aesgcm.decrypt(nonce, ct, None).decode("utf-8")
    except Exception:
        return ""


# ── OTP / TOTP 2FA ────────────────────────────────────────────────────────────

def generate_totp_secret() -> str:
    """Generate a new TOTP secret key for a user."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str) -> str:
    """Return an otpauth:// URI for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name="OncoAI")


def verify_totp(secret: str, otp_code: str) -> bool:
    """Verify a TOTP code (±1 step tolerance for clock drift)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code, valid_window=1)


def generate_email_otp() -> tuple[str, datetime.datetime]:
    """
    Generate a 6-digit numeric OTP for email / SMS delivery.
    Returns (otp_string, expiry_datetime).
    """
    otp    = f"{secrets.randbelow(1000000):06d}"
    expiry = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=int(os.getenv("OTP_EXPIRY_SECONDS", "300"))
    )
    return otp, expiry


def verify_email_otp(stored_otp: str, stored_expiry: datetime.datetime, provided_otp: str) -> bool:
    """Verify a time-bound email/SMS OTP using constant-time comparison."""
    if datetime.datetime.utcnow() > stored_expiry:
        return False
    return hmac.compare_digest(stored_otp, provided_otp)
