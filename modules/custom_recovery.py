import os
import struct
import hashlib
from PIL import Image

def recover_fat32_images(device_path, output_dir="Recovered_Images", max_files=50):
    os.makedirs(output_dir, exist_ok=True)

    def log(msg):
        print(msg)

    # ================= FAT32 RECOVERY =================
    def fat32_recovery():
        recovered = 0

        with open(device_path, "rb") as f:

            boot = f.read(512)

            bytes_per_sector = struct.unpack("<H", boot[11:13])[0]
            sectors_per_cluster = boot[13]
            reserved_sectors = struct.unpack("<H", boot[14:16])[0]
            num_fats = boot[16]
            sectors_per_fat = struct.unpack("<I", boot[36:40])[0]
            root_cluster = struct.unpack("<I", boot[44:48])[0]

            fat_start = reserved_sectors * bytes_per_sector
            data_start = (reserved_sectors + num_fats * sectors_per_fat) * bytes_per_sector
            cluster_size = bytes_per_sector * sectors_per_cluster

            f.seek(fat_start)
            fat = f.read(sectors_per_fat * bytes_per_sector)

            def get_next_cluster(cluster):
                entry_offset = cluster * 4
                val = struct.unpack("<I", fat[entry_offset:entry_offset+4])[0]
                return val & 0x0FFFFFFF

            def read_cluster(cluster):
                offset = data_start + (cluster - 2) * cluster_size
                f.seek(offset)
                return f.read(cluster_size)

            def recover_chain(start_cluster):
                data = b""
                cluster = start_cluster

                while cluster < 0x0FFFFFF8:
                    data += read_cluster(cluster)
                    cluster = get_next_cluster(cluster)

                return data

            cluster = root_cluster

            while cluster < 0x0FFFFFF8:

                data = read_cluster(cluster)

                for i in range(0, len(data), 32):
                    entry = data[i:i+32]

                    if entry[0] == 0x00:
                        break

                    # DELETED FILE
                    if entry[0] == 0xE5:

                        ext = entry[8:11].decode(errors="ignore").strip().lower()

                        if ext not in ["jpg", "jpeg", "png"]:
                            continue

                        start_cluster = struct.unpack("<H", entry[26:28])[0] | \
                                        (struct.unpack("<H", entry[20:22])[0] << 16)

                        size = struct.unpack("<I", entry[28:32])[0]

                        if start_cluster < 2 or size == 0:
                            continue

                        file_data = recover_chain(start_cluster)
                        file_data = file_data[:size]

                        fname = os.path.join(output_dir, f"fat32_{recovered}.{ext}")

                        with open(fname, "wb") as out:
                            out.write(file_data)

                        # verify image
                        try:
                            Image.open(fname).verify()
                        except:
                            os.remove(fname)
                            continue

                        log(f"[FAT32] {fname}")
                        recovered += 1

                        if recovered >= max_files:
                            return recovered

                cluster = get_next_cluster(cluster)

        return recovered

    # ================= RAW CARVING (FALLBACK) =================
    def raw_recovery(start_index):
        chunk_size = 1024 * 1024
        buffer = b""
        recovered = start_index

        jpg_start = b'\xff\xd8'
        jpg_end = b'\xff\xd9'

        png_start = b'\x89PNG\r\n\x1a\n'
        png_end = b'IEND\xaeB`\x82'

        seen_hash = set()

        with open(device_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                buffer += chunk

                # JPG
                while True:
                    s = buffer.find(jpg_start)
                    if s == -1:
                        break
                    e = buffer.find(jpg_end, s)
                    if e == -1:
                        break

                    data = buffer[s:e+2]

                    h = hashlib.md5(data).hexdigest()
                    if h in seen_hash:
                        buffer = buffer[s+2:]
                        continue

                    fname = os.path.join(output_dir, f"raw_{recovered}.jpg")

                    with open(fname, "wb") as out:
                        out.write(data)

                    try:
                        Image.open(fname).verify()
                    except:
                        os.remove(fname)
                        buffer = buffer[s+2:]
                        continue

                    log(f"[RAW JPG] {fname}")
                    seen_hash.add(h)
                    recovered += 1
                    buffer = buffer[e+2:]

                    if recovered >= max_files:
                        return

                # PNG
                while True:
                    s = buffer.find(png_start)
                    if s == -1:
                        break
                    e = buffer.find(png_end, s)
                    if e == -1:
                        break

                    data = buffer[s:e+8]

                    h = hashlib.md5(data).hexdigest()
                    if h in seen_hash:
                        buffer = buffer[s+8:]
                        continue

                    fname = os.path.join(output_dir, f"raw_{recovered}.png")

                    with open(fname, "wb") as out:
                        out.write(data)

                    try:
                        Image.open(fname).verify()
                    except:
                        os.remove(fname)
                        buffer = buffer[s+8:]
                        continue

                    log(f"[RAW PNG] {fname}")
                    seen_hash.add(h)
                    recovered += 1
                    buffer = buffer[e+8:]

                    if recovered >= max_files:
                        return

                buffer = buffer[-2 * 1024 * 1024:]

    # ================= RUN =================
    log("[START] Recovering images...")

    fat_count = fat32_recovery()

    if fat_count < max_files:
        raw_recovery(fat_count)

    log("[DONE] Recovery Complete")
    return output_dir
