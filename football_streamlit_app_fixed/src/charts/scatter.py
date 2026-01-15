from __future__ import annotations

from typing import Optional, Sequence, Set, List, Tuple
import unicodedata

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

BG = "#191919"
FG = "white"

def _norm(s):
    if isinstance(s, str):
        return unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("utf-8").lower()
    return str(s).lower()

def _apply_contains(df: pd.DataFrame, col: str, values: Optional[Sequence[str]]):
    if not values:
        return df
    if col not in df.columns:
        return df
    vals = [_norm(v) for v in values]
    return df[df[col].astype(str).apply(lambda x: any(v in _norm(x) for v in vals))]

def _apply_range(df: pd.DataFrame, col: str, min_v=None, max_v=None):
    if col not in df.columns:
        return df
    if min_v is not None:
        df = df[df[col] >= min_v]
    if max_v is not None:
        df = df[df[col] <= max_v]
    return df

def plot_scatter_v2(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str,
    team_col: str,
    jugador_destacado: Optional[str] = None,
    equipo_resaltado: Optional[str] = None,
    top_n: int = 5,
    color_destacado: str = "#FB8E4B",
    color_equipo: str = "red",
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
):
    df_f = df.copy()
    df_f.columns = df_f.columns.str.strip()

    # categoricals (contains)
    df_f = _apply_contains(df_f, "Temporada", temporadas)
    df_f = _apply_contains(df_f, "País", paises)
    df_f = _apply_contains(df_f, "Liga", ligas)
    df_f = _apply_contains(df_f, "Jugador", jugadores)
    df_f = _apply_contains(df_f, "Equipo", equipos)
    df_f = _apply_contains(df_f, "Pie", pies)
    df_f = _apply_contains(df_f, "Posición específica", posiciones)

    # ranges
    df_f = _apply_range(df_f, "Minutos jugados", min_minutos, max_minutos)
    df_f = _apply_range(df_f, "Edad", min_edad, max_edad)
    df_f = _apply_range(df_f, "Altura", min_altura, max_altura)

    # reference lines
    if ref_type.lower().startswith("med"):
        ref_x = float(df_f[x_col].median())
        ref_y = float(df_f[y_col].median())
        ref_label = "Mediana"
    else:
        ref_x = float(df_f[x_col].mean())
        ref_y = float(df_f[y_col].mean())
        ref_label = "Media"

    top_pct = df_f.sort_values(by=y_col, ascending=False).head(top_n)
    top_vol = df_f.sort_values(by=x_col, ascending=False).head(top_n)
    destacados = pd.concat([top_pct, top_vol])[label_col].astype(str).unique().tolist()

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    ax.axvline(ref_x, color="gray", linestyle="--", lw=1)
    ax.axhline(ref_y, color="gray", linestyle="--", lw=1)

    if subtitulo is None:
        subtitulo = f"{x_col} vs {y_col}"

    if titulo_principal:
        fig.suptitle(titulo_principal, fontsize=18, fontweight="bold", y=0.97, fontproperties=font, color=FG)
    ax.set_title(subtitulo, fontsize=14, pad=10, fontproperties=font, color=FG)
    ax.set_xlabel(x_col, fontproperties=font, color=FG)
    ax.set_ylabel(y_col, fontproperties=font, color=FG)
    ax.tick_params(colors=FG)

    for spine in ["top","right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["bottom","left"]:
        ax.spines[spine].set_color(FG)

    # plot points
    for _, row in df_f.iterrows():
        jugador = str(row[label_col])
        x = row[x_col]
        y = row[y_col]
        equipo = str(row[team_col]) if team_col in df_f.columns else ""

        etq = False
        bbox_color = None
        alpha = 0.85
        if jugador_destacado and jugador == str(jugador_destacado):
            fc, ec, sz, etq, bbox_color, alpha = color_destacado, "black", 70, True, color_destacado, 0.85
        elif equipo_resaltado and _norm(equipo_resaltado) in _norm(equipo):
            fc, ec, sz, etq, bbox_color, alpha = color_equipo, "black", 60, True, color_equipo, 0.95
        elif jugador in destacados:
            fc, ec, sz, etq, bbox_color, alpha = color_top, "black", 50, True, color_top, 0.85
        else:
            fc, ec, sz, etq = color_resto, "none", 30, False

        ax.scatter(x, y, s=sz, c=fc, edgecolors=ec, linewidths=0.8, alpha=0.8, zorder=3)

        if etq:
            ax.annotate(
                jugador, (x, y),
                textcoords="offset points", xytext=(14, 10),
                fontsize=9, ha="left", va="bottom",
                fontweight="bold" if jugador_destacado and jugador == str(jugador_destacado) else "normal",
                fontproperties=font,
                color="black",
                bbox=dict(boxstyle="round,pad=0.3", fc=bbox_color, ec=fc, lw=1, alpha=alpha),
            )

    ax.text(
        0.99, 0.01,
        f"{ref_label} {x_col}: {ref_x:.2f}\n{ref_label} {y_col}: {ref_y:.2f}",
        ha="right", va="bottom",
        fontsize=9, color="lightgray",
        transform=ax.transAxes,
        fontproperties=font,
    )

    fig.tight_layout()
    return fig, df_f
