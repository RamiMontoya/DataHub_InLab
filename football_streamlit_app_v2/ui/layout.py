# ui/layout.py

import os, io, base64
import streamlit as st
from PIL import Image

LOGO_PATH = "assets/logos/inlab.png"

def _logo_as_base64(path: str) -> str:
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{b64}"
        img = Image.new("RGBA", (44, 44), (0, 0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
    except Exception:
        return "data:image/gif;base64,R0lGODlhAQABAAAAACw="


def render_header(
    title: str = "InLab Data Hub – Scouting IA",
    subtitle: str = "Perfiles de Similaridad · Scouting Avanzado · IA aplicada al Fútbol",
):
    logo_src = _logo_as_base64(LOGO_PATH)

    st.markdown(
        f"""
        <style>
        header[data-testid="stHeader"] {{
            background: transparent;
            box-shadow: none;
        }}

        .inlab-header {{
            position: sticky;
            top: 56px;
            z-index: 999;
            background: rgba(25,25,25,0.95);
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #2a2a2a;
        }}

        .inlab-wrap {{
            max-width: 1200px;
            margin: auto;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .inlab-logo {{
            height: 32px;
        }}

        .inlab-title {{
            font-size: 1.2rem;
            font-weight: 800;
        }}

        .inlab-sub {{
            font-size: 0.8rem;
            opacity: 0.7;
        }}
        </style>

        <div class="inlab-header">
            <div class="inlab-wrap">
                <img src="{logo_src}" class="inlab-logo"/>
                <div>
                    <div class="inlab-title">{title}</div>
                    <div class="inlab-sub">{subtitle}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )