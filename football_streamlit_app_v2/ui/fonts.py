# ui/fonts.py

from matplotlib.font_manager import FontProperties
import os

ASSETS_FONTS = "assets/fonts"

def load_font(name: str, size: int = 12, weight: str = "regular"):
    path = os.path.join(ASSETS_FONTS, name)
    if not os.path.exists(path):
        return None
    return FontProperties(fname=path, size=size, weight=weight)