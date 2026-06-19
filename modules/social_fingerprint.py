# modules/social_fingerprint.py
from PIL import Image
import os

KNOWN_SOFTWARE_KEYWORDS = {
    "WhatsApp": ["WhatsApp", "WhatsApp/Android", "WhatsApp/IOS"],
    "Instagram": ["Instagram", "IG", "Instagram for"],
    "Facebook": ["Facebook", "FB"],
    "Snapseed": ["Snapseed"],
    "Photoshop": ["Adobe", "Photoshop"],
    "Telegram": ["Telegram"],
    "Twitter": ["Twitter"],
    "Gmail": ["Gmail"],
    "PhoneCamera": ["Camera", "Pixel", "iPhone", "HUAWEI", "Samsung", "Xiaomi", "realme", "OPPO", "VIVO"]
}

def _longest_side(width, height):
    return max(width, height)

def analyze_social_fingerprint(image_path, metadata=None):
    """
    Heuristic-based fingerprint: returns likely source & confidence and reasons.
    metadata: pass existing metadata dict (optional) to reuse EXIF info.
    """
    result = {"likely_source": "Unknown", "confidence": 0, "reasons": []}
    try:
        img = Image.open(image_path)
        w, h = img.size
        ls = _longest_side(w, h)
        filesize_kb = os.path.getsize(image_path) / 1024.0

        # Use metadata if available
        exif = {}
        if metadata and isinstance(metadata, dict):
            exif = metadata

        # Rule 1: if EXIF Software / Make contains known keywords
        sw = exif.get("Software") or exif.get("Camera Model") or exif.get("Camera Make")
        if sw:
            sstr = str(sw)
            for name, keys in KNOWN_SOFTWARE_KEYWORDS.items():
                for k in keys:
                    if k.lower() in sstr.lower():
                        result["likely_source"] = name if name != "PhoneCamera" else "Camera (direct)"
                        result["confidence"] = max(result["confidence"], 75)
                        result["reasons"].append(f"Software/Camera tag suggests {name}: '{sstr}'")

        # Rule 2: EXIF missing + small longest side => compressed by chat apps
        exif_present = bool(exif)
        if not exif_present:
            if ls <= 1600 and filesize_kb < 500:
                result["likely_source"] = "WhatsApp/ChatApp (probable)"
                result["confidence"] = max(result["confidence"], 70)
                result["reasons"].append("No EXIF and small size/longest side indicates chat app compression")
            elif ls <= 1100:
                result["likely_source"] = "Social (Instagram/Facebook) compressed"
                result["confidence"] = max(result["confidence"], 50)
                result["reasons"].append("Small resolution suggests social platform compression")

        # Rule 3: Instagram typical resize to square near 1080
        if abs(w - 1080) < 200 and abs(h - 1080) < 200:
            result["likely_source"] = "Instagram (probable)"
            result["confidence"] = max(result["confidence"], 65)
            result["reasons"].append("Image near Instagram standard square size ~1080x1080")

        # Rule 4: WhatsApp special hint: filename or other signs (optional)
        # Add more rules as you find signatures

        # Fallback: if nothing strong, mark as Camera if EXIF has DateTimeOriginal + Make/Model
        if result["confidence"] < 30:
            if exif.get("Date Taken (EXIF)") or exif.get("Camera Model"):
                result["likely_source"] = "Camera (direct)"
                result["confidence"] = max(result["confidence"], 60)
                result["reasons"].append("EXIF present indicating camera origin")

        return result
    except Exception as e:
        return {"likely_source": "Unknown", "confidence": 0, "reasons": [f"Error: {e}"]}

