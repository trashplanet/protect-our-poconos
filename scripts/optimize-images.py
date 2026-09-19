"""Build the responsive WebP variants used by the site.

Source PNGs remain the master artwork. Keeping every derivative here makes image
compression reproducible instead of relying on one-off editor exports.

    python3 scripts/optimize-images.py
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
# filename, output filename, width (0 preserves source width), WebP quality
DERIVATIVES = [
    ('hero-waterfall.png', 'hero-waterfall.webp', 0, 60),
    ('hero-waterfall.png', 'hero-waterfall-mobile.webp', 768, 60),
    ('faq-hero.webp', 'faq-hero-mobile.webp', 1024, 72),
    ('take-action-hero.webp', 'take-action-hero-mobile.webp', 1024, 72),
    ('resources-hero.webp', 'resources-hero-mobile.webp', 1024, 72),
    ('mountains-sunset.webp', 'mountains-sunset-mobile.webp', 1024, 72),
    ('misty-mountains.webp', 'misty-mountains-mobile.webp', 1024, 72),
    ('misty-forest.webp', 'misty-forest-mobile.webp', 1024, 72),
    ('forest-silhouette.webp', 'forest-silhouette-mobile.webp', 1024, 72),
    ('scale-datacenter-trim.png', 'scale-datacenter-card.webp', 768, 68),
    ('scale-datacenter-trim.png', 'scale-datacenter-card-384.webp', 384, 68),
    ('misty-forest.png', 'misty-forest-card.webp', 768, 68),
    ('misty-forest.png', 'misty-forest-card-384.webp', 384, 68),
    ('forest-dark.png', 'forest-dark-card.webp', 768, 68),
    ('forest-dark.png', 'forest-dark-card-384.webp', 384, 68),
    ('mountains-sunset.png', 'mountains-sunset-card.webp', 768, 68),
    ('mountains-sunset.png', 'mountains-sunset-card-384.webp', 384, 68),
    ('misty-forest.png', 'misty-forest-1440.webp', 1440, 68),
    ('scale-house-trim.png', 'scale-house-small.webp', 480, 70),
    ('scale-house-trim.png', 'scale-house-tiny.webp', 240, 70),
    ('scale-warehouse-trim.png', 'scale-warehouse-small.webp', 480, 70),
    ('scale-warehouse-trim.png', 'scale-warehouse-tiny.webp', 240, 70),
    ('scale-datacenter-trim.png', 'scale-datacenter-small.webp', 480, 70),
    ('scale-datacenter-trim.png', 'scale-datacenter-tiny.webp', 240, 70),
    ('scale-campus-trim.png', 'scale-campus-small.webp', 480, 70),
    ('scale-campus-trim.png', 'scale-campus-tiny.webp', 240, 70),
]


def main():
    for source_name, output_name, width, quality in DERIVATIVES:
        src = ASSETS / source_name
        dst = ASSETS / output_name
        command = ['cwebp', '-quiet', '-q', str(quality)]
        if width:
            command.extend(['-resize', str(width), '0'])
        command.extend([str(src), '-o', str(dst)])
        subprocess.run(command, check=True)
        print(f'{dst.name}: {dst.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()
