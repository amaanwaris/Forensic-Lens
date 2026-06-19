from PIL import Image
from PIL.ExifTags import TAGS
import os

def detect_ai_image(image_path):

    result = {
        "is_ai_generated": False,
        "confidence": 0,
        "reasons": []
    }

    try:
        img = Image.open(image_path)

        # -----------------------------
        # 🔍 EXIF CHECK
        # -----------------------------
        exif = img._getexif()

        if not exif:
            result["confidence"] += 40
            result["reasons"].append("No EXIF metadata")

            exif_data = {}
        else:
            exif_data = {
                TAGS.get(tag): val
                for tag, val in exif.items()
                if tag in TAGS
            }

            if "Make" not in exif_data:
                result["confidence"] += 20
                result["reasons"].append("Camera info missing")

        # -----------------------------
        # 🔍 SOFTWARE TRACE CHECK
        # -----------------------------
        software = str(exif_data.get("Software", "")).lower()

        if any(word in software for word in ["ai", "stable", "diffusion", "midjourney", "dalle"]):
            result["confidence"] += 30
            result["reasons"].append("AI software detected in metadata")

        # -----------------------------
        # 🔍 SIZE CHECK
        # -----------------------------
        width, height = img.size

        if width % 8 != 0 or height % 8 != 0:
            result["confidence"] += 10
            result["reasons"].append("Unusual resolution pattern")

        # -----------------------------
        # 🔍 FILENAME CHECK
        # -----------------------------
        name = os.path.basename(image_path).lower()

        if any(word in name for word in ["ai", "generated", "midjourney", "dalle"]):
            result["confidence"] += 20
            result["reasons"].append("Suspicious filename")

        # -----------------------------
        # 🔍 COLOR VARIATION CHECK
        # -----------------------------
        pixels = list(img.getdata())

        # only check first 1000 pixels for speed
        unique_colors = len(set(pixels[:1000]))

        if unique_colors < 50:
            result["confidence"] += 10
            result["reasons"].append("Low color variation (AI-like pattern)")

        # -----------------------------
        # 🎯 FINAL DECISION
        # -----------------------------
        if result["confidence"] >= 40:
            result["is_ai_generated"] = True

        return result

    except Exception as e:
        return {"error": str(e)}
