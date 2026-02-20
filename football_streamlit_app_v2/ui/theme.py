# =========================================================
# InLab – Theme v2.0
# Tipografías, colores y helpers globales
# =========================================================

from pathlib import Path
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties

# =========================================================
# PATHS
# =========================================================
BASE_PATH = Path(__file__).resolve().parent.parent
ASSETS_PATH = BASE_PATH / "assets"
FONTS_PATH = ASSETS_PATH / "fonts"
LOGO_PATH = ASSETS_PATH / "logo" / "logo-in.png"

# =========================================================
# COLORES INSTITUCIONALES
# =========================================================
INLAB_BLUE = "#4b4efb"      # color principal
ACCENT_ORANGE = "#FB8E4B"   # secundario (destacados puntuales)
BG_DARK = "#191919"
BG_DARK_2 = "#232323"
FG_LIGHT = "#FFFFFF"
FG_MUTED = "#B0B0B0"
GRID_COLOR = "#444444"



# =========================================================
# TIPOGRAFÍAS (INTER)
# =========================================================
_INTER_FONTS = {
    "light": FONTS_PATH / "Inter-Light.ttf",
    "regular": FONTS_PATH / "Inter-Regular.ttf",
    "semibold": FONTS_PATH / "Inter-SemiBold.ttf",
}

_fonts_cache = None


def load_inter_fonts():
    """
    Carga Inter Light / Regular / SemiBold.
    Devuelve un dict con FontProperties listos para usar.
    Se cachea para no recargar múltiples veces.
    """
    global _fonts_cache

    if _fonts_cache is not None:
        return _fonts_cache

    fonts = {}

    for key, path in _INTER_FONTS.items():
        if not path.exists():
            raise FileNotFoundError(f"❌ Fuente Inter no encontrada: {path}")
        fm.fontManager.addfont(str(path))
        fonts[key] = FontProperties(fname=str(path))

    _fonts_cache = fonts
    return fonts


# =========================================================
# SHORTCUTS DE FUENTES (comodidad)
# =========================================================
def fonts():
    """
    Accesos rápidos:
    f["light"], f["regular"], f["semibold"]
    """
    return load_inter_fonts()


# =========================================================
# CONFIGURACIÓN GLOBAL MATPLOTLIB
# =========================================================
def apply_mpl_theme():
    """
    Aplica configuración base de matplotlib
    (colores, grids, fondo).
    """
    import matplotlib as mpl

    mpl.rcParams.update({
        "figure.facecolor": BG_DARK,
        "axes.facecolor": BG_DARK,
        "axes.edgecolor": FG_LIGHT,
        "axes.labelcolor": FG_LIGHT,
        "xtick.color": FG_LIGHT,
        "ytick.color": FG_LIGHT,
        "text.color": FG_LIGHT,
        "axes.grid": False,
        "grid.color": GRID_COLOR,
        "font.size": 11,
        "savefig.facecolor": "none",
        "savefig.edgecolor": "none",
    })


# =========================================================
# STREAMLIT – DARK THEME + AZUL INLAB
# =========================================================
def inject_streamlit_theme():
    """
    Inyecta CSS para:
    - Dark mode
    - Azul InLab como color primario
    - Inputs, sliders, botones consistentes
    """
    import streamlit as st

    st.markdown(
        f"""
        <style>
        /* Fondo general */
        .stApp {{
            background-color: {BG_DARK};
            color: {FG_LIGHT};
        }}

        /* Headers */
        h1, h2, h3, h4 {{
            color: {FG_LIGHT};
        }}

        /* Botones */
        .stButton > button {{
            background-color: {INLAB_BLUE};
            color: white;
            border-radius: 6px;
            border: none;
            padding: 0.45rem 0.9rem;
            font-weight: 600;
        }}

        .stButton > button:hover {{
            background-color: #3a3ee0;
        }}

        /* Sliders */
        div[data-baseweb="slider"] > div {{
            color: {INLAB_BLUE};
        }}

        /* Multiselect / Select */
        .stMultiSelect div, .stSelectbox div {{
            background-color: {BG_DARK_2};
            color: {FG_LIGHT};
        }}

        /* Tabs */
        button[data-baseweb="tab"] {{
            color: {FG_MUTED};
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {INLAB_BLUE};
            border-bottom: 2px solid {INLAB_BLUE};
        }}

        /* Dataframe */
        .stDataFrame {{
            background-color: {BG_DARK_2};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# UTILIDADES DE EXPORTACIÓN
# =========================================================
def save_figure(
    fig,
    path,
    dpi=300,
    transparent=True,
    pad_inches=0.4,
):
    """
    Guardado consistente de figuras.
    """
    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches="tight",
        transparent=transparent,
        pad_inches=pad_inches,
    )


# =========================================================
# Alias de compatibilidad
# =========================================================
inject_theme_css = inject_streamlit_theme