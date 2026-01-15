import streamlit as st
import matplotlib.pyplot as plt

from src.state import init_state
from src.data import uploader_ui
from src.pca_similarity import run_pca_similarity

init_state()

st.title("🔎 Jugadores Similares (PCA)")

# Asegurar dataset cargado (si entran directo a esta página)
if st.session_state.df_raw is None:
    df = uploader_ui()
    if df is not None:
        st.session_state.df_raw = df

df = st.session_state.df_raw
if df is None:
    st.info("Subí un dataset para comenzar.")
    st.stop()

# KPIs: tomados de tu script (podés editar esta lista)
kpis = [
    'Acciones defensivas realizadas/90', "Duelos aéreos ganados, %","Duelos atacantes ganados, %",
    "xA/90", "Jugadas claves/90", "Precisión pases en el último tercio, %", 'Acciones de ataque exitosas/90', 'xG/90',
    'Remates/90', "Duelos defensivos ganados, %", 'Regates exitosos/90', 'Precisión regates, %',
    'Pases en profundidad/90', 'Precisión pases en profundidad, %', 'Pases/90', 'Precisión pases, %'
]

# Chequeo rápido de KPIs faltantes
faltan = [c for c in kpis if c not in df.columns]
if faltan:
    st.warning(f"Hay KPIs que no están en tu dataset (se omiten): {', '.join(faltan[:8])}" + ("..." if len(faltan)>8 else ""))
    kpis = [c for c in kpis if c in df.columns]

if not kpis:
    st.error("No quedaron KPIs disponibles para correr PCA. Revisá nombres de columnas.")
    st.stop()

st.subheader("1) Filtro base por posición y minutos")
min_minutos = st.slider("Minutos jugados mínimos", 0, int(df["minutos_jugados"].max()) if "minutos_jugados" in df.columns else 2000, 300, step=50)
texto_posicion = st.text_input("Contiene en posición (ej: CB|LCB|RCB)", value="")

if st.button("Aplicar filtro (posición/minutos)", type="primary"):
    df_pos = df.copy()
    if "minutos_jugados" in df_pos.columns:
        df_pos = df_pos[df_pos["minutos_jugados"] >= min_minutos]
    if texto_posicion and "posicion" in df_pos.columns:
        df_pos = df_pos[df_pos["posicion"].astype(str).str.contains(texto_posicion, case=False, na=False)]
    df_pos = df_pos.dropna(subset=kpis)
    st.session_state.df_pos = df_pos
    st.success(f"Base filtrada: {df_pos.shape[0]} filas")

df_pos = st.session_state.df_pos
if df_pos is None or df_pos.empty:
    st.info("Aplicá el filtro para habilitar el modelo.")
    st.stop()

st.subheader("2) Elegí jugador + temporada y corré el modelo")
jugador = st.selectbox("Jugador de referencia", options=sorted(df_pos["Jugador"].dropna().unique().tolist()))
temporadas_j = sorted(df_pos[df_pos["Jugador"] == jugador]["Temporada"].dropna().unique().tolist()) if "Temporada" in df_pos.columns else []
temporada = st.selectbox("Temporada", options=temporadas_j if temporadas_j else sorted(df_pos["Temporada"].dropna().unique().tolist()))

if st.button("Correr similitud (PCA)", type="primary"):
    try:
        df_modelado, df_similares = run_pca_similarity(df_pos, kpis, jugador, temporada)
        st.session_state.df_modelado = df_modelado
        st.session_state.similares = df_similares
        st.success("Modelo corrido.")
    except Exception as e:
        st.error(str(e))

df_sim = st.session_state.similares
df_modelado = st.session_state.df_modelado

if df_sim is None or df_modelado is None:
    st.stop()

st.subheader("3) Visualización PCA")
# Scatter simple (luego lo llevamos a tu estética)
fig, ax = plt.subplots()
ax.scatter(df_modelado["PCA1"], df_modelado["PCA2"], alpha=0.35)
ref = df_modelado[(df_modelado["Jugador"] == jugador) & (df_modelado["Temporada"] == temporada)]
if not ref.empty:
    ax.scatter(ref["PCA1"], ref["PCA2"], s=80)
ax.set_xlabel("PCA1")
ax.set_ylabel("PCA2")
st.pyplot(fig, use_container_width=True)

st.subheader("4) Filtros adicionales sobre resultados")
cols = st.columns(4)
with cols[0]:
    filtro_pais = st.multiselect("País", options=sorted(df_sim["País"].dropna().unique().tolist())) if "País" in df_sim.columns else []
with cols[1]:
    filtro_liga = st.multiselect("Liga", options=sorted(df_sim["Liga"].dropna().unique().tolist())) if "Liga" in df_sim.columns else []
with cols[2]:
    filtro_pie = st.multiselect("Pie", options=sorted(df_sim["Pie"].dropna().unique().tolist())) if "Pie" in df_sim.columns else []
with cols[3]:
    filtro_nac = st.multiselect("Nacionalidad", options=sorted(df_sim["Nacionalidad"].dropna().unique().tolist())) if "Nacionalidad" in df_sim.columns else []

if st.button("Aplicar filtros adicionales"):
    out = df_sim.copy()
    if filtro_pais: out = out[out["País"].isin(filtro_pais)]
    if filtro_liga: out = out[out["Liga"].isin(filtro_liga)]
    if filtro_pie: out = out[out["Pie"].isin(filtro_pie)]
    if filtro_nac: out = out[out["Nacionalidad"].isin(filtro_nac)]
    st.session_state.similares = out
    st.success("Filtros aplicados.")

st.subheader("5) Tabla final")
n = st.slider("Cantidad de jugadores a mostrar", 5, 200, 20, step=5)
cols_show = [c for c in ["Jugador","País","Edad","Liga","Equipo","Temporada","Pie","posicion","minutos_jugados","distancia"] if c in st.session_state.similares.columns]
st.dataframe(st.session_state.similares[cols_show].head(n), use_container_width=True)
