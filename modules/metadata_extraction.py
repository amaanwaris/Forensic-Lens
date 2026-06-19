# modules/metadata_extraction.py
import os
import datetime
import hashlib
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def _safe_float(x):
    """Try convert EXIF rational/int/float to float safely."""
    try:
        return float(x)
    except Exception:
        try:
            # some EXIF values come as tuples of rationals ((num,den),...)
            return x[0] / x[1]
        except Exception:
            return None

def _to_degrees(value):
    """
    Convert EXIF GPS component to degrees.
    value expected like: (deg, min, sec) where each can be rational or float.
    """
    try:
        d = _safe_float(value[0])
        m = _safe_float(value[1])
        s = _safe_float(value[2])
        if d is None or m is None or s is None:
            return None
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None

def _extract_gps_info(exif):
    """Return (lat, lon, raw_gps_dict) or (None, None, None)"""
    if not exif:
        return None, None, None
    gps_ifd = exif.get(34853) or exif.get('GPSInfo')  # numeric tag or 'GPSInfo'
    if not gps_ifd:
        return None, None, None

    # build a readable gps dict
    gps_data = {}
    # gps_ifd may be mapping of tag->value where tag is numeric key
    for key in gps_ifd.keys():
        name = GPSTAGS.get(key, key)
        gps_data[name] = gps_ifd[key]

    lat = lon = None
    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
        lat_deg = _to_degrees(gps_data["GPSLatitude"])
        if lat_deg is not None:
            lat = lat_deg if gps_data["GPSLatitudeRef"] == "N" else -lat_deg

    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
        lon_deg = _to_degrees(gps_data["GPSLongitude"])
        if lon_deg is not None:
            lon = lon_deg if gps_data["GPSLongitudeRef"] == "E" else -lon_deg

    return lat, lon, gps_data

def _format_datetime(exif_dt):
    """Convert EXIF DateTimeOriginal like 'YYYY:MM:DD HH:MM:SS' to readable format."""
    try:
        dt = datetime.datetime.strptime(exif_dt, "%Y:%m:%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return exif_dt  # return raw if parsing fails

def _compute_hashes(path):
    """Compute MD5 and SHA256 for given file path."""
    try:
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                md5.update(chunk)
                sha256.update(chunk)
        return md5.hexdigest(), sha256.hexdigest()
    except Exception:
        return None, None

def extract_metadata(file_path):
    """
    Forensic-focused metadata extractor for image files.
    Returns dict of metadata fields (and prints them).
    """
    try:
        # filesystem metadata
        stats = os.stat(file_path)
        metadata = {
            "File Path": file_path,
            "Size (bytes)": stats.st_size,
            "Created (FS)": datetime.datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "Modified (FS)": datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }

        # compute hashes (for chain-of-custody)
        md5, sha256 = _compute_hashes(file_path)
        if md5:
            metadata["MD5"] = md5
        if sha256:
            metadata["SHA256"] = sha256

        # Only attempt EXIF for common image types
        lower = file_path.lower()
        if lower.endswith((".jpg", ".jpeg", ".tiff", ".heic", ".png")):
            try:
                img = Image.open(file_path)

                # resolution & orientation
                try:
                    w, h = img.size
                    metadata["Resolution"] = f"{w} x {h}"
                except Exception:
                    pass
                try:
                    orientation = None
                    exif_test = img._getexif()
                    if exif_test:
                        orientation = exif_test.get(274) or exif_test.get('Orientation')  # 274 is Orientation tag
                    if orientation:
                        # map common values to human readable rotation
                        orient_map = {
                            1: "Horizontal (normal)",
                            2: "Mirrored horizontal",
                            3: "Rotate 180",
                            4: "Mirrored vertical",
                            5: "Mirrored horizontal then rotate 270 CW",
                            6: "Rotate 90 CW",
                            7: "Mirrored horizontal then rotate 90 CW",
                            8: "Rotate 270 CW"
                        }
                        metadata["Orientation"] = orient_map.get(orientation, str(orientation))
                except Exception:
                    pass

                exif_data = img._getexif()
                if exif_data:
                    # map tag ids to names
                    exif = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif[tag] = value

                    # Date Taken
                    if "DateTimeOriginal" in exif:
                        metadata["Date Taken (EXIF)"] = _format_datetime(exif["DateTimeOriginal"])

                    # Camera / Device
                    if "Make" in exif:
                        metadata["Camera Make"] = exif["Make"]
                    if "Model" in exif:
                        metadata["Camera Model"] = exif["Model"]

                    # Software / Editor (indicates edits)
                    if "Software" in exif:
                        metadata["Software"] = exif["Software"]

                    # Exposure settings
                    if "ExposureTime" in exif:
                        try:
                            metadata["ExposureTime"] = str(exif["ExposureTime"])
                        except Exception:
                            pass
                    if "FNumber" in exif:
                        try:
                            # FNumber can be rational
                            fnum = _safe_float(exif["FNumber"])
                            if fnum:
                                metadata["FNumber"] = f"f/{fnum}"
                        except Exception:
                            pass
                    if "ISOSpeedRatings" in exif:
                        metadata["ISO"] = exif["ISOSpeedRatings"]
                    if "FocalLength" in exif:
                        fl = exif["FocalLength"]
                        flv = _safe_float(fl)
                        if flv:
                            metadata["FocalLength(mm)"] = f"{flv}"

                    # GPS
                    lat, lon, gps_raw = _extract_gps_info(exif_data)
                    if lat is not None and lon is not None:
                        metadata["GPS Latitude"] = f"{lat:.6f}"
                        metadata["GPS Longitude"] = f"{lon:.6f}"
                        metadata["Google Maps"] = f"https://maps.google.com/?q={lat:.6f},{lon:.6f}"
                        metadata["GPS Raw"] = gps_raw
            except Exception as e:
                # keep EXIF error info for forensic trace
                metadata["EXIF_Error"] = str(e)

        # Print in a forensic-friendly format
        print("[Metadata Extraction] Success:")
        for k, v in metadata.items():
            print(f"   {k}: {v}")
        return metadata

    except Exception as e:
        print(f"[Metadata Extraction] Failed: {e}")
        return None

