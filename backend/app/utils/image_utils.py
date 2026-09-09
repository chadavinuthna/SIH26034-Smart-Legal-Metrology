"""Image utility functions for format validation and basic quality inspection."""
import io
from typing import Tuple
from PIL import Image
from ..schemas import ImageQualityInfo


SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


def validate_and_inspect_image(image_bytes: bytes) -> Tuple[Image.Image, ImageQualityInfo]:
    """Validate image bytes with Pillow, verify format and dimensions, and generate image metadata."""
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"Image exceeds maximum permissible file size of 20MB.")

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify data integrity
    except Exception as e:
        raise ValueError(f"Invalid or corrupted image file: {str(e)}")

    # Re-open because verify() closes/invalidates the image object
    image = Image.open(io.BytesIO(image_bytes))

    fmt = (image.format or "UNKNOWN").upper()
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format '{fmt}'. Allowed formats: JPEG, PNG, WEBP.")

    width, height = image.size
    total_pixels = width * height
    size_kb = round(len(image_bytes) / 1024, 2)

    # Honest simple heuristic indicators based on resolution
    if total_pixels >= 1000 * 1000:
        quality_label = "GOOD"
        text_visibility = "CLEAR"
    elif total_pixels >= 400 * 400:
        quality_label = "MODERATE"
        text_visibility = "READABLE"
    else:
        quality_label = "LOW"
        text_visibility = "POTENTIALLY AMBIGUOUS"

    metadata = ImageQualityInfo(
        width=width,
        height=height,
        format=fmt,
        file_size_kb=size_kb,
        quality_label=quality_label,
        text_visibility=text_visibility,
    )

    return image, metadata
