"""Optimize original fonts: python scripts/optimize-fonts.py /path/to/originals.

Optional maintenance tool requiring fonttools[woff]; not a site build dependency.
Original font files remain available in git history. Retains optical sizing and
all characters while restricting weights to the ranges declared in fonts.css.
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

if __name__ == '__main__':
    output = Path(__file__).resolve().parents[1] / 'assets/fonts'
    for source in Path(sys.argv[1]).glob('*.woff2'):
        font = TTFont(source)
        instantiateVariableFont(font, {'wght': (400, 700 if 'public-sans' in source.name else 600)}, inplace=True)
        font.save(output / source.name)
