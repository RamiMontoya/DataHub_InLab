# pages/1_Exploratorio.py
import streamlit as st
import pandas as pd
import numpy as np
import io
import zipfile
import warnings
import matplotlib.pyplot as plt
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
BASE_PATH = Path(__file__).resolve().parent.parent
FAVICON_PATH = BASE_PATH / "assets" / "logos" / "logo-claro.png"

st.set_page_config(
    page_title="InLab Data Hub — Exploratorio",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "📊",
    layout="wide",
)

# =========================================================
# THEME + HEADER
# =========================================================
from src.theme import inject_streamlit_theme, BG_DARK
from ui.header import render_header

inject_streamlit_theme()
render_header(title="InLab Sports", subtitle="Exploratorio de datos", beta=True)

# =========================================================
# IMPORTS DE DOMINIO
# =========================================================
from config.positions import BASE_POSITIONS
from config.roles import ROLES
from charts.bees import beeswarm_grid, beeswarm_single
from charts.scatter import plot_scatter_v2
from charts.radar import graficar_radar

# =========================================================
# HELPERS FIG (FONDO PARA COPY/PASTE)
# =========================================================
def set_fig_bg(fig, color=BG_DARK):
    """Fuerza fondo en figure + axes (copy/paste sin fondo blanco)."""
    if fig is None:
        return
    try:
        fig.patch.set_facecolor(color)
        fig.patch.set_alpha(1.0)

        # Radar/polar: reduce borde blanco sin tocar tus funciones
        try:
            fig.set_constrained_layout(False)
            fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        except Exception:
            pass

        for ax in getattr(fig, "axes", []):
            ax.set_facecolor(color)
    except Exception:
        pass

def show_fig(fig):
    if fig is None:
        return
    set_fig_bg(fig, BG_DARK)
    st.pyplot(fig)

# =========================================================
# SESSION STATE – INIT
# =========================================================
ss = st.session_state
ss.setdefault("df_filtrado", None)

ss.setdefault("bees_figs", {})
ss.setdefault("bees_last_ui", {})      # para export individual por métrica
ss.setdefault("scatter_params", {"fig": None, "color_equipo": "#ff0000"})
ss.setdefault("radar_figs", {})
ss.setdefault("radar_last_ui", {})     # para export

# =========================================================
# VALIDAR DATASET BASE
# =========================================================
if "df" not in ss or ss["df"] is None:
    st.warning("⚠️ Primero cargá una base de datos en la página principal.")
    st.stop()

df = ss["df"].copy()
df.columns = df.columns.str.strip()

# =========================================================
# HELPERS
# =========================================================
def parse_positions(cell):
    if pd.isna(cell):
        return set()
    return {p.strip() for p in str(cell).split(",") if p.strip()}

def filter_by_positions(df_in, positions):
    if not positions:
        return df_in
    return df_in[
        df_in["Posición específica"].apply(lambda x: bool(parse_positions(x) & set(positions)))
    ]

def filter_by_roles(df_in, roles):
    if not roles:
        return df_in
    pos = set()
    for r in roles:
        pos.update(ROLES.get(r, []))
    return df_in[
        df_in["Posición específica"].apply(lambda x: bool(parse_positions(x) & pos))
    ]

# =========================================================
# 🎛️ FILTROS GLOBALES (CASCADA EN VIVO)
# =========================================================
st.markdown("## 🎛️ Filtros globales")

df_base = df.copy()

c1, c2, c3, c4 = st.columns(4)

with c1:
    temporadas_opts = sorted(df_base["Temporada"].dropna().unique().tolist()) if "Temporada" in df_base.columns else []
    temporadas_sel = st.multiselect(
        "Temporada",
        temporadas_opts,
        key="f_temporada",
    )

df_tmp = df_base.copy()
if temporadas_sel and "Temporada" in df_tmp.columns:
    df_tmp = df_tmp[df_tmp["Temporada"].isin(temporadas_sel)]

with c2:
    paises_opts = sorted(df_tmp["País"].dropna().unique().tolist()) if "País" in df_tmp.columns else []
    paises_sel = st.multiselect(
        "País (competición)",
        paises_opts,
        key="f_pais",
    )

if paises_sel and "País" in df_tmp.columns:
    df_tmp = df_tmp[df_tmp["País"].isin(paises_sel)]

