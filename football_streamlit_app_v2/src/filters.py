import streamlit as st
import pandas as pd

def _sorted_unique(series):
    return sorted([x for x in series.dropna().unique().tolist()])

def global_filters_ui(df: pd.DataFrame):
    # Estos nombres siguen tu script; ajustamos si tu DB usa otros.
    filters = st.session_state.get("global_filters", {})

    cols = st.columns(4)
    with cols[0]:
        if "Temporada" in df.columns:
            filters["Temporada"] = st.multiselect("Temporada", _sorted_unique(df["Temporada"]), default=filters.get("Temporada", []))
    with cols[1]:
        if "País" in df.columns:
            filters["País"] = st.multiselect("País", _sorted_unique(df["País"]), default=filters.get("País", []))
    with cols[2]:
        if "Liga" in df.columns:
            filters["Liga"] = st.multiselect("Liga", _sorted_unique(df["Liga"]), default=filters.get("Liga", []))
    with cols[3]:
        if "Equipo" in df.columns:
            filters["Equipo"] = st.multiselect("Equipo", _sorted_unique(df["Equipo"]), default=filters.get("Equipo", []))

    cols2 = st.columns(3)
    with cols2[0]:
        if "Pie" in df.columns:
            filters["Pie"] = st.multiselect("Pie", _sorted_unique(df["Pie"]), default=filters.get("Pie", []))
    with cols2[1]:
        if "posicion" in df.columns:
            filters["posicion_contains"] = st.text_input("Posición contiene (texto)", value=filters.get("posicion_contains", ""))
    with cols2[2]:
        if "minutos_jugados" in df.columns:
            mn = int(df["minutos_jugados"].min()) if df["minutos_jugados"].notna().any() else 0
            mx = int(df["minutos_jugados"].max()) if df["minutos_jugados"].notna().any() else 0
            default = filters.get("min_minutos", min(300, mx))
            filters["min_minutos"] = st.slider("Minutos mínimos", mn, mx, int(default), step=50)

    st.session_state.global_filters = filters

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

    if "posicion" in out.columns and f.get("posicion_contains"):
        out = out[out["posicion"].astype(str).str.contains(f["posicion_contains"], case=False, na=False)]

    if "minutos_jugados" in out.columns and f.get("min_minutos") is not None:
        out = out[out["minutos_jugados"] >= f["min_minutos"]]

    return out
