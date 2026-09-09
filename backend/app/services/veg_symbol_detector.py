from PIL import Image
import numpy as np


class VegSymbolDetector:
    """Offline deterministic detector for Indian veg/non-veg identification marks."""

    def detect(self, image: Image.Image):
        rgb = np.array(image.convert("RGB"))

        # Green-color mask.
        r = rgb[:, :, 0].astype(np.float32)
        g = rgb[:, :, 1].astype(np.float32)
        b = rgb[:, :, 2].astype(np.float32)

        mask = (
            (g > 60)
            & (g > r * 1.15)
            & (g > b * 1.05)
        )

        h, w = mask.shape

        # Work on a smaller image for fast connected-component analysis.
        scale = max(1, int(max(h, w) / 600))
        small = mask[::scale, ::scale]
        sh, sw = small.shape

        visited = np.zeros_like(small, dtype=bool)
        components = []

        for y in range(sh):
            for x in range(sw):
                if not small[y, x] or visited[y, x]:
                    continue

                stack = [(y, x)]
                visited[y, x] = True
                pixels = []

                while stack:
                    cy, cx = stack.pop()
                    pixels.append((cy, cx))

                    for dy, dx in (
                        (-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)
                    ):
                        ny, nx = cy + dy, cx + dx

                        if (
                            0 <= ny < sh
                            and 0 <= nx < sw
                            and small[ny, nx]
                            and not visited[ny, nx]
                        ):
                            visited[ny, nx] = True
                            stack.append((ny, nx))

                if len(pixels) < 8:
                    continue

                ys = [p[0] for p in pixels]
                xs = [p[1] for p in pixels]

                x1, x2 = min(xs), max(xs)
                y1, y2 = min(ys), max(ys)
                cw = x2 - x1 + 1
                ch = y2 - y1 + 1

                components.append({
                    "x": x1 * scale,
                    "y": y1 * scale,
                    "width": cw * scale,
                    "height": ch * scale,
                    "area": len(pixels) * scale * scale,
                })

        # Look for a compact approximately-square green component.
        candidates = []

        for c in components:
            cw = c["width"]
            ch = c["height"]
            area = c["area"]

            if cw < 15 or ch < 15:
                continue
            if cw > min(w, h) * 0.35 or ch > min(w, h) * 0.35:
                continue

            ratio = cw / max(ch, 1)

            if 0.55 <= ratio <= 1.8:
                candidates.append(c)

        # Prefer small/medium compact components, not large package artwork.
        candidates.sort(
            key=lambda c: (
                abs(c["width"] / max(c["height"], 1) - 1.0),
                c["area"]
            )
        )

        for c in candidates:
            x1 = max(0, c["x"] - c["width"] // 2)
            y1 = max(0, c["y"] - c["height"] // 2)
            x2 = min(w, c["x"] + c["width"] + c["width"] // 2)
            y2 = min(h, c["y"] + c["height"] + c["height"] // 2)

            roi = mask[y1:y2, x1:x2]

            if roi.size == 0:
                continue

            # A veg symbol normally has green material both around the
            # perimeter and in a compact central region.
            rh, rw = roi.shape

            center = roi[
                int(rh * 0.25):int(rh * 0.75),
                int(rw * 0.25):int(rw * 0.75)
            ]

            if center.size == 0:
                continue

            center_ratio = float(center.mean())

            if center_ratio > 0.01:
                return {
                    "detected": True,
                    "type": "Vegetarian",
                    "confidence": "HIGH",
                    "bbox": {
                        "x": int(x1),
                        "y": int(y1),
                        "width": int(x2 - x1),
                        "height": int(y2 - y1),
                    },
                }

        return {
            "detected": False,
            "type": None,
            "confidence": "NONE",
            "bbox": None,
        }


veg_symbol_detector = VegSymbolDetector()
