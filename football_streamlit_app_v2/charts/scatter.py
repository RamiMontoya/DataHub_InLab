from __future__ import annotations

from typing import Optional, Sequence, List, Dict
import unicodedata

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# =========================================================
# ESTILO
# =========================================================
BG = "#191919"
FG = "white"


# =========================================================
# HELPERS
# =========================================================
def _norm(s) -> str:
    """Normaliza strings para matching robusto."""
    if s is None:
        return ""
    if isinstance(s, str):
        s2 = (
            unicodedata.normalize("NFKD", s)
            .encode("ascii", "ignore")
            .decode("utf-8")
        )
        return s2.strip().lower()
    return str(s).strip().lower()


def _apply_contains(df: pd.DataFrame, col: str, values: Optional[Sequence[str]]):
    if not values or col not in df.columns:
        return df
    vals = [_norm(v) for v in values if str(v).strip() != ""]
    if not vals:
        return df
    return df[df[col].astype(str).apply(lambda x: any(v in _norm(x) for v in vals))]


def _apply_range(df: pd.DataFrame, col: str, min_v=None, max_v=None):
    if col not in df.columns:
        return df
    s = pd.to_numeric(df[col], errors="coerce")
    out = df.copy()
    out[col] = s
    if min_v is not None:
        out = out[out[col] >= min_v]
    if max_v is not None:
        out = out[out[col] <= max_v]
    return out


def _safe_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce")


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================
def plot_scatter_v2(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str,
    team_col: str,
    jugador_destacado: Optional[str] = None,
    jugadores_destacados: Optional[Sequence[str]] = None,
    colores_jugadores: Optional[Dict[str, str]] = None,
    equipo_resaltado: Optional[str] = None,
    color_equipo: str = "red",
    top_n: int = 5,
    color_destacado: str = "#FB8E4B",
    color_top: str = "dimgray",
    color_resto: str = "lightgray",
    titulo_principal: str = "",
    subtitulo: Optional[str] = None,
    min_minutos=None,
    max_minutos=None,
    min_edad=None,
    max_edad=None,
    min_altura=None,
    max_altura=None,
    temporadas=None,
    paises=None,
    ligas=None,
    jugadores=None,
    equipos=None,
    pies=None,
    posiciones=None,
    ref_type: str = "Mediana",
    font: Optional[FontProperties] = None,
) -> tuple[plt.Figure, pd.DataFrame]:
    """
    Scatter InLab v2.0
    - Fondo oscuro completo (copy/paste sin bordes blancos)
    - Multi jugadores destacados
    - Equipo destacado
    - Media / Mediana
    """

    df_f = df.copy()
    df_f.columns = df_f.columns.str.strip()

    # -----------------------------
    # FILTROS
    # -----------------------------
    df_f = _apply_contains(df_f, "Temporada", temporadas)
    df_f = _apply_contains(df_f, "País", paises)
    df_f = _apply_contains(df_f, "Liga", ligas)
    df_f = _apply_contains(df_f, "Equipo", equipos)
    df_f = _apply_contains(df_f, "Pie", pies)
    df_f = _apply_contains(df_f, "Posición específica", posiciones)

    df_f = _apply_range(df_f, "Minutos jugados", min_minutos, max_minutos)
    df_f = _apply_range(df_f, "Edad", min_edad, max_edad)
    df_f = _apply_range(df_f, "Altura", min_altura, max_altura)

    df_f[x_col] = _safe_numeric(df_f, x_col)
    df_f[y_col] = _safe_numeric(df_f, y_col)
    df_f = df_f.dropna(subset=[x_col, y_col, label_col]).copy()

    if df_f.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.text(0.5, 0.5, "No hay datos para graficar",
                ha="center", va="center", fontsize=14, color=FG)
        ax.axis("off")
        return fig, df_f

    # -----------------------------
    # REFERENCIA
    # -----------------------------
    if str(ref_type).lower().startswith("med"):
        ref_x = df_f[x_col].median()
        ref_y = df_f[y_col].median()
        ref_label = "Mediana"
    else:
        ref_x = df_f[x_col].mean()
        ref_y = df_f[y_col].mean()
        ref_label = "Media"

    # -----------------------------
    # TOP EXTREMOS
    # -----------------------------
    top_n = min(top_n, len(df_f))
    destacados_top = (
        pd.concat([
            df_f.sort_values(y_col, ascending=False).head(top_n),
            df_f.sort_values(x_col, ascending=False).head(top_n),
        ])[label_col]
        .astype(str)
        .unique()
        .tolist()
    )
    destacados_top_norm = {_norm(j) for j in destacados_top}

    # -----------------------------
    # DESTACADOS MANUALES
    # -----------------------------
    jugadores_destacados = list(jugadores_destacados) if jugadores_destacados else []
    if jugador_destacado:
        jugadores_destacados.append(jugador_destacado)

    seen = set()
    jugadores_clean = []
    for j in jugadores_destacados:
        nj = _norm(j)
        if nj and nj not in seen:
            seen.add(nj)
            jugadores_clean.append(j)

    jugadores_norm = {_norm(j) for j in jugadores_clean}
    colores_jugadores = colores_jugadores or {}
    colores_norm = {_norm(k): v for k, v in colores_jugadores.items()}

    equipo_norm = _norm(equipo_resaltado) if equipo_resaltado else ""

    # =========================================================
    # FIGURA
    # =========================================================
    fig, ax = plt.subplots(figsize=(12, 8))

    # 🔑 FONDO TOTAL DEL LIENZO (copy/paste)
    fig.patch.set_facecolor(BG)
    fig.patch.set_alpha(1.0)
    ax.set_facecolor(BG)

    # 🔑 ELIMINAR MÁRGENES BLANCOS DEL CANVAS
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Referencias
    ax.axvline(ref_x, color="gray", linestyle="--", lw=1)
    ax.axhline(ref_y, color="gray", linestyle="--", lw=1)

    if subtitulo is None:
        subtitulo = f"{x_col} vs {y_col}"

    if titulo_principal:
        fig.suptitle(
            titulo_principal,
            fontsize=20,          # ⬅️ ajustar tamaño título general
            fontweight="bold",
            y=0.96,
            fontproperties=font,
            color=FG,
        )

    ax.set_title(
        subtitulo,
        fontsize=16,             # ⬅️ tamaño subtítulo
        pad=14,
        fontproperties=font,
        color=FG,
    )

    ax.set_xlabel(x_col, fontsize=13, fontproperties=font, color=FG)
    ax.set_ylabel(y_col, fontsize=13, fontproperties=font, color=FG)
    ax.tick_params(colors=FG)

    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["bottom", "left"]:
        ax.spines[s].set_color(FG)

    # -----------------------------
    # BASE SCATTER
    # -----------------------------
    ax.scatter(
        df_f[x_col],
        df_f[y_col],
        s=26,
        c=color_resto,
        alpha=0.75,
        edgecolors="none",
        zorder=1,
    )

    # -----------------------------
    # DESTACADOS
    # -----------------------------
    for _, r in df_f.iterrows():
        jugador = str(r[label_col]).strip()
        jn = _norm(jugador)
        equipo = str(r[team_col]) if team_col in df_f.columns else ""

        is_player = jn in jugadores_norm
        is_team = equipo_norm and equipo_norm in _norm(equipo)
        is_top = jn in destacados_top_norm

        if not (is_player or is_team or is_top):
            continue

        if is_player:
            fc = colores_norm.get(jn, color_destacado)
            sz, z = 70, 5
        elif is_team:
            fc = color_equipo
            sz, z = 60, 4
        else:
            fc = color_top
            sz, z = 50, 3

        ax.scatter(
            r[x_col],
            r[y_col],
            s=sz,
            c=fc,
            edgecolors="black",
            linewidths=0.8,
            zorder=z,
        )

        ax.annotate(
            jugador,
            (r[x_col], r[y_col]),
            textcoords="offset points",
            xytext=(14, 10),
            fontsize=10,          # ⬅️ tamaño etiquetas
            fontweight="bold" if is_player else "normal",
            fontproperties=font,
            color="black",
            bbox=dict(
                boxstyle="round,pad=0.3",
                fc=fc,
                ec=fc,
                alpha=0.95,
            ),
            zorder=z + 1,
        )

    # -----------------------------
    # TEXTO REFERENCIA
    # -----------------------------
    ax.text(
        0.99,
        0.01,
        f"{ref_label} {x_col}: {ref_x:.2f}\n{ref_label} {y_col}: {ref_y:.2f}",
        ha="right",
        va="bottom",
        fontsize=10,          # ⬅️ tamaño texto referencia
        color="lightgray",
        transform=ax.transAxes,
        fontproperties=font,
    )

    fig.tight_layout(pad=0.5)
    return fig, df_f