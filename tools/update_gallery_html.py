"""
Regenerate the gallery section HTML in all 6 cosmetic service pages.
Replaces existing .gallery-grid contents with all images currently in each folder.
"""
import re
from pathlib import Path

BASE = Path(r"C:\Users\Joel\Website Designs\truffel-healthcare")
GALLERY = BASE / "images" / "gallery"

# page path -> (gallery folder, procedure label, img alt prefix, img path prefix)
PAGES = [
    ("cosmetic/bbl.html",               "bbl",          "Brazilian Butt Lift photo",    "../images/gallery/bbl"),
    ("cosmetic/liposuction.html",        "lipo",         "Liposuction photo",             "../images/gallery/lipo"),
    ("cosmetic/mastopexy.html",          "mastopexy",    "Mastopexy photo",               "../images/gallery/mastopexy"),
    ("cosmetic/tummy-tuck.html",         "tummy-tuck",   "Tummy tuck photo",              "../images/gallery/tummy-tuck"),
    ("cosmetic/breast-augmentation.html","augmentation", "Breast augmentation photo",     "../images/gallery/augmentation"),
    ("cosmetic/breast-reduction.html",   "reduction",    "Breast reduction photo",        "../images/gallery/reduction"),
]

def build_gallery_grid(folder_name, img_prefix, alt_prefix):
    folder = GALLERY / folder_name
    imgs = sorted(folder.glob("*.jpg"), key=lambda p: int(p.stem))
    lines = ['      <div class="gallery-grid">']
    for i, img in enumerate(imgs, 1):
        lines.append(f'        <div class="gallery-item reveal" onclick="openLightbox(this)">')
        lines.append(f'          <img src="{img_prefix}/{img.name}" alt="{alt_prefix} {i}" loading="lazy">')
        lines.append(f'        </div>')
    lines.append('      </div>')
    return "\n".join(lines)

def update_page(rel_path, folder_name, alt_prefix, img_prefix):
    page = BASE / rel_path
    html = page.read_text(encoding="utf-8")

    new_grid = build_gallery_grid(folder_name, img_prefix, alt_prefix)

    # Replace everything between <div class="gallery-grid"> and matching </div>
    # 6 spaces indentation as used in actual HTML
    pattern = r'      <div class="gallery-grid">.*?      </div>'
    replacement = new_grid
    new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL)

    if n == 0:
        print(f"  WARNING: gallery-grid not found in {rel_path}")
        # Debug: show what indentation is used
        for line in html.splitlines():
            if 'gallery-grid' in line:
                spaces = len(line) - len(line.lstrip())
                print(f"  DEBUG: found gallery-grid with {spaces} leading spaces: {repr(line[:40])}")
        return
    if n > 1:
        print(f"  WARNING: {n} gallery-grids found in {rel_path} -- replaced all")

    page.write_text(new_html, encoding="utf-8")
    count = len(list((GALLERY / folder_name).glob("*.jpg")))
    print(f"  Updated {rel_path}: {count} images")

print("Updating gallery HTML...")
for rel_path, folder, alt, prefix in PAGES:
    update_page(rel_path, folder, alt, prefix)
print("Done.")
