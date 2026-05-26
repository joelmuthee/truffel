"""
Resize and optimize all website images to web-appropriate dimensions.
"""
from pathlib import Path
from PIL import Image

IMGS = Path(r"C:\Users\Joel\Website Designs\truffel-healthcare\images")

# (filename, max_width, max_height) — image is scaled to fit within these bounds
TARGETS = [
    # Hero background — wide landscape
    ("hero-bg.jpg",                 1920, 1080),
    # Doctor portrait — square-ish
    ("Dr-Matwa-upscaled.jpg",       900,  900),
    # About section photos
    ("about-1.jpg",                 900,  700),
    ("about-2.jpg",                 900,  700),
    # Service cards — portrait preferred
    ("service-bbl.jpg",             900, 1100),
    ("service-liposuction.png",     900, 1100),
    ("service-mastopexy.jpg",       900, 1100),
    ("service-tummytuck.png",       900, 1100),
    ("service-augmentation.jpg",    900, 1100),
    ("service-mammoplasty.jpg",     900, 1100),
    # Before/after pairs — portrait
    ("ba-lipo-before.png",          900, 1100),
    ("ba-lipo-after.png",           900, 1100),
    ("ba-mastopexy-before.png",     900, 1100),
    ("ba-mastopexy-after.png",      900, 1100),
    ("ba-frontallipo-before.png",   900, 1100),
    ("ba-frontallipo-after.png",    900, 1100),
    # Breast augmentation page
    ("Breast augmentation.png",     900, 1100),
]

def resize(path: Path, max_w: int, max_h: int):
    img = Image.open(path)
    orig = img.size
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.save(str(path), "JPEG", quality=85, optimize=True)
    print(f"  {path.name}: {orig} -> {img.size}  ({path.stat().st_size // 1024} KB)")

print("Resizing images...")
for fname, w, h in TARGETS:
    p = IMGS / fname
    if p.exists():
        resize(p, w, h)
    else:
        print(f"  MISSING: {fname}")
print("Done.")
