import streamlit as st
from src.state import init_state
from src.data import uploader_ui
from src.filters import global_filters_ui, apply_global_filters
from src.exploratory import overview, missing_table, numeric_describe

init_state()

st.title("📊 Exploratorio de Datos (Fútbol)")

if st.session_state.df_raw is None:
    df = uploader_ui()
    if df is not None:
        st.session_state.df_raw = df

df_raw = st.session_state.df_raw
if df_raw is None:
    st.info("Subí un dataset para comenzar.")
    st.stop()

st.subheader("Filtros globales")
global_filters_ui(df_raw)

if st.button("Aplicar filtros", type="primary"):
    st.session_state.df_global = apply_global_filters(df_raw)
    st.success("Filtros aplicados.")

df_use = st.session_state.df_global if st.session_state.df_global is not None else df_raw

st.subheader("Resumen")
overview(df_use)

with st.expander("Vista rápida (head)"):
    st.dataframe(df_use.head(50), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("Nulos (top)")
    missing_table(df_use, top_n=30)
with c2:
    st.subheader("Describe numérico")
    numeric_describe(df_use)


st.divider()
st.divider()
st.subheader("🐝 Beeswarm (abejas)")

from src.charts.bees import beeswarm_single, beeswarm_grid, beeswarm_grid_preset
from src.export_utils import fig_to_png_bytes, fig_to_svg_text
from src.theme import load_font_from_assets
import numpy as np

numeric_cols = [c for c in df_use.columns if np.issubdtype(df_use[c].dtype, np.number)]
player_col = "Jugador" if "Jugador" in df_use.columns else None

if not numeric_cols:
    st.info("No detecté columnas numéricas para graficar.")
else:
    default_metrics = [c for c in numeric_cols if c in [
        'Carreras en progresión/90','Pases largos/90','Precisión pases largos, %','Precisión pases, %',
        'Precisión pases en el último tercio, %','Centros/90','Precisión centros desde la banda izquierda, %',
        'Interceptaciones/90','Posesión conquistada después de una interceptación','Duelos defensivos ganados, %',
        'Aceleraciones/90'
    ]]
    if not default_metrics:
        default_metrics = numeric_cols[:6]

    with st.form("bees_form", clear_on_submit=False):
        mode = st.radio(
            "Layout",
            ["Una métrica", "Varias métricas (grid)", "Preset 4x3 (estilo informe)"],
            horizontal=True,
            index=2
        )

        metrics = st.multiselect("Métricas a graficar", options=numeric_cols, default=default_metrics[:12])

        if mode == "Varias métricas (grid)":
            ncols = st.slider("Columnas en grid", 2, 5, 3)
        else:
            ncols = 3  # no se usa

        # Callout (aplica a 1 o 2 jugadores)
        show_label = st.checkbox("Mostrar etiqueta + línea curva del/los jugador(es)", value=True)
        label_y_offset = st.slider("Separación vertical etiqueta", 0.10, 0.80, 0.30, 0.05)
        curve_rad = st.slider("Curvatura línea", 0.00, 0.60, 0.30, 0.05)

        p_low, p_high = st.slider("Cortes (quantiles)", 0.05, 0.95, (0.33, 0.67), step=0.01)

        lower_opts = st.multiselect(
            "Métricas donde LOWER = mejor (invertir eje)",
            options=numeric_cols,
            default=["Goles recibidos/90"] if "Goles recibidos/90" in numeric_cols else []
        )

        if player_col:
            players = st.multiselect(
                "Jugador(es) a destacar (multiselect)",
                options=sorted(df_use[player_col].dropna().astype(str).unique().tolist()),
                default=[]
            )
        else:
            players = []
            st.warning("No encontré columna 'Jugador' para destacar jugadores.")

        submitted = st.form_submit_button("Graficar", type="primary")

    if submitted:
        font = load_font_from_assets("RockySans.ttf")

        if p_low >= p_high:
            st.error("El primer corte debe ser menor que el segundo.")
            st.stop()

        if not metrics:
            st.info("Elegí al menos una métrica.")
            st.stop()

        if mode == "Una métrica" and len(metrics) != 1:
            st.warning("En 'Una métrica' seleccioná exactamente 1 métrica.")
            st.stop()

        # Regla: 0->sin destacados, 1->uno, 2->dos en el mismo, 3+->uno por jugador
        if len(players) == 0:
            runs = [None]
        elif len(players) == 1:
            runs = [players]
        elif len(players) == 2:
            runs = [players]
        else:
            runs = [[p] for p in players]

        for players_sel in runs:
            if mode == "Una métrica":
                fig = beeswarm_single(
                    df_use,
                    metric=metrics[0],
                    player_col=player_col or "Jugador",
                    player=players_sel,
                    lower_is_better=set(lower_opts),
                    p_low=p_low,
                    p_high=p_high,
                    font=font,
                    show_player_label=show_label,
                    label_y_offset=label_y_offset,
                    curve_rad=curve_rad,
                )

            elif mode == "Varias métricas (grid)":
                fig = beeswarm_grid(
                    df_use,
                    metrics=metrics,
                    ncols=ncols,
                    player_col=player_col or "Jugador",
                    player=players_sel,
                    lower_is_better=set(lower_opts),
                    p_low=p_low,
                    p_high=p_high,
                    font=font,
                )

            else:
                fig = beeswarm_grid_preset(
                    df_use,
                    metrics=metrics,
                    nrows=4,
                    ncols=3,
                    player_col=player_col or "Jugador",
                    player=players_sel,
                    lower_is_better=set(lower_opts),
                    p_low=p_low,
                    p_high=p_high,
                    font=font,
                    show_player_label=show_label,
                    label_y_offset=label_y_offset,
                    curve_rad=curve_rad,
                )

            st.pyplot(fig, use_container_width=True)

            if players_sel is None:
                fname = "bees.png"
            elif len(players_sel) == 1:
                fname = f"bees_{str(players_sel[0]).replace(' ', '_')}.png"
            else:
                fname = f"bees_{str(players_sel[0]).replace(' ', '_')}_vs_{str(players_sel[1]).replace(' ', '_')}.png"

            png_bytes = fig_to_png_bytes(fig, dpi=300, transparent=True)
            st.download_button("⬇️ Descargar PNG (transparente)", data=png_bytes, file_name=fname, mime="image/png")

            svg = fig_to_svg_text(fig)
            with st.expander("📋 Copiar SVG"):
                st.code(svg, language="xml")


st.divider()
st.subheader("📡 Scatter (v2)")

from src.charts.scatter import plot_scatter_v2
from src.export_utils import fig_to_png_bytes, fig_to_svg_text
from src.theme import load_font_from_assets
import numpy as np

numeric_cols = [c for c in df_use.columns if np.issubdtype(df_use[c].dtype, np.number)]
label_col = "Jugador" if "Jugador" in df_use.columns else df_use.columns[0]
team_col = "Equipo" if "Equipo" in df_use.columns else ("Equipo durante el período seleccionado" if "Equipo durante el período seleccionado" in df_use.columns else label_col)

if len(numeric_cols) < 2:
    st.info("Necesito al menos 2 métricas numéricas para el scatter.")
else:
    with st.form("scatter_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            x_col = st.selectbox("Eje X", options=numeric_cols, index=0)
        with c2:
            y_col = st.selectbox("Eje Y", options=[c for c in numeric_cols if c != x_col], index=0)

        top_n = st.slider("Top N (etiquetar extremos)", 1, 15, 5)

        jugador_destacado = None
        equipo_resaltado = None
        if "Jugador" in df_use.columns:
            jugador_destacado = st.selectbox("Jugador destacado (opcional)", options=["(None)"] + sorted(df_use["Jugador"].dropna().astype(str).unique().tolist()))
            if jugador_destacado == "(None)":
                jugador_destacado = None

        if team_col in df_use.columns:
            equipo_resaltado = st.selectbox("Equipo resaltado (opcional)", options=["(None)"] + sorted(df_use[team_col].dropna().astype(str).unique().tolist()))
            if equipo_resaltado == "(None)":
                equipo_resaltado = None

        ref_type = st.radio("Líneas de referencia", ["Mediana", "Media"], horizontal=True)

        submitted_scatter = st.form_submit_button("Graficar Scatter", type="primary")

    if submitted_scatter:
        font = load_font_from_assets("RockySans.ttf")
        fig, _ = plot_scatter_v2(
            df_use,
            x_col=x_col,
            y_col=y_col,
            label_col=label_col,
            team_col=team_col,
            jugador_destacado=jugador_destacado,
            equipo_resaltado=equipo_resaltado,
            top_n=top_n,
            titulo_principal="",
            subtitulo=None,
            ref_type=ref_type,
            font=font,
        )
        st.pyplot(fig, use_container_width=True)

        png_bytes = fig_to_png_bytes(fig, dpi=300, transparent=True)
        st.download_button("⬇️ Descargar PNG (transparente)", data=png_bytes, file_name="scatter.png", mime="image/png")

        svg = fig_to_svg_text(fig)
        with st.expander("📋 Copiar SVG"):
            st.code(svg, language="xml")


st.divider()
st.subheader("🕸️ Radar (mplsoccer)")

from src.charts.radar import prepare_radar_values, plot_radar
from src.export_utils import fig_to_png_bytes, fig_to_svg_text
from src.theme import load_font_from_assets
import numpy as np

numeric_cols = [c for c in df_use.columns if np.issubdtype(df_use[c].dtype, np.number)]
player_col = "Jugador" if "Jugador" in df_use.columns else None

if not player_col:
    st.info("No encuentro columna 'Jugador' para el radar.")
else:
    with st.form("radar_form", clear_on_submit=False):
        metrics = st.multiselect("Métricas del radar", options=numeric_cols, default=numeric_cols[:8])
        players = st.multiselect(
            "Jugador(es) (1 o 2 recomendado)",
            options=sorted(df_use[player_col].dropna().astype(str).unique().tolist()),
            default=[]
        )
        compare_to = st.selectbox("Comparar vs", options=["(Nada)", "Media muestra", "Mediana muestra"], index=0)

        lower_opts = st.multiselect(
            "Métricas donde LOWER = mejor",
            options=numeric_cols,
            default=["Goles recibidos/90"] if "Goles recibidos/90" in numeric_cols else []
        )

        submitted_radar = st.form_submit_button("Graficar Radar", type="primary")

    if submitted_radar:
        if not metrics:
            st.warning("Elegí al menos 3 métricas para un radar legible.")
            st.stop()
        if len(players) == 0 and compare_to == "(Nada)":
            st.warning("Elegí al menos un jugador o una referencia (media/mediana).")
            st.stop()

        # valores
        params, low, high, mean_vals, median_vals, vals_by_player = prepare_radar_values(
            df_use, metrics=metrics, player_col=player_col, players=players, lower_is_better=set(lower_opts)
        )

        names = []
        values = []
        if players:
            for p in players[:2]:
                names.append(p)
                values.append(vals_by_player[p])

        if compare_to == "Media muestra":
            names.append("Media")
            values.append(mean_vals)
        elif compare_to == "Mediana muestra":
            names.append("Mediana")
            values.append(median_vals)

        font_thin = load_font_from_assets("AVGARDN_2.TTF")
        font_bold = load_font_from_assets("AVGARDD_2.TTF")
        # fallback: si esas no están en assets, usamos Rocky
        if font_thin is None:
            font_thin = load_font_from_assets("RockySans.ttf")
        if font_bold is None:
            font_bold = load_font_from_assets("RockySans.ttf")

        fig = plot_radar(
            params=params,
            low=low,
            high=high,
            names=names,
            values=values,
            colors=["#4b4efb", "#FB8E4B", "#109fd5"],
            lower_is_better=lower_opts,
            show_max_labels=False,
            font_thin=font_thin,
            font_bold=font_bold,
        )
        st.pyplot(fig, use_container_width=True)

        png_bytes = fig_to_png_bytes(fig, dpi=300, transparent=True)
        st.download_button("⬇️ Descargar PNG (transparente)", data=png_bytes, file_name="radar.png", mime="image/png")

        svg = fig_to_svg_text(fig)
        with st.expander("📋 Copiar SVG"):
            st.code(svg, language="xml")
