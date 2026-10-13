"""
OncoAI — DICOM Image Handler
Loads DICOM (.dcm) medical files, converts them to PNG/JPEG-compatible format
for downstream model inference. Supports grayscale and multi-frame DICOM series.

Batch 2026-27 | Odd Semester | 7th Sem
"""

import io
import numpy as np
from PIL import Image

try:
    import pydicom
    from pydicom.pixel_data_handlers.util import apply_voi_lut
    DICOM_AVAILABLE = True
except ImportError:
    DICOM_AVAILABLE = False


def is_dicom_bytes(data: bytes) -> bool:
    """
    Check if raw bytes represent a DICOM file by inspecting the magic header.
    DICOM preamble is 128 bytes + 'DICM' magic.
    """
    if len(data) < 132:
        return False
    return data[128:132] == b"DICM"


def dicom_to_png_bytes(dicom_bytes: bytes) -> bytes | None:
    """
    Convert DICOM bytes to a standard PNG image (bytes).
    Applies VOI LUT (windowing) for proper radiological display.
    Handles both grayscale (CT, MRI, X-Ray) and RGB DICOM images.

    Args:
        dicom_bytes: Raw bytes of a .dcm DICOM file.

    Returns:
        PNG image bytes on success, None on failure.
    """
    if not DICOM_AVAILABLE:
        return None

    try:
        buf  = io.BytesIO(dicom_bytes)
        dcm  = pydicom.dcmread(buf)
        arr  = dcm.pixel_array.astype(np.float32)

        # Apply window/level (VOI LUT) if present — important for CT/MRI
        arr = apply_voi_lut(arr, dcm)

        # Normalise to 0-255
        arr_min, arr_max = arr.min(), arr.max()
        if arr_max > arr_min:
            arr = (arr - arr_min) / (arr_max - arr_min) * 255.0
        else:
            arr = np.zeros_like(arr)
        arr = arr.clip(0, 255).astype(np.uint8)

        # Handle multi-frame (take middle frame for series)
        if arr.ndim == 3 and arr.shape[0] > 3:
            mid_frame = arr.shape[0] // 2
            arr = arr[mid_frame]

        # Convert grayscale to RGB
        if arr.ndim == 2:
            pil = Image.fromarray(arr, mode="L").convert("RGB")
        elif arr.ndim == 3 and arr.shape[2] == 3:
            pil = Image.fromarray(arr, mode="RGB")
        elif arr.ndim == 3 and arr.shape[2] == 1:
            pil = Image.fromarray(arr[:, :, 0], mode="L").convert("RGB")
        else:
            pil = Image.fromarray(arr).convert("RGB")

        out_buf = io.BytesIO()
        pil.save(out_buf, format="PNG")
        return out_buf.getvalue()

    except Exception as e:
        print(f"[DICOM] Failed to convert DICOM: {e}")
        return None


def load_image_bytes(raw_bytes: bytes) -> tuple[bytes, str]:
    """
    Universal image loader supporting JPEG, PNG, and DICOM.
    Returns (processed_image_bytes, detected_format).

    Args:
        raw_bytes: Raw bytes of any supported image file.

    Returns:
        Tuple of (png_bytes, format_name).
        format_name is one of: 'JPEG', 'PNG', 'DICOM', 'UNKNOWN'.
    """
    # Try DICOM first
    if is_dicom_bytes(raw_bytes):
        png = dicom_to_png_bytes(raw_bytes)
        if png:
            return png, "DICOM"
        return raw_bytes, "DICOM_ERROR"

    # Standard image formats via PIL
    try:
        buf = io.BytesIO(raw_bytes)
        img = Image.open(buf)
        fmt = img.format or "UNKNOWN"

        if fmt not in ("JPEG", "PNG", "WEBP", "BMP", "TIFF"):
            return raw_bytes, "UNSUPPORTED"

        # Normalise to PNG for consistent downstream processing
        if img.mode != "RGB":
            img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue(), fmt

    except Exception as e:
        print(f"[ImageLoader] Cannot open image: {e}")
        return raw_bytes, "UNKNOWN"
