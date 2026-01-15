import streamlit as st
import pandas as pd

RENAME_MAP = {
    "Minutos jugados": "minutos_jugados",
    "Posición específica": "posicion",
    "País de nacimiento": "Nacionalidad",
}

@st.cache_data(show_spinner=False)
def read_dataset(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".xlsx"):
        xls = pd.ExcelFile(uploaded_file)
        df = xls.parse(xls.sheet_names[0])
    elif name.endswith(".parquet"):
        df = pd.read_parquet(uploaded_file)
    elif name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        raise ValueError("Formato no compatible. Usá .xlsx, .parquet o .csv")

    df = df.copy()
    df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
    return df

def uploader_ui():
    uploaded = st.file_uploader("Subí dataset (.xlsx / .parquet / .csv)", type=["xlsx", "parquet", "csv"])
    if uploaded is None:
        return None
    try:
        return read_dataset(uploaded)
    except Exception as e:
        st.error(f"No pude leer el archivo: {e}")
        return None
