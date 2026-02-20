# =========================================================
# InLab – Theme v1.4 (NO ORANGE / FORCE STREAMLIT PRIMARY)
# src/theme.py
# =========================================================

from pathlib import Path
import matplotlib as mpl
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

# =========================================================
# PATHS
# =========================================================
BASE_PATH = Path(__file__).resolve().parent.parent
ASSETS_PATH = BASE_PATH / "assets"
FONTS_PATH = ASSETS_PATH / "fonts"
LOGOS_PATH = ASSETS_PATH / "logos"

# =========================================================
# COLORES INSTITUCIONALES
# =========================================================
INLAB_BLUE = "#4b4efb"

# 👇 mantener por compatibilidad con charts/radar.py (no lo uses en UI)
ACCENT_ORANGE = "#FB8E4B"

BG_DARK = "#191919"
BG_DARK_2 = "#232323"
FG_LIGHT = "#FFFFFF"
FG_MUTED = "#B0B0B0"
GRID_COLOR = "#444444"

# =========================================================
# TIPOGRAFÍAS – INTER
# =========================================================
_INTER_FONTS = {
    "light": FONTS_PATH / "Inter-Light.otf",
    "regular": FONTS_PATH / "Inter-Regular.otf",
    "medium": FONTS_PATH / "Inter-Medium.otf",
    "semibold": FONTS_PATH / "Inter-SemiBold.otf",
}

_fonts_cache = None


def load_inter_fonts():
    global _fonts_cache
    if _fonts_cache is not None:
        return _fonts_cache

    fonts_map = {}
    for key, path in _INTER_FONTS.items():
        if path.exists():
            fm.fontManager.addfont(str(path))
            fonts_map[key] = FontProperties(fname=str(path))

    _fonts_cache = fonts_map
    return fonts_map


def fonts():
    return load_inter_fonts()


# =========================================================
# MATPLOTLIB – THEME GLOBAL
# =========================================================
def apply_mpl_theme():
    mpl.rcParams.update({
        "figure.facecolor": BG_DARK,
        "axes.facecolor": BG_DARK,
        "savefig.facecolor": "none",
        "savefig.edgecolor": "none",

        "text.color": FG_LIGHT,
        "axes.labelcolor": FG_LIGHT,
        "xtick.color": FG_LIGHT,
        "ytick.color": FG_LIGHT,

        "axes.edgecolor": FG_LIGHT,
        "axes.grid": False,
        "grid.color": GRID_COLOR,

        "font.size": 11,
        "figure.autolayout": False,
    })


