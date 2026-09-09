"""Generate mobile-width variants of the large hero background images (needs cwebp).

The full-resolution heroes are heavy (the homepage waterfall is ~450 KB) and phones
render them small, so the page CSS serves a narrower variant under a mobile media
query. Re-run this after replacing any source image, and commit the *-mobile.webp
files it writes.

    python3 scripts/optimize-images.py
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
WIDTH = 1024
QUALITY = 72
# Above-the-fold page hero backgrounds. forest-dark (~27 KB) is already small; skipped.
SOURCES = ['hero-waterfall', 'faq-hero', 'take-action-hero', 'resources-hero',
           'mountains-sunset', 'misty-mountains', 'misty-forest', 'forest-silhouette']


def main():
    for stem in SOURCES:
        src = ASSETS / f'{stem}.webp'
        dst = ASSETS / f'{stem}-mobile.webp'
        subprocess.run(['cwebp', '-quiet', '-q', str(QUALITY), '-resize', str(WIDTH), '0',
                        str(src), '-o', str(dst)], check=True)
        print(f'{dst.name}: {dst.stat().st_size // 1024} KB (from {src.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
