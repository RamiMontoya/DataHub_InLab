import streamlit as st
import pandas as pd
import numpy as np

def overview(df: pd.DataFrame):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filas", f"{df.shape[0]:,}".replace(",", "."))
    c2.metric("Columnas", f"{df.shape[1]:,}".replace(",", "."))
    c3.metric("Nulos", f"{int(df.isna().sum().sum()):,}".replace(",", "."))
    c4.metric("Duplicados", f"{int(df.duplicated().sum()):,}".replace(",", "."))

def missing_table(df: pd.DataFrame, top_n: int = 30):
    miss = df.isna().mean().sort_values(ascending=False)
    miss = (miss * 100).round(2)
    out = miss.head(top_n).reset_index()
    out.columns = ["columna", "%_nulos"]
    st.dataframe(out, use_container_width=True)

def numeric_describe(df: pd.DataFrame):
    num = df.select_dtypes(include=[np.number])
    if num.empty:
        st.info("No hay columnas numéricas para describir.")
        return
    st.dataframe(num.describe().T, use_container_width=True)
