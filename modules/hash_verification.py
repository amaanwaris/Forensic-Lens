# modules/hash_verification.py
import hashlib
import os

def calculate_hashes(file_path):
    """
    Forensic-focused hashing: compute MD5, SHA1, SHA256.
    Returns a dictionary: {"MD5": ..., "SHA1": ..., "SHA256": ...}
    """
    hashes = { 
        "MD5": None,
        "SHA1": None,
        "SHA256": None
    }   

    try:
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()

        # Read file in chunks to handle large files
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)

        # Save hash values
        hashes["MD5"] = md5.hexdigest()
        hashes["SHA1"] = sha1.hexdigest()
        hashes["SHA256"] = sha256.hexdigest()

        # Console output for forensic log
        print(f"[Hashing] Hashes for {file_path}:")
        for algo, value in hashes.items():
            print(f"   {algo}: {value}")

        return hashes

    except Exception as e:
        print(f"[Hashing] Error for {file_path}: {e}")
        return None

