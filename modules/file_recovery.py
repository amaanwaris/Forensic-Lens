# modules/file_recovery.py  ✅ FINAL STABLE BUILD
import os, subprocess
from datetime import datetime

def recover_files(image_path, log_callback=None):
    """
    Recover deleted files using 'foremost'.
    Saves inside current CASE folder → ./Recovered/Recovered_timestamp/
    """

    try:
        if not image_path:
            msg = "[File Recovery] ❌ No input file!"
            print(msg)
            if log_callback: log_callback(msg)
            return None

        # ✅ Ensure recovery goes inside CASE folder
        case_dir = os.getcwd()
        recovered_root = os.path.join(case_dir, "Recovered")
        os.makedirs(recovered_root, exist_ok=True)

        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join(recovered_root, f"Recovered_{ts}")
        os.makedirs(output_dir, exist_ok=True)

        msg = f"[File Recovery] 🔍 Running Foremost...\n📂 Input: {image_path}\n📁 Output Folder: {output_dir}"
        print(msg)
        if log_callback: log_callback(msg)

        cmd = ["foremost", "-i", image_path, "-o", output_dir]
        proc = subprocess.run(cmd, text=True, capture_output=True)

        if proc.stdout:
            print(proc.stdout)
            if log_callback: log_callback(proc.stdout)
        if proc.stderr:
            print(proc.stderr)
            if log_callback: log_callback(proc.stderr)

        done = f"[File Recovery] ✅ Recovery Completed → {output_dir}"
        print(done)
        if log_callback: log_callback(done)

        return output_dir

    except FileNotFoundError:
        err = "❌ Foremost not found! Install using: sudo apt install foremost"
        print(err)
        if log_callback: log_callback(err)

    except Exception as e:
        err = f"[File Recovery] ❌ Error: {e}"
        print(err)
        if log_callback: log_callback(err)

    return None

