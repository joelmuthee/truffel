"""
Re-export the clinic photos from Doc's full-resolution originals, cleaned up for the web.

Only global corrections, the same way a photographer would in Lightroom:
white balance, levels, a little contrast and colour, clarity, sharpening, resize.
Nothing inside the frame is added, removed or retouched.

Source: client-photos/  (full-res iPhone originals, 3024x4032)
Output: images/running/NN.jpg, images/hero-bg.jpg  (EXIF stripped, so no GPS leaks)

    python tools/enhance_photos.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "client-photos" / "Home Page running photos"
OUT = ROOT / "images"

# output name -> (source file, long edge px)
PHOTOS = {
    "hero-bg.jpg":     ("IMG_8533.jpg", 2400),  # reception, hero
    "running/01.jpg":  ("IMG_8533.jpg", 1800),  # reception
    "running/03.jpg":  ("IMG_8543.jpg", 1800),  # theatre, wide
    "running/04.jpg":  ("IMG_8546.jpg", 1800),  # theatre, portrait
    "running/07.jpg":  ("IMG_8537.jpg", 1800),  # corridor + pharmacy
    "running/09.jpg":  ("IMG_0092.jpg", 1800),  # patient monitor
    "running/12.jpg":  ("IMG_0453.jpg", 1800),  # surgical team at work
    "running/15.jpg":  ("IMG_8541.jpg", 1800),  # recovery room
}


def white_balance(a: np.ndarray, strength: float = 0.7) -> np.ndarray:
    """Neutralise the colour cast using the brightest low-saturation pixels
    (ceiling panels, lights, white walls), which should read as white."""
    lum = a.mean(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    mask = (lum > np.percentile(lum, 90)) & (sat < 40) & (lum < 250)
    if mask.sum() < 500:
        return a
    ref = a[mask].mean(axis=0)
    gain = ref.mean() / ref
    gain = 1 + (gain - 1) * strength
    return np.clip(a * gain, 0, 255)


def levels(a: np.ndarray, lo_pct: float = 0.4, hi_pct: float = 99.6) -> np.ndarray:
    """Stretch luminance so blacks are black and whites are white, keeping hue."""
    lum = a.mean(axis=2)
    lo, hi = np.percentile(lum, lo_pct), np.percentile(lum, hi_pct)
    if hi - lo < 50:
        return a
    return np.clip((a - lo) * (255.0 / (hi - lo)), 0, 255)


def enhance(src: Path, long_edge: int) -> Image.Image:
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    a = white_balance(a)
    a = levels(a)
    im = Image.fromarray(a.astype(np.uint8))

    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.08)
    # clarity: large-radius, low-amount unsharp lifts midtone depth
    im = im.filter(ImageFilter.UnsharpMask(radius=40, percent=18, threshold=0))

    w, h = im.size
    scale = long_edge / max(w, h)
    if scale < 1:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    # output sharpening after the resize
    return im.filter(ImageFilter.UnsharpMask(radius=1.1, percent=70, threshold=2))


def main():
    for out_name, (src_name, long_edge) in PHOTOS.items():
        dest = OUT / out_name
        im = enhance(SRC / src_name, long_edge)
        im.save(dest, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"{out_name:18} {im.size[0]}x{im.size[1]}  {dest.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