with c3:
    ligas_opts = sorted(df_tmp["Liga"].dropna().unique().tolist()) if "Liga" in df_tmp.columns else []
    ligas_sel = st.multiselect(
        "Liga",
        ligas_opts,
        key="f_liga",
    )

if ligas_sel and "Liga" in df_tmp.columns:
    df_tmp = df_tmp[df_tmp["Liga"].isin(ligas_sel)]

with c4:
    equipos_opts = sorted(df_tmp["Equipo"].dropna().unique().tolist()) if "Equipo" in df_tmp.columns else []
    equipos_sel = st.multiselect(
        "Equipo",
        equipos_opts,
        key="f_equipo",
    )

st.divider()

# =========================================================
# FILTROS ADICIONALES
# =========================================================
c5, c6, c7 = st.columns(3)

with c5:
    edades = None
    if "Edad" in df_base.columns and df_base["Edad"].notna().any():
        edades = st.slider(
            "Edad",
            int(df_base["Edad"].min()),
            int(df_base["Edad"].max()),
            (int(df_base["Edad"].min()), int(df_base["Edad"].max())),
            key="f_edad",
        )

with c6:
    minutos = None
    if "Minutos jugados" in df_base.columns and df_base["Minutos jugados"].notna().any():
        minutos = st.slider(
            "Minutos jugados (mínimo)",
            int(df_base["Minutos jugados"].min()),
            int(df_base["Minutos jugados"].max()),
            int(df_base["Minutos jugados"].min()),
            step=50,
            key="f_minutos",
        )

with c7:
    pies_sel = []
    if "Pie" in df_base.columns:
        pies_sel = st.multiselect(
            "Pie hábil",
            sorted(df_base["Pie"].dropna().unique().tolist()),
            key="f_pie",
        )

# =========================================================
# POSICIÓN / ROL
# =========================================================
st.markdown("### 🧭 Posición / Rol")

modo_pos = st.radio(
    "Filtrar por",
    ["Posición", "Rol"],
    horizontal=True,
    key="f_modo_pos",
)

if modo_pos == "Posición":
    posiciones_sel = st.multiselect("Posiciones", BASE_POSITIONS, key="f_posiciones")
    roles_sel = []
else:
    roles_sel = st.multiselect("Roles", list(ROLES.keys()), key="f_roles")
    posiciones_sel = []

# =========================================================
# APLICAR FILTROS
# =========================================================
if st.button("✅ Aplicar filtros", type="primary", key="btn_apply_filters"):
    df_f = df_base.copy()

    # cascada
    if temporadas_sel and "Temporada" in df_f.columns:
        df_f = df_f[df_f["Temporada"].isin(temporadas_sel)]
    if paises_sel and "País" in df_f.columns:
        df_f = df_f[df_f["País"].isin(paises_sel)]
    if ligas_sel and "Liga" in df_f.columns:
        df_f = df_f[df_f["Liga"].isin(ligas_sel)]
    if equipos_sel and "Equipo" in df_f.columns:
        df_f = df_f[df_f["Equipo"].isin(equipos_sel)]

    # edad / minutos
    if edades and "Edad" in df_f.columns:
        df_f = df_f[(df_f["Edad"] >= edades[0]) & (df_f["Edad"] <= edades[1])]
    if minutos is not None and "Minutos jugados" in df_f.columns:
        df_f = df_f[df_f["Minutos jugados"] >= minutos]

    # pie
    if pies_sel and "Pie" in df_f.columns:
        df_f = df_f[df_f["Pie"].isin(pies_sel)]

    # posición / rol
    if modo_pos == "Posición":
        df_f = filter_by_positions(df_f, posiciones_sel)
    else:
        df_f = filter_by_roles(df_f, roles_sel)

    ss.df_filtrado = df_f

# =========================================================
# RESULTADOS
# =========================================================
df_filtrado = ss.df_filtrado

if df_filtrado is None:
    st.info("Seleccioná filtros y presioná **Aplicar filtros**.")
    st.stop()

if df_filtrado.empty:
    st.warning("No hay jugadores que cumplan los filtros.")
    st.stop()

st.markdown("## 📋 Dataset filtrado")
st.caption(f"Jugadores: {len(df_filtrado)}")
st.dataframe(df_filtrado.head(200), height=420, width="stretch")

st.divider()
st.markdown("## 📊 Visualizaciones")

