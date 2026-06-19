from PIL import Image, ImageChops, ImageEnhance
from io import BytesIO
import os
import numpy as np
import cv2


# ------------------------------------------------------------
# ELA FUNCTION
# ------------------------------------------------------------
def perform_ela(image_path, quality=90, brightness_boost=15):

    try:
        original = Image.open(image_path).convert("RGB")

        buffer = BytesIO()
        original.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        recompressed = Image.open(buffer)

        diff = ImageChops.difference(original, recompressed)

        enhancer = ImageEnhance.Brightness(diff)
        ela_image = enhancer.enhance(brightness_boost)

        ela_array = np.array(ela_image)

        mean_error = float(np.mean(ela_array))
        max_error = int(np.max(ela_array))
        std_dev = float(np.std(ela_array))

        report_dir = os.path.join(os.path.dirname(image_path), "UDFA_Reports")
        os.makedirs(report_dir, exist_ok=True)

        ela_path = os.path.join(
            report_dir,
            os.path.basename(image_path) + "_ELA.jpg"
        )

        ela_image.save(ela_path)

        return {
            "ela_path": ela_path,
            "mean_error": mean_error,
            "max_error": max_error,
            "std_dev": std_dev
        }

    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------------------
# DETECT TAMPERED REGIONS (BOX DRAW)
# ------------------------------------------------------------
def detect_tampered_regions(ela_path):

    img = cv2.imread(ela_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    output = img.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 500:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        cv2.rectangle(output, (x, y), (x+w, y+h), (0, 0, 255), 2)

    out_path = ela_path.replace(".jpg", "_BOX.jpg")
    cv2.imwrite(out_path, output)

    return out_path


# ------------------------------------------------------------
# FINAL TAMPER CHECK
# ------------------------------------------------------------
def quick_tamper_check(image_path):

    ela_result = perform_ela(image_path)

    if "error" in ela_result:
        return {
            "tamper_likelihood": 0,
            "decision": "Unknown",
            "details": ela_result
        }

    mean_err = ela_result["mean_error"]
    max_err = ela_result["max_error"]
    std_dev = ela_result["std_dev"]

    score = 0

    # 🔥 IMPROVED SCORING (LESS FALSE POSITIVES)

    if mean_err > 35:
        score += 40
    elif mean_err > 20:
        score += 20
    elif mean_err > 12:
        score += 10

    if max_err > 220:
        score += 20
    elif max_err > 150:
        score += 10

    if std_dev > 50:
        score += 20
    elif std_dev > 30:
        score += 10

    score = min(score, 100)

    # 🔥 FINAL DECISION

    if score >= 75:
        decision = "Likely Tampered"
    elif score >= 45:
        decision = "Possibly Tampered"
    elif score >= 20:
        decision = "Low Suspicion"
    else:
        decision = "Likely Authentic"

    # 🔥 REGION DETECTION
    box_path = detect_tampered_regions(ela_result["ela_path"])

    return {
        "tamper_likelihood": score,
        "decision": decision,
        "details": {
            "ELA_mean": round(mean_err, 2),
            "ELA_max": max_err,
            "ELA_std_dev": round(std_dev, 2),
            "ELA_path": ela_result["ela_path"],
            "BOX_path": box_path
        }
    }
