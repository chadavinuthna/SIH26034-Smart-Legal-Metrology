import sys
from pathlib import Path
import io

from PIL import Image

# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.paddle_ocr_service import paddle_ocr_service


# ---------------------------------------------------------
# SVG -> PNG using Pillow is NOT supported directly.
# Therefore, this test expects a PNG/JPG version.
# ---------------------------------------------------------

def test_image(image_path: Path):
    print("=" * 70)
    print(f"TESTING: {image_path}")
    print("=" * 70)

    image = Image.open(image_path).convert("RGB")

    print(f"Image size: {image.size}")

    result = paddle_ocr_service.extract_raw_ocr(image)

    print("\n1. OCR DETECTED TEXT")
    print("-" * 70)

    for line in result.lines:
        print(f"\nLine {line.line_index + 1}")
        print(f"Text       : {line.text}")
        print(f"Confidence : {line.confidence:.4f}")
        print(
            f"Bounding Box: "
            f"[{line.bbox.x_min:.1f}, "
            f"{line.bbox.y_min:.1f}, "
            f"{line.bbox.x_max:.1f}, "
            f"{line.bbox.y_max:.1f}]"
        )

    print("\n2. SUMMARY")
    print("-" * 70)
    print(f"Total lines       : {result.total_lines}")
    print(f"Average confidence: {result.average_confidence:.4f}")

    print("\n3. PRODUCT DATA")
    print("-" * 70)

    product = paddle_ocr_service.extract_product_data(image)

    print(product.model_dump_json(indent=2))


if __name__ == "__main__":

    # Use PNG/JPG here.
    # We will create this from demo_biscuits.svg separately.
    biscuits = (
        PROJECT_ROOT
        / "frontend"
        / "src"
        / "assets"
        / "demo_biscuits.png"
    )

    if not biscuits.exists():
        print("\nERROR:")
        print(f"Could not find: {biscuits}")
        print()
        print(
            "The project currently has demo_biscuits.svg, "
            "but this test needs a PNG/JPG image."
        )
        print()
        print("Please convert demo_biscuits.svg to PNG once,")
        print("then run this test again.")
        sys.exit(1)

    test_image(biscuits)