# =========================================================
# 🐝 BEES
# =========================================================
with st.expander("🐝 Bees", expanded=True):

    numeric_cols = df_filtrado.select_dtypes(include="number").columns.tolist()

    metricas = st.multiselect(
        "Métricas",
        options=numeric_cols,
        key="bees_metrics",
    )

    jugadores = st.multiselect(
        "Jugador(es)",
        options=sorted(df_filtrado["Jugador"].dropna().unique().tolist()) if "Jugador" in df_filtrado.columns else [],
        max_selections=4,
        key="bees_players",
    )

    colores = []
    if jugadores:
        st.markdown("🎨 Colores de jugadores destacados")
        base = ["#4b4efb", "#FB8E4B", "#2ecc71", "#e74c3c"]
        for i, j in enumerate(jugadores):
            colores.append(
                st.color_picker(
                    j,
                    value=base[i % len(base)],
                    key=f"bees_color_{i}_{j}",
                )
            )

    modo_viz = st.radio(
        "Modo de visualización",
        ["Comparativo", "Individual"],
        horizontal=True,
        key="bees_viz_mode",
    )

    modo_export = st.radio(
        "Modo de exportación",
        ["Grilla", "Individual por métrica"],
        horizontal=True,
        key="bees_export_mode",
    )

    # ✅ Botón de cálculo: SOLO calcula cuando apretás
    if st.button("🐝 Graficar Bees", key="run_bees_btn"):

        if not metricas:
            st.warning("Seleccioná al menos una métrica.")
        else:
            ss.bees_figs = {}
            ss.bees_last_ui = {
                "metricas": metricas,
                "jugadores": jugadores,
                "colores": colores,
                "modo_viz": modo_viz,
                "modo_export": modo_export,
            }

            with st.spinner("Generando Bees…"):
                if modo_viz == "Comparativo":
                    fig = beeswarm_grid(
                        df=df_filtrado,
                        metrics=metricas,
                        player=jugadores if jugadores else None,
                        colors=colores if colores else None,
                    )
                    ss.bees_figs["comparativo"] = fig
                else:
                    for idx, jugador in enumerate(jugadores):
                        fig = beeswarm_grid(
                            df=df_filtrado,
                            metrics=metricas,
                            player=[jugador],
                            colors=[colores[idx]] if idx < len(colores) else None,
                        )
                        ss.bees_figs[jugador] = fig

    # ✅ Mostrar SIEMPRE desde session_state
    if ss.bees_figs:
        st.markdown("### 📊 Bees generados")
        for nombre, fig in ss.bees_figs.items():
            show_fig(fig)

# =========================================================
# ⬇️ EXPORTACIÓN BEES (NO REGENERA / NO DESAPARECE)
# =========================================================
if ss.bees_figs:
    st.markdown("### ⬇️ Exportar Bees")

    bees_ui = ss.bees_last_ui or {}
    metricas_ui = bees_ui.get("metricas", [])
    jugadores_ui = bees_ui.get("jugadores", [])
    colores_ui = bees_ui.get("colores", [])
    modo_export_ui = st.session_state.get("bees_export_mode", "Grilla")
    modo_viz_ui = st.session_state.get("bees_viz_mode", "Comparativo")

    if modo_export_ui == "Grilla":
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:
            for nombre, fig in ss.bees_figs.items():
                img_buf = io.BytesIO()
                fig.savefig(img_buf, format="png", dpi=300, transparent=True, bbox_inches="tight")
                img_buf.seek(0)

                filename = f"bees_{nombre}.png".replace(" ", "_")
                zipf.writestr(filename, img_buf.read())

                st.download_button(
                    label=f"⬇️ Descargar – {nombre}",
                    data=img_buf.getvalue(),
                    file_name=filename,
                    mime="image/png",
                    key=f"download_bees_{nombre}",
                )

        zip_buf.seek(0)
        st.download_button(
            "🗜️ Descargar TODO (ZIP)",
            data=zip_buf,
            file_name="bees_grilla.zip",
            mime="application/zip",
            key="download_bees_zip_grilla",
        )

    else:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:

            if modo_viz_ui == "Comparativo":
                for metrica in metricas_ui:
                    fig_ind = beeswarm_single(
                        df=df_filtrado,
                        metric=metrica,
                        player=jugadores_ui if jugadores_ui else None,
                        colors=colores_ui if colores_ui else None,
                    )

                    img_buf = io.BytesIO()
                    fig_ind.savefig(img_buf, format="png", dpi=300, transparent=True, bbox_inches="tight")
                    img_buf.seek(0)

                    filename = f"bees_comparativo_{metrica}.png".replace(" ", "_").replace("/", "-")
                    zipf.writestr(filename, img_buf.read())

                    st.download_button(
                        label=f"⬇️ Comparativo – {metrica}",
                        data=img_buf.getvalue(),
                        file_name=filename,
                        mime="image/png",
                        key=f"dl_comp_{metrica}",
                    )

                    plt.close(fig_ind)

            else:
                for idx, jugador in enumerate(jugadores_ui):
                    for metrica in metricas_ui:
                        fig_ind = beeswarm_single(
                            df=df_filtrado,
                            metric=metrica,
                            player=jugador,
                            colors=[colores_ui[idx]] if idx < len(colores_ui) else None,
                        )

                        img_buf = io.BytesIO()
                        fig_ind.savefig(img_buf, format="png", dpi=300, transparent=True, bbox_inches="tight")
                        img_buf.seek(0)

                        filename = f"bees_{jugador}_{metrica}.png".replace(" ", "_").replace("/", "-")
                        zipf.writestr(filename, img_buf.read())

                        st.download_button(
                            label=f"⬇️ {jugador} – {metrica}",
                            data=img_buf.getvalue(),
                            file_name=filename,
                            mime="image/png",
                            key=f"dl_{jugador}_{metrica}",
                        )

                        plt.close(fig_ind)

        zip_buf.seek(0)
        st.download_button(
            "🗜️ Descargar TODO (ZIP)",
            data=zip_buf,
            file_name="bees_individuales.zip",
            mime="application/zip",
            key="download_bees_zip_ind",
        )

