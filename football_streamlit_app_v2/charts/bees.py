from __future__ import annotations

from typing import Sequence, Optional, List, Union, Set

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyArrowPatch
from matplotlib.font_manager import FontProperties

# =========================================================
# ESTILO GLOBAL
# =========================================================
BG = "#191919"   # fondo visible en preview / copy-paste
FG = "white"

# =========================================================
# PALETA BASE
# =========================================================
DEFAULT_PALETTE = {
    "rojo": "red",
    "amarillo": "gold",
    "verde": "limegreen",
    "gris": "gray",
    "naranja": "#FB8E4B",
}

DEFAULT_HILITE_COLORS = [
    "#4b4efb",  # azul
    "#FB8E4B",  # naranja
    "#2ecc71",  # verde
    "#e74c3c",  # rojo
]

# =========================================================
# BASE PLOT (stripplot estable)
# =========================================================
def _plot_bees(
    ax,
    aux_df: pd.DataFrame,
    palette: dict,
    size: float = 6,        # 🔧 tamaño puntos base
    jitter: float = 0.25,  # 🔧 dispersión horizontal
):
    sns.stripplot(
        ax=ax,
        y=[""] * len(aux_df),
        x="valor",
        hue="color",
        data=aux_df,
        palette=palette,
        dodge=False,
        size=size,
        orient="h",
        jitter=jitter,
        alpha=0.85,
        legend=False,
    )

# =========================================================
# CALLOUT (línea curva + texto jugador)
# =========================================================
def _add_callout(
    ax,
    x_val: float,
    y_val: float,
    text: str,
    font: Optional[FontProperties] = None,
    label_y_offset: float = 0.30,  # 🔧 distancia vertical etiqueta
    curve_rad: float = 0.30,       # 🔧 curvatura línea
    fontsize: int = 11,            # 🔧 tamaño texto jugador
):
    y_text = y_val + label_y_offset

    ax.text(
        x_val,
        y_text,
        text,
        ha="center",
        va="bottom",
        fontsize=fontsize,
        fontproperties=font,
        weight="bold",
        color=FG,
        zorder=7,
    )

    curva = FancyArrowPatch(
        (x_val, y_val),
        (x_val, y_text),
        connectionstyle=f"arc3,rad={curve_rad}",
        arrowstyle="-",
        color=FG,
        linewidth=0.9,
        zorder=6,
    )
    ax.add_patch(curva)

# =========================================================
# HIGHLIGHT DE JUGADORES
# =========================================================
def _highlight_players(
    ax,
    aux_df: pd.DataFrame,
    players: Sequence[str],
    colors: Optional[Sequence[str]] = None,
    font: Optional[FontProperties] = None,
    label_y_offsets: Sequence[float] = (0.30, 0.55, 0.80, 1.05),
    curve_rad: float = 0.30,
):
    if not players:
        return

    colors = colors or DEFAULT_HILITE_COLORS

    for idx, player in enumerate(players[:4]):
        fila = aux_df[aux_df["Jugador"].str.strip() == str(player).strip()]
        if fila.empty:
            continue

        x_val = float(fila["valor"].values[0])
        y_val = 0.0
        color = colors[idx % len(colors)]

        # halo
        ax.scatter(
            x_val, y_val,
            color=color,
            s=260,            # 🔧 tamaño halo
            alpha=0.15,
            linewidth=0,
            zorder=4,
        )

        # punto principal
        ax.scatter(
            x_val, y_val,
            color=color,
            edgecolor=FG,
            linewidth=1,
            s=110,            # 🔧 tamaño punto destacado
            zorder=6,
        )

        _add_callout(
            ax,
            x_val,
            y_val,
            text=str(player),
            font=font,
            label_y_offset=label_y_offsets[idx],
            curve_rad=curve_rad,
        )

# =========================================================
# AUX DF + PERCENTILES
# =========================================================
def _build_aux_df(
    df: pd.DataFrame,
    metric: str,
    player_col: str,
    lower_is_better: Set[str],
    p_low: float,
    p_high: float,
):
    s = df[metric]
    p1 = float(s.quantile(p_low))
    p2 = float(s.quantile(p_high))

    def clasificar(v):
        if pd.isna(v):
            return "gris"
        if metric in lower_is_better:
            return "verde" if v <= p1 else "amarillo" if v <= p2 else "rojo"
        else:
            return "rojo" if v <= p1 else "amarillo" if v <= p2 else "verde"

    aux_df = pd.DataFrame({
        "Jugador": df[player_col].astype(str),
        "valor": s.astype(float),
        "color": s.apply(clasificar),
    })

    return aux_df, p1, p2

