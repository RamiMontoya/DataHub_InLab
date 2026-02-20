import io
from typing import Optional

import matplotlib.pyplot as plt

def fig_to_png_bytes(fig, dpi: int = 300, transparent: bool = True) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, transparent=transparent, bbox_inches="tight", pad_inches=0.4)
    buf.seek(0)
    return buf.read()

def fig_to_svg_text(fig) -> str:
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight", pad_inches=0.4)
    return buf.getvalue()
