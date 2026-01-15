from pathlib import Path
from matplotlib.font_manager import FontProperties

def load_font_from_assets(filename: str) -> FontProperties | None:
    """Load a TTF from ./assets if present. Returns None if not found."""
    assets = Path(__file__).resolve().parents[1] / "assets"
    path = assets / filename
    if path.exists():
        try:
            return FontProperties(fname=str(path))
        except Exception:
            return None
    return None
