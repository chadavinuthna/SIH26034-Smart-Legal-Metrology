from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class ImageAnnotationService:
    """Creates local annotated package images for inspection evidence."""

    def annotate(self, image: Image.Image, regions, output_path: str):
        annotated = image.convert("RGB").copy()
        draw = ImageDraw.Draw(annotated)

        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except Exception:
            font = ImageFont.load_default()

        for region in regions:
            bbox = region.get("bbox")
            if not bbox:
                continue

            x = int(bbox.get("x", 0))
            y = int(bbox.get("y", 0))
            width = int(bbox.get("width", 0))
            height = int(bbox.get("height", 0))

            if width <= 0 or height <= 0:
                continue

            padding_x = max(12, annotated.width // 120)
            padding_y = max(10, annotated.height // 120)
            x = max(0, x - padding_x)
            y = max(0, y - padding_y)
            x2 = min(annotated.width - 1, x + width + (padding_x * 2))
            y2 = min(annotated.height - 1, y + height + (padding_y * 2))

            draw.rectangle(
                [x, y, x2, y2],
                outline=(255, 0, 0),
                width=max(6, annotated.width // 180),
            )

            label = region.get("label", "Issue")
            label_y = max(5, y - 42)
            bbox_text = draw.textbbox((0, 0), label, font=font)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
            draw.rectangle([x, label_y, x + text_width + 12, label_y + text_height + 8], fill=(255, 255, 255))
            draw.text((x + 6, label_y + 4), label, fill=(255, 0, 0), font=font)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        annotated.save(output_path, format="PNG")
        return output_path


image_annotation_service = ImageAnnotationService()
