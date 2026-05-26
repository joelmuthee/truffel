"""
Convert base64-encoded HEIC/JPG data to JPG and save to the images folder.
Usage: python convert_heic.py <base64_file> <output_path>
Or import and call convert_b64(b64_string, output_path)
"""
import sys
import base64
import io
from pathlib import Path

def convert_b64(b64_data: str, output_path: str):
    from pillow_heif import register_heif_opener
    register_heif_opener()
    from PIL import Image

    raw = base64.b64decode(b64_data)
    img = Image.open(io.BytesIO(raw))

    # Convert to RGB if needed (HEIC can be RGBA or other modes)
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Save as JPEG regardless of the output extension in the filename
    img.save(str(out), 'JPEG', quality=85, optimize=True)
    print(f"Saved {out} ({out.stat().st_size // 1024} KB) — size: {img.size}")

if __name__ == '__main__':
    b64_file, out_path = sys.argv[1], sys.argv[2]
    b64_data = Path(b64_file).read_text().strip()
    convert_b64(b64_data, out_path)
