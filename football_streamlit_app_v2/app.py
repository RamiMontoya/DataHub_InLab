# app.py
import streamlit as st
import pandas as pd
from pathlib import Path

from src.theme import inject_streamlit_theme
from ui.header import render_header

# =========================================================
# PAGE CONFIG (SIEMPRE PRIMERO Y UNA SOLA VEZ)
# =========================================================
BASE_PATH = Path(__file__).resolve().parent
FAVICON_PATH = BASE_PATH / "assets" / "logos" / "logo-claro.png"

st.set_page_config(
    page_title="InLab Data Hub",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "📊",
    layout="wide",
)

# =========================================================
# THEME + HEADER
# =========================================================
inject_streamlit_theme()

render_header(
    title="InLab Sports",
    subtitle="Herramienta de visualización avanzada",
    beta=True,
)

# =========================================================
# CONTENIDO
# =========================================================
st.markdown("## 📂 Carga de base de datos")

st.markdown(
    """
    Subí una base de datos para comenzar el análisis.  
    Formatos soportados:
    - **Excel (.xlsx)**
    - **CSV (.csv)**
    - **Parquet (.parquet)** (recomendado para bases grandes)
    """
)

archivo = st.file_uploader(
    "Seleccioná un archivo",
    type=["xlsx", "csv", "parquet"],
)

if archivo is not None:
    try:
        # ---------- LECTURA ----------
        if archivo.name.endswith(".xlsx"):
            df = pd.read_excel(archivo)
        elif archivo.name.endswith(".csv"):
            df = pd.read_csv(archivo)
        elif archivo.name.endswith(".parquet"):
            df = pd.read_parquet(archivo)
        else:
            st.error("Formato no soportado.")
            st.stop()

        # ---------- SESSION STATE ----------
        st.session_state["df"] = df
        st.session_state["df_name"] = archivo.name

        st.success("✅ Base de datos cargada correctamente")

        st.markdown("### 📊 Resumen rápido")
        col1, col2, col3 = st.columns(3)

        col1.metric("Filas", f"{df.shape[0]:,}")
        col2.metric("Columnas", df.shape[1])
        col3.metric("Memoria (MB)", f"{df.memory_usage(deep=True).sum() / 1024**2:.1f}")

        st.dataframe(df.head(50), use_container_width=True)

        st.info("👉 Ahora podés ir a **Exploratorio de datos** desde el menú lateral.")

    except Exception as e:
        st.error("❌ Error al cargar el archivo")
        st.exception(e)
else:
    st.warning("⚠️ Todavía no cargaste ninguna base de datos.")