# =========================================================
# 📡 SCATTER
# =========================================================
with st.expander("📡 Scatter", expanded=True):

    numeric_cols = [c for c in df_filtrado.columns if np.issubdtype(df_filtrado[c].dtype, np.number)]
    if len(numeric_cols) < 2:
        st.info("Necesito al menos 2 métricas numéricas para el scatter.")
        st.stop()

    # -------------------------------------------------
    # EJES
    # -------------------------------------------------
    c1, c2 = st.columns(2)
    with c1:
        x_col = st.selectbox("Eje X", options=numeric_cols, key="scatter_x_col")
    with c2:
        y_opts = [c for c in numeric_cols if c != x_col]
        y_col = st.selectbox("Eje Y", options=y_opts, key="scatter_y_col")

    # -------------------------------------------------
    # TOP N SLIDER (🔥 NUEVO)
    # -------------------------------------------------
    top_n = st.slider(
        "Top jugadores por eje (extremos)",
        min_value=1,
        max_value=min(20, len(df_filtrado)),
        value=5,
        step=1,
        key="scatter_top_n",
    )

    # -------------------------------------------------
    # DESTACADOS
    # -------------------------------------------------
    jugadores_destacados = st.multiselect(
        "Jugadores destacados",
        options=sorted(df_filtrado["Jugador"].dropna().unique().tolist()) if "Jugador" in df_filtrado.columns else [],
        key="scatter_players",
    )

    st.markdown("🎨 Colores de jugadores")
    base_colors = ["#4b4efb", "#FB8E4B", "#2ecc71", "#e74c3c"]
    colores_jugadores = {}
    for i, j in enumerate(jugadores_destacados):
        colores_jugadores[j] = st.color_picker(
            j,
            value=base_colors[i % len(base_colors)],
            key=f"scatter_color_{i}_{j}",
        )

    # -------------------------------------------------
    # EQUIPO DESTACADO
    # -------------------------------------------------
    equipo_resaltado = st.selectbox(
        "Equipo destacado",
        options=["(None)"] + (sorted(df_filtrado["Equipo"].dropna().unique().tolist()) if "Equipo" in df_filtrado.columns else []),
        key="scatter_team",
    )

    color_equipo = st.color_picker(
        "Color del equipo",
        value=ss.scatter_params.get("color_equipo", "#ff0000"),
        key="scatter_team_color",
    )
    ss.scatter_params["color_equipo"] = color_equipo

    # -------------------------------------------------
    # REFERENCIA
    # -------------------------------------------------
    ref_type = st.radio(
        "Líneas de referencia",
        ["Mediana", "Media"],
        horizontal=True,
        key="scatter_ref_type",
    )

    # -------------------------------------------------
    # BOTÓN
    # -------------------------------------------------
    if st.button("📡 Graficar Scatter", type="primary", key="run_scatter_btn"):

        fig_scatter, _ = plot_scatter_v2(
            df=df_filtrado,
            x_col=x_col,
            y_col=y_col,
            label_col="Jugador",
            team_col="Equipo",
            jugadores_destacados=jugadores_destacados,
            colores_jugadores=colores_jugadores,
            equipo_resaltado=None if equipo_resaltado == "(None)" else equipo_resaltado,
            color_equipo=color_equipo,
            ref_type=ref_type,
            top_n=top_n,   # 🔥 PASAMOS EL SLIDER
        )

        ss.scatter_params["fig"] = fig_scatter

    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------
    fig_scatter = ss.scatter_params.get("fig")
    if fig_scatter is not None:

        st.markdown("### 📊 Scatter generado")
        show_fig(fig_scatter)

        buf = io.BytesIO()
        fig_scatter.savefig(
            buf,
            format="png",
            dpi=300,
            transparent=True,
            bbox_inches="tight",
        )
        buf.seek(0)

        filename = (
            f"scatter_{x_col}_vs_{y_col}_top{top_n}.png"
            .replace(" ", "_")
            .replace("/", "-")
        )

        st.download_button(
            "⬇️ Descargar PNG",
            data=buf,
            file_name=filename,
            mime="image/png",
            key="dl_scatter_png",
        )