# =========================================================
# BEES – GRID
# =========================================================
def beeswarm_grid(
    df: pd.DataFrame,
    metrics: Sequence[str],
    player_col: str = "Jugador",
    player: Optional[Union[List[str], str]] = None,
    colors: Optional[List[str]] = None,
    lower_is_better: Optional[Set[str]] = None,
    p_low: float = 0.33,
    p_high: float = 0.67,
    font: Optional[FontProperties] = None,
    ncols: int = 3,
    point_size: float = 5,    # 🔧 puntos base
    title_size: int = 18,     # 🔧 tamaño título (REAL, escala con el subplot)
):
    lower_is_better = lower_is_better or set()

    metrics = [
        m for m in metrics
        if m in df.columns and np.issubdtype(df[m].dtype, np.number)
    ]

    if not metrics:
        fig = plt.figure(figsize=(8, 3), facecolor=BG)
        return fig

    players = (
        [player] if isinstance(player, str)
        else list(player) if isinstance(player, list)
        else []
    )

    n = len(metrics)
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(6 * ncols, 3.2 * nrows),
        facecolor=BG,   # 👈 CLAVE copy/paste
    )

    axes = np.array(axes).flatten()

    for i, metric in enumerate(metrics):
        ax = axes[i]
        ax.set_facecolor(BG)

        df_use = df[[player_col, metric]].dropna()
        aux_df, p1, p2 = _build_aux_df(
            df_use, metric, player_col,
            lower_is_better, p_low, p_high
        )

        _plot_bees(ax, aux_df, DEFAULT_PALETTE, size=point_size)

        # percentiles
        if metric in lower_is_better:
            ax.axvline(p1, color="green", linestyle="--", lw=1, alpha=0.6)
            ax.axvline(p2, color="red", linestyle="--", lw=1, alpha=0.6)
            ax.invert_xaxis()
        else:
            ax.axvline(p1, color="red", linestyle="--", lw=1, alpha=0.6)
            ax.axvline(p2, color="green", linestyle="--", lw=1, alpha=0.6)

        _highlight_players(
            ax,
            aux_df,
            players=players,
            colors=colors,
            font=font,
        )

        # ✅ TÍTULO REAL (escala con el subplot)
        ax.text(
            0.0, 1.08,
            metric,
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            color=FG,
            fontproperties=font,
            fontsize=title_size,   # 👈 ESTE VALOR AHORA SÍ SE NOTA
        )

        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(FG)
        ax.spines["left"].set_color(FG)
        ax.tick_params(axis="x", colors=FG)
        ax.set_ylim(-0.5, 1.2)

    for j in range(len(metrics), len(axes)):
        fig.delaxes(axes[j])

    fig.tight_layout()
    return fig

# =========================================================
# BEES – SINGLE
# =========================================================
def beeswarm_single(
    df: pd.DataFrame,
    metric: str,
    player_col: str = "Jugador",
    player: Optional[Union[str, List[str]]] = None,
    colors: Optional[List[str]] = None,
    lower_is_better: Optional[Set[str]] = None,
    p_low: float = 0.33,
    p_high: float = 0.67,
    font: Optional[FontProperties] = None,
    point_size: float = 6,
    title_size: int = 20,   # 🔧 título individual (más grande)
):
    lower_is_better = lower_is_better or set()

    fig, ax = plt.subplots(figsize=(8, 3.2), facecolor=BG)
    ax.set_facecolor(BG)

    df_use = df[[player_col, metric]].dropna()
    aux_df, p1, p2 = _build_aux_df(
        df_use, metric, player_col,
        lower_is_better, p_low, p_high
    )

    _plot_bees(ax, aux_df, DEFAULT_PALETTE, size=point_size)

    if metric in lower_is_better:
        ax.axvline(p1, color="green", linestyle="--", lw=1, alpha=0.6)
        ax.axvline(p2, color="red", linestyle="--", lw=1, alpha=0.6)
        ax.invert_xaxis()
    else:
        ax.axvline(p1, color="red", linestyle="--", lw=1, alpha=0.6)
        ax.axvline(p2, color="green", linestyle="--", lw=1, alpha=0.6)

    if player:
        players = [player] if isinstance(player, str) else list(player)
        _highlight_players(
            ax,
            aux_df,
            players=players,
            colors=colors,
            font=font,
        )

    # ✅ TÍTULO INDIVIDUAL REAL
    ax.text(
        0.0, 1.08,
        metric,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        color=FG,
        fontproperties=font,
        fontsize=title_size,
    )

    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(FG)
    ax.spines["left"].set_color(FG)
    ax.tick_params(axis="x", colors=FG)
    ax.set_ylim(-0.5, 1.2)

    fig.tight_layout()
    return fig