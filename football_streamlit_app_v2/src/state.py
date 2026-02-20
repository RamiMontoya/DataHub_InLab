import streamlit as st

def init_state():
    defaults = {
        "df_raw": None,
        "df_global": None,   # df tras filtros globales (exploratorio)
        "df_pos": None,      # df tras filtro de posición/minutos (PCA)
        "df_modelado": None, # df con PCA1/PCA2/distancia
        "similares": None,
        "global_filters": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