# =========================================================
# 🕸 RADAR (MÉTRICAS EN FORM, COLORES REACTIVOS, CÁLCULO SOLO BOTÓN)
# =========================================================
with st.expander("🕸 Radar", expanded=True):

    # --- init state ---
    if "radar_figs" not in st.session_state:
        st.session_state.radar_figs = {}
    if "radar_last_inputs" not in st.session_state:
        st.session_state.radar_last_inputs = None
    if "radar_go" not in st.session_state:
        st.session_state.radar_go = False

    # -----------------------------
    # 1) MÉTRICAS (NO “REACCIONAN” HASTA APLICAR)
    # -----------------------------
    with st.form("radar_metrics_form", clear_on_submit=False):
        metricas_radar = st.multiselect(
            "Métricas (Radar)",
            options=df_filtrado.select_dtypes(include="number").columns.tolist(),
            key="radar_metrics",
        )
        apply_metrics = st.form_submit_button("✅ Aplicar métricas")

    # Si aplicó métricas, guardamos un “snapshot” para usarlo en el cálculo
    if apply_metrics:
        st.session_state["radar_metrics_applied"] = list(metricas_radar)

    # Usamos métricas aplicadas (si no hay, usamos lo actual del widget como fallback)
    metricas_aplicadas = st.session_state.get("radar_metrics_applied", list(metricas_radar))

    # -----------------------------
    # 2) UI REACTIVA (fuera del form)
    # -----------------------------
    jugadores_radar = st.multiselect(
        "Jugador(es)",
        options=sorted(df_filtrado["Jugador"].dropna().unique()),
        max_selections=4,
        key="radar_players",
    )

    ref_ui = st.radio(
        "Referencia",
        ["Ninguna", "Media", "Mediana"],
        horizontal=True,
        key="radar_ref",
    )
    ref_map = {"Ninguna": None, "Media": "media", "Mediana": "mediana"}

    color_ref = None
    if ref_ui != "Ninguna":
        color_ref = st.color_picker(
            f"Color {ref_ui}",
            value="#aaaaaa" if ref_ui == "Media" else "#888888",
            key="radar_ref_color",
        )

    colores_radar = []
    if jugadores_radar:
        st.markdown("🎨 Colores de jugadores")
        base = ["#4b4efb", "#FB8E4B", "#2ecc71", "#e74c3c"]
        for i, j in enumerate(jugadores_radar):
            colores_radar.append(
                st.color_picker(
                    j,
                    value=base[i % len(base)],
                    key=f"radar_color_{j}_{i}",  # key única estable
                )
            )

    modo_export = st.radio(
        "Modo de visualización",
        [
            "Visualización simple",
            "Jugadores individuales",
            "Jugador vs referencia",
            "Primero vs resto",
            "Todas las combinaciones",
        ],
        key="radar_export_mode",
    )

    # -----------------------------
    # 3) BOTÓN (dispara el cálculo)
    # -----------------------------
    if st.button("🕸 Graficar Radar", key="run_radar_btn"):
        st.session_state.radar_go = True

    # -----------------------------
    # 4) CÁLCULO (solo si botón + inputs cambiaron)
    # -----------------------------
    if st.session_state.radar_go:

        if not metricas_aplicadas:
            st.warning("Seleccioná métricas y presioná **Aplicar métricas**.")
        elif not jugadores_radar and ref_ui == "Ninguna":
            st.warning("Seleccioná jugadores o una referencia.")
        else:
            radar_inputs = {
                "metricas": tuple(metricas_aplicadas),
                "jugadores": tuple(jugadores_radar),
                "colores": tuple(colores_radar),
                "ref": ref_map[ref_ui],
                "color_ref": color_ref,
                "modo": modo_export,
                "n_rows": int(len(df_filtrado)),
            }

            if radar_inputs != st.session_state.radar_last_inputs:
                st.session_state.radar_last_inputs = radar_inputs
                st.session_state.radar_figs = {}

                with st.spinner("Generando Radares…"):

                    if modo_export == "Visualización simple":
                        fig = graficar_radar(
                            df=df_filtrado,
                            jugadores=jugadores_radar,
                            metricas=metricas_aplicadas,
                            referencia=ref_map[ref_ui],
                            colores_jugadores=colores_radar,
                            color_referencia=color_ref,
                        )
                        st.session_state.radar_figs["radar_general"] = fig

                    elif modo_export == "Jugadores individuales":
                        for j, c in zip(jugadores_radar, colores_radar):
                            fig = graficar_radar(
                                df=df_filtrado,
                                jugadores=[j],
                                metricas=metricas_aplicadas,
                                colores_jugadores=[c],
                            )
                            st.session_state.radar_figs[j] = fig

                    elif modo_export == "Jugador vs referencia":
                        for j, c in zip(jugadores_radar, colores_radar):
                            fig = graficar_radar(
                                df=df_filtrado,
                                jugadores=[j],
                                metricas=metricas_aplicadas,
                                referencia=ref_map[ref_ui],
                                colores_jugadores=[c],
                                color_referencia=color_ref,
                            )
                            st.session_state.radar_figs[f"{j}_vs_ref"] = fig

                    elif modo_export == "Primero vs resto":
                        base_j = jugadores_radar[0]
                        base_c = colores_radar[0]
                        for j, c in zip(jugadores_radar[1:], colores_radar[1:]):
                            fig = graficar_radar(
                                df=df_filtrado,
                                jugadores=[base_j, j],
                                metricas=metricas_aplicadas,
                                colores_jugadores=[base_c, c],
                            )
                            st.session_state.radar_figs[f"{base_j}_vs_{j}"] = fig

                    elif modo_export == "Todas las combinaciones":
                        for i in range(len(jugadores_radar)):
                            for k in range(i + 1, len(jugadores_radar)):
                                j1, j2 = jugadores_radar[i], jugadores_radar[k]
                                c1_, c2_ = colores_radar[i], colores_radar[k]
                                fig = graficar_radar(
                                    df=df_filtrado,
                                    jugadores=[j1, j2],
                                    metricas=metricas_aplicadas,
                                    colores_jugadores=[c1_, c2_],
                                )
                                st.session_state.radar_figs[f"{j1}_vs_{j2}"] = fig

        # IMPORTANTÍSIMO: apagar flag para no recalcular en reruns
        st.session_state.radar_go = False

    # -----------------------------
    # 5) RENDER + EXPORT (NO REGENERA)
    # -----------------------------
    if st.session_state.radar_figs:
        st.markdown("### 📊 Radares generados")
        for nombre, fig in st.session_state.radar_figs.items():
            show_fig(fig)

        st.markdown("### ⬇️ Exportar Radar")
        for nombre, fig in st.session_state.radar_figs.items():
            buf = io.BytesIO()
            fig.savefig(
                buf,
                format="png",
                dpi=300,
                transparent=True,
                bbox_inches="tight",
            )
            buf.seek(0)

            st.download_button(
                label=f"⬇️ Descargar – {nombre}",
                data=buf,
                file_name=(f"radar_{nombre}.png".replace(" ", "_").replace("/", "-")),
                mime="image/png",
                key=f"dl_radar_{nombre}",
            )