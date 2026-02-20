
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="Cargando base de datos...")
def load_dataframe(uploaded_file):
    if uploaded_file is None:
        return None

    name = uploaded_file.name.lower()

    if name.endswith(".parquet"):
        df = pd.read_parquet(uploaded_file)
    elif name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, low_memory=False)
    elif name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        raise ValueError("Formato no soportado")

    df.columns = df.columns.str.strip()
    return df
