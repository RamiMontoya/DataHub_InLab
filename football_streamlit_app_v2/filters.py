import streamlit as st
import pandas as pd

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _sorted_unique(series):
    return sorted([x for x in series.dropna().unique().tolist()])


# --------------------------------------------------
# UI de filtros globales
# --------------------------------------------------
def global_filters_ui(df: pd.DataFrame):

    if "global_filters" not in st.session_state:
        st.session_state.global_filters = {}

    f = st.session_state.global_filters

    # =============================
    # FILTROS CATEGÓRICOS
    # =============================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if "Temporada" in df.columns:
            f["Temporada"] = st.multiselect(
                "Temporada",
                _sorted_unique(df["Temporada"]),
                default=f.get("Temporada", []),
                key="f_temporada",
            )

    with c2:
        if "País" in df.columns:
            f["País"] = st.multiselect(
                "País",
                _sorted_unique(df["País"]),
                default=f.get("País", []),
                key="f_pais",
            )

    with c3:
        if "Liga" in df.columns:
            f["Liga"] = st.multiselect(
                "Liga",
                _sorted_unique(df["Liga"]),
                default=f.get("Liga", []),
                key="f_liga",
            )

    with c4:
        if "Equipo" in df.columns:
            f["Equipo"] = st.multiselect(
                "Equipo",
                _sorted_unique(df["Equipo"]),
                default=f.get("Equipo", []),
                key="f_equipo",
            )

    # =============================
    # FILTROS NUMÉRICOS / EXTRA
    # =============================
    c5, c6, c7 = st.columns(3)

    with c5:
        if "Edad" in df.columns:
            mn = int(df["Edad"].min())
            mx = int(df["Edad"].max())
            f["Edad"] = st.slider(
                "Edad",
                mn,
                mx,
                value=f.get("Edad", (mn, mx)),
                key="f_edad",
            )

    with c6:
        if "Minutos jugados" in df.columns:
            mn = int(df["Minutos jugados"].min())
            mx = int(df["Minutos jugados"].max())
            f["Minutos"] = st.slider(
                "Minutos jugados",
                mn,
                mx,
                value=f.get("Minutos", (mn, mx)),
                step=50,
                key="f_minutos",
            )

    with c7:
        if "Pie" in df.columns:
            f["Pie"] = st.multiselect(
                "Pie hábil",
                _sorted_unique(df["Pie"]),
                default=f.get("Pie", []),
                key="f_pie",
            )


# --------------------------------------------------
# Aplicar filtros
# --------------------------------------------------
def apply_global_filters(df: pd.DataFrame) -> pd.DataFrame:
    f = st.session_state.get("global_filters", {})
    out = df.copy()

    def _isin(col):
        nonlocal out
        vals = f.get(col, [])
        if vals and col in out.columns:
            out = out[out[col].isin(vals)]

    for c in ["Temporada", "País", "Liga", "Equipo", "Pie"]:
        _isin(c)

    if "Edad" in f and "Edad" in out.columns:
        mn, mx = f["Edad"]
        out = out[(out["Edad"] >= mn) & (out["Edad"] <= mx)]

    if "Minutos" in f and "Minutos jugados" in out.columns:
        mn, mx = f["Minutos"]
        out = out[(out["Minutos jugados"] >= mn) & (out["Minutos jugados"] <= mx)]

    return out