# =========================================================
# STREAMLIT – THEME + CSS (FINAL SIN NARANJA + SLIDER FIX)
# =========================================================
def inject_streamlit_theme():
    import streamlit as st

    st.markdown(
        f"""
        <style>

        /* =========================================================
           0) FORCE PRIMARY COLOR (mata naranja interno Streamlit)
        ========================================================= */
        :root {{
            --primary-color: {INLAB_BLUE} !important;
            --primaryColor: {INLAB_BLUE} !important;
            --primary-color-alpha: rgba(75, 78, 251, 0.35) !important;
            --primaryColorAlpha: rgba(75, 78, 251, 0.35) !important;

            --background-color: {BG_DARK} !important;
            --secondary-background-color: {BG_DARK_2} !important;
            --text-color: {FG_LIGHT} !important;
        }}

        /* =========================================================
           BASE
        ========================================================= */
        .stApp {{
            background-color: {BG_DARK} !important;
            color: {FG_LIGHT} !important;
        }}

        h1, h2, h3, h4 {{
            color: {FG_LIGHT} !important;
            font-weight: 600;
        }}

        .stCaption {{
            color: {FG_MUTED} !important;
        }}

        /* =========================================================
           FOCUS RINGS (NO ORANGE)
        ========================================================= */
        *:focus {{
            outline: none !important;
        }}
        *:focus-visible {{
            outline: none !important;
            box-shadow: none !important;
        }}

        input:focus, textarea:focus, select:focus {{
            outline: none !important;
            border-color: {INLAB_BLUE} !important;
            box-shadow: 0 0 0 2px rgba(75, 78, 251, 0.35) !important;
        }}

        /* =========================================================
           BUTTONS
        ========================================================= */
        .stButton > button {{
            background-color: {INLAB_BLUE} !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            font-weight: 600 !important;
        }}

        .stButton > button:hover {{
            background-color: #3a3ee0 !important;
        }}

        .stButton > button:focus,
        .stButton > button:focus-visible {{
            box-shadow: 0 0 0 3px rgba(75, 78, 251, 0.45) !important;
        }}

        /* =========================================================
           SELECT / MULTISELECT
        ========================================================= */
        div[data-baseweb="select"] {{
            background-color: {BG_DARK_2} !important;
            color: {FG_LIGHT} !important;
            border-radius: 8px !important;
        }}

        div[data-baseweb="select"] div[role="combobox"] {{
            border-color: rgba(255,255,255,0.10) !important;
            box-shadow: none !important;
        }}

        div[data-baseweb="select"] div[role="combobox"]:hover {{
            border-color: rgba(75,78,251,0.55) !important;
        }}

        div[data-baseweb="select"] div[role="combobox"]:focus,
        div[data-baseweb="select"] div[role="combobox"]:focus-visible {{
            border-color: rgba(75,78,251,0.75) !important;
            box-shadow: 0 0 0 2px rgba(75,78,251,0.35) !important;
        }}

        div[data-baseweb="menu"] div[role="option"]:hover {{
            background-color: rgba(75, 78, 251, 0.18) !important;
        }}

        div[data-baseweb="menu"] div[aria-selected="true"] {{
            background-color: rgba(75, 78, 251, 0.28) !important;
        }}

        div[data-baseweb="tag"] {{
            background-color: rgba(75, 78, 251, 0.18) !important;
            color: {FG_LIGHT} !important;
            border: 1px solid rgba(75, 78, 251, 0.55) !important;
        }}

        div[data-baseweb="tag"] * {{
            color: {FG_LIGHT} !important;
            fill: {FG_LIGHT} !important;
        }}

        /* =========================================================
           SLIDER
        ========================================================= */

        /* Track */
        div[data-baseweb="slider"] div > div > div {{
            background-color: {INLAB_BLUE} !important;
        }}

        /* Thumb */
        div[data-baseweb="slider"] div[role="slider"] > div {{
            background-color: {INLAB_BLUE} !important;
            border: 2px solid rgba(255,255,255,0.25) !important;
        }}

        /* Tooltip (valor flotante) */
        div[data-baseweb="slider"] [role="tooltip"],
        div[data-baseweb="slider"] [data-testid="stTooltip"],
        div[data-baseweb="slider"] div[aria-live="polite"] {{
            background: rgba(75, 78, 251, 0.95) !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
        }}

        /* =========================================================
           FIX DEFINITIVO: MIN/MAX LABELS (0, 67, etc.)
        ========================================================= */

        div[data-testid="stSlider"] p,
        div[data-testid="stSlider"] span,
        div[data-testid="stSlider"] small,
        div[data-testid="stSlider"] label {{
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
            opacity: 1 !important;
        }}

        div[data-testid="stSlider"] * {{
            color: #FFFFFF !important;
        }}

        /* =========================================================
           RADIO / CHECKBOX
        ========================================================= */
        input[type="radio"],
        input[type="checkbox"] {{
            accent-color: {INLAB_BLUE} !important;
        }}

        /* =========================================================
           PROGRESS / SPINNER
        ========================================================= */
        div[data-testid="stProgress"] > div > div > div {{
            background-color: {INLAB_BLUE} !important;
        }}

        div[data-testid="stSpinner"] svg {{
            stroke: {INLAB_BLUE} !important;
        }}

        .stSpinner > div {{
            border-top-color: {INLAB_BLUE} !important;
        }}

        /* =========================================================
           TEXT INPUTS
        ========================================================= */
        [data-baseweb="base-input"] input {{
            background-color: {BG_DARK_2} !important;
            color: {FG_LIGHT} !important;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# EXPORT UTIL
# =========================================================
def save_figure(fig, path, dpi=300, transparent=True, pad_inches=0.4):
    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches="tight",
        transparent=transparent,
        pad_inches=pad_inches,
    )