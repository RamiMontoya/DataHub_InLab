import streamlit as st
from pathlib import Path

from src.theme import INLAB_BLUE, FG_MUTED

# =========================================================
# ASSETS
# =========================================================
BASE_PATH = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_PATH / "assets" / "logos" / "logo-inlab.png"

# =========================================================
# HEADER
# =========================================================
def render_header(
    title: str,
    subtitle: str | None = None,
    beta: bool = False,
):
    col_logo, col_title, col_badge = st.columns([1, 8, 1])

    with col_logo:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=480)

    with col_title:
        st.markdown(
            f"""
            <div style="line-height:1.15">
                <h1 style="margin-bottom:0">{title}</h1>
                {f"<p style='color:{FG_MUTED};margin-top:4px'>{subtitle}</p>" if subtitle else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_badge:
        if beta:
            st.markdown(
                f"""
                <div style="
                    background:{INLAB_BLUE};
                    color:white;
                    padding:4px 12px;
                    border-radius:14px;
                    font-size:11px;
                    font-weight:600;
                    text-align:center;
                    margin-top:14px;
                ">
                    BETA
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<hr style='border:1px solid #2a2a2a;margin:12px 0 8px 0'>",
        unsafe_allow_html=True,
    )