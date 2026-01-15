import streamlit as st
from src.state import init_state

init_state()

st.set_page_config(page_title="Football Explorer", layout="wide")
st.title("🏟️ Football Explorer")

st.markdown(
    """Esta app está organizada en páginas:
- **Exploratorio**: cargar dataset, aplicar filtros globales y ver resumen.
- **Jugadores similares (PCA)**: filtrar por posición/minutos, elegir jugador+temporada y obtener similares.

Usá el menú de la izquierda para navegar.
"""
)
