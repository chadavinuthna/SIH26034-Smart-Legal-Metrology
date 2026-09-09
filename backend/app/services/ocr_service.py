import logging
import re
from typing import Any, Dict, List

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from pytesseract import Output

logger = logging.getLogger(__name__)


class OCRService:
    """
    Fully local OCR service.

    Uses Tesseract installed on the local machine.
    No internet connection or AI/LLM service is required.
    """

    def __init__(self):
        self.tesseract_cmd = None

        # Tesseract is normally available through PATH.
        # This Windows fallback handles the common installation location.
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            fallback = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if __import__("os").path.exists(fallback):
                self.tesseract_cmd = fallback
                pytesseract.pytesseract.tesseract_cmd = fallback

    def is_available(self) -> bool:
        """Return True when the local Tesseract engine is available."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as exc:
            logger.error("Tesseract is not available: %s", exc)
            return False

    @staticmethod
    def _preprocess(image: Image.Image) -> Image.Image:
        """
        Prepare the package image for OCR.

        The image is converted to grayscale, enlarged when necessary,
        contrast-enhanced and lightly sharpened.
        """
        image = image.convert("RGB")

        # Keep OCR reasonably fast while giving small label text enough pixels.
        max_dimension = 2200
        width, height = image.size

        if max(width, height) > max_dimension:
            scale = max_dimension / max(width, height)
            image = image.resize(
                (int(width * scale), int(height * scale)),
                Image.Resampling.LANCZOS,
            )

        gray = ImageOps.grayscale(image)

        # Improve contrast without aggressive thresholding.
        gray = ImageEnhance.Contrast(gray).enhance(1.5)
        gray = gray.filter(ImageFilter.SHARPEN)

        return gray

    def extract(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text, confidence and bounding boxes from a package image.

        Returns:
            {
                "text": "...",
                "words": [
                    {
                        "text": "...",
                        "confidence": 95.2,
                        "left": 10,
                        "top": 20,
                        "width": 100,
                        "height": 25
                    }
                ],
                "average_confidence": 91.4
            }
        """
        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR is not available. "
                "Please install Tesseract OCR and make sure it is in PATH."
            )

        processed = self._preprocess(image)

        # OCR data gives us both text and coordinates.
        data = pytesseract.image_to_data(
            processed,
            lang="eng",
            config="--oem 3 --psm 6",
            output_type=Output.DICT,
        )

        words: List[Dict[str, Any]] = []
        confidence_values: List[float] = []

        for i, raw_text in enumerate(data["text"]):
            text = raw_text.strip()

            if not text:
                continue

            try:
                confidence = float(data["conf"][i])
            except (ValueError, TypeError):
                confidence = -1

            if confidence < 0:
                continue

            item = {
                "text": text,
                "confidence": round(confidence, 2),
                "left": int(data["left"][i]),
                "top": int(data["top"][i]),
                "width": int(data["width"][i]),
                "height": int(data["height"][i]),
                "block_num": int(data["block_num"][i]),
                "par_num": int(data["par_num"][i]),
                "line_num": int(data["line_num"][i]),
            }

            words.append(item)
            confidence_values.append(confidence)

        # Reconstruct readable OCR text from the original Tesseract output.
        text_block = pytesseract.image_to_string(
            processed,
            lang="eng",
            config="--oem 3 --psm 6",
        )

        # Sparse-text pass helps detect small/separated declarations such as
        # batch numbers, dates and Best Before text on package labels.
        text_sparse = pytesseract.image_to_string(
            processed,
            lang="eng",
            config="--oem 3 --psm 11",
        )

        text = text_block + "\n" + text_sparse.strip()

        average_confidence = (
            round(sum(confidence_values) / len(confidence_values), 2)
            if confidence_values
            else 0.0
        )

        return {
            "text": text,
            "words": words,
            "average_confidence": average_confidence,
            "image_width": processed.width,
            "image_height": processed.height,
        }


ocr_service = OCRService()
