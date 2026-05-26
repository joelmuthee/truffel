"""
Extract base64 image content from MCP tool-result JSON files and save as JPGs.
"""
import json, base64, io, sys
from pathlib import Path

def convert_json_to_image(json_path: str, output_path: str):
    from pillow_heif import register_heif_opener
    register_heif_opener()
    from PIL import Image

    data = json.loads(Path(json_path).read_text(encoding='utf-8'))
    b64 = data['content']
    raw = base64.b64decode(b64)

    img = Image.open(io.BytesIO(raw))
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out), 'JPEG', quality=88, optimize=True)
    print(f"  OK {out.name}  ({out.stat().st_size // 1024} KB)  {img.size}")

if __name__ == '__main__':
    # pairs = [(json_file, output_path), ...]
    pairs = []
    for i in range(0, len(sys.argv[1:]), 2):
        pairs.append((sys.argv[1 + i], sys.argv[2 + i]))
    for src, dst in pairs:
        print(f"Processing {Path(src).name} -> {dst}")
        convert_json_to_image(src, dst)
