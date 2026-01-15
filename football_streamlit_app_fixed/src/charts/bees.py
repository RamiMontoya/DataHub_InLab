from __future__ import annotations

from typing import Iterable, Sequence, Optional, Set, List, Union

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyArrowPatch
from matplotlib.font_manager import FontProperties

DEFAULT_PALETTE = {
    "rojo": "red",
    "amarillo": "gold",
    "verde": "limegreen",
    "gris": "gray",
    "naranja": "#FB8E4B",
}

BG = "#191919"
FG = "white"
HILITE_COLORS = ("#4b4efb", "#FB8E4B")


def plot_bees(ax, aux_df: pd.DataFrame, palette: dict, size: float = 6, jitter: float = 0.25, threshold: int = 150):
    """Swarm para pocos puntos, strip para muchos (mucho más rápido)."""
    n = len(aux_df)
    if n <= threshold:
        sns.swarmplot(
            ax=ax,
            y=[""] * n,
            x="valor",
            hue="color",
            data=aux_df,
            palette=palette,
            dodge=False,
            size=size,
            orient="h",
            legend=False,
        )
    else:
        sns.stripplot(
            ax=ax,
            y=[""] * n,
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


def _add_callout(ax, x_val: float, y_val: float, text: str, font: Optional[FontProperties] = None,
                 text_color: str = FG, line_color: str = FG,
                 label_y_offset: float = 0.30, curve_rad: float = 0.30, fontsize: int = 11):
    y_text = y_val + label_y_offset
    ax.text(
        x_val, y_text, str(text),
        ha="center", va="bottom",
        fontsize=fontsize,
        fontproperties=font,
        weight="bold",
        color=text_color,
        zorder=7,
    )
    curva = FancyArrowPatch(
        (x_val, y_val), (x_val, y_text),
        connectionstyle=f"arc3,rad={curve_rad}",
        arrowstyle="-",
        color=line_color,
        linewidth=0.8,
        zorder=6,
    )
    ax.add_patch(curva)


def _highlight_players(ax, aux_df: pd.DataFrame, players: Sequence[str], font: Optional[FontProperties] = None,
                       show_labels: bool = True, label_y_offsets: tuple = (0.30, 0.55), curve_rad: float = 0.30):
    """Destaca 1 o 2 jugadores en el mismo gráfico."""
    if not players:
        return
    players = [p for p in players if p is not None][:2]

    for idx, p in enumerate(players):
        fila = aux_df[aux_df["Jugador"].str.strip() == str(p).strip()]
        if fila.empty:
            continue
        x_val = float(fila["valor"].values[0])
        y_val = 0.0
        color = HILITE_COLORS[idx % len(HILITE_COLORS)]

        ax.scatter(x_val, y_val, color=color, s=220, alpha=0.12, linewidth=0, zorder=4)
        ax.scatter(x_val, y_val, color=color, edgecolor=FG, linewidth=1, s=100, zorder=6)

        if show_labels:
            _add_callout(
                ax,
                x_val=x_val,
                y_val=y_val,
                text=str(p),
                font=font,
                label_y_offset=label_y_offsets[idx % len(label_y_offsets)],
                curve_rad=curve_rad,
                fontsize=11,
            )


def _aux_df_for_metric(df: pd.DataFrame, metric: str, player_col: str, lower_is_better: Set[str],
                       p_low: float, p_high: float) -> tuple[pd.DataFrame, float, float]:
    s = df[metric]
    p1 = float(s.quantile(p_low))
    p2 = float(s.quantile(p_high))

    def clasificar(v):
        if pd.isna(v):
            return "gris"
        if metric in lower_is_better:
            # invertido: bajo=verde, alto=rojo
            if v <= p1:
                return "verde"
            elif v <= p2:
                return "amarillo"
            else:
                return "rojo"
        else:
            # normal: bajo=rojo, alto=verde
            if v <= p1:
                return "rojo"
            elif v <= p2:
                return "amarillo"
            else:
                return "verde"

    aux_df = pd.DataFrame({
        "Jugador": df[player_col].astype(str),
        "valor": s.astype(float),
        "color": s.apply(clasificar),
    })
    return aux_df, p1, p2


def beeswarm_single(
    df: pd.DataFrame,
    metric: str,
    player_col: str = "Jugador",
    player: Optional[Union[List[str], str]] = None,
    lower_is_better: Set[str] | None = None,
    p_low: float = 0.33,
    p_high: float = 0.67,
    font: Optional[FontProperties] = None,
    point_size: float = 6,
    show_player_label: bool = True,
    label_y_offset: float = 0.30,
    curve_rad: float = 0.30,
):
    lower_is_better = lower_is_better or set()

    df_use = df[[player_col, metric]].dropna(subset=[metric]).copy()
    aux_df, p1, p2 = _aux_df_for_metric(df_use, metric, player_col, lower_is_better, p_low, p_high)

    fig = plt.figure(figsize=(8, 3), facecolor=BG)
    ax = fig.add_subplot(111)
    ax.set_facecolor(BG)

    plot_bees(ax, aux_df, palette=DEFAULT_PALETTE, size=point_size)

    # Líneas percentiles (colores como tu notebook)
    if metric in lower_is_better:
        ax.axvline(p1, color="green", linestyle="--", linewidth=1, alpha=0.6)
        ax.axvline(p2, color="red", linestyle="--", linewidth=1, alpha=0.6)
        ax.invert_xaxis()
    else:
        ax.axvline(p1, color="red", linestyle="--", linewidth=1, alpha=0.6)
        ax.axvline(p2, color="green", linestyle="--", linewidth=1, alpha=0.6)

    # Highlight 0/1/2
    players = []
    if player is None:
        players = []
    elif isinstance(player, str):
        players = [player]
    else:
        players = list(player)

    _highlight_players(
        ax,
        aux_df,
        players=players,
        font=font,
        show_labels=show_player_label,
        label_y_offsets=(label_y_offset, label_y_offset + 0.25),
        curve_rad=curve_rad,
    )

    ax.set_title(metric, fontsize=14, fontproperties=font, color=FG)
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(FG)
    ax.spines["left"].set_color(FG)
    ax.tick_params(axis="x", colors=FG)
    ax.set_ylim(-0.5, 0.8)

    fig.tight_layout()
    return fig


def beeswarm_grid(
    df: pd.DataFrame,
    metrics: Sequence[str],
    ncols: int = 3,
    player_col: str = "Jugador",
    player: Optional[Union[List[str], str]] = None,
    lower_is_better: Set[str] | None = None,
    p_low: float = 0.33,
    p_high: float = 0.67,
    font: Optional[FontProperties] = None,
    point_size: float = 5,
):
    lower_is_better = lower_is_better or set()
    metrics = [m for m in metrics if m in df.columns and np.issubdtype(df[m].dtype, np.number)]
    if not metrics:
        fig = plt.figure(figsize=(8, 3), facecolor=BG)
        return fig

    n = len(metrics)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6*ncols, 3*nrows), facecolor=BG)
    axes = np.array(axes).reshape(-1)

    players = []
    if player is None:
        players = []
    elif isinstance(player, str):
        players = [player]
    else:
        players = list(player)

    for i, metric in enumerate(metrics):
        ax = axes[i]
        ax.set_facecolor(BG)
        df_use = df[[player_col, metric]].dropna(subset=[metric]).copy()
        aux_df, p1, p2 = _aux_df_for_metric(df_use, metric, player_col, lower_is_better, p_low, p_high)

        plot_bees(ax, aux_df, palette=DEFAULT_PALETTE, size=point_size)

        if metric in lower_is_better:
            ax.axvline(p1, color="green", linestyle="--", linewidth=1, alpha=0.6)
            ax.axvline(p2, color="red", linestyle="--", linewidth=1, alpha=0.6)
            ax.invert_xaxis()
        else:
            ax.axvline(p1, color="red", linestyle="--", linewidth=1, alpha=0.6)
            ax.axvline(p2, color="green", linestyle="--", linewidth=1, alpha=0.6)

        _highlight_players(ax, aux_df, players=players, font=font, show_labels=True, label_y_offsets=(0.30, 0.55), curve_rad=0.30)

        ax.set_title(metric, fontsize=10, fontproperties=font, color=FG)
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(FG)
        ax.spines["left"].set_color(FG)
        ax.tick_params(axis="x", colors=FG)
        ax.set_ylim(-0.5, 0.8)

    # remove unused axes
    for j in range(len(metrics), len(axes)):
        fig.delaxes(axes[j])

    fig.tight_layout()
    return fig


def beeswarm_grid_preset(
    df: pd.DataFrame,
    metrics: Sequence[str],
    nrows: int = 4,
    ncols: int = 3,
    player_col: str = "Jugador",
    player: Optional[Union[List[str], str]] = None,
    lower_is_better: Set[str] | None = None,
    p_low: float = 0.33,
    p_high: float = 0.67,
    font: Optional[FontProperties] = None,
    point_size: float = 5,
    show_player_label: bool = True,
    label_y_offset: float = 0.30,
    curve_rad: float = 0.30,
):
    lower_is_better = lower_is_better or set()
    metrics = [m for m in metrics if m in df.columns and np.issubdtype(df[m].dtype, np.number)]
    metrics = metrics[: nrows*ncols]
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6*ncols, 3*nrows), facecolor=BG)
    axes = axes.flatten()

    players = []
    if player is None:
        players = []
    elif isinstance(player, str):
        players = [player]
    else:
        players = list(player)

    for i, metric in enumerate(metrics):
        ax = axes[i]
        ax.set_facecolor(BG)

        df_use = df[[player_col, metric]].dropna(subset=[metric]).copy()
        aux_df, p1, p2 = _aux_df_for_metric(df_use, metric, player_col, lower_is_better, p_low, p_high)

        plot_bees(ax, aux_df, palette=DEFAULT_PALETTE, size=point_size)

        if metric in lower_is_better:
            ax.axvline(p1, color="green", linestyle="--", linewidth=1, alpha=0.6)
            ax.axvline(p2, color="red", linestyle="--", linewidth=1, alpha=0.6)
            ax.invert_xaxis()
        else:
            ax.axvline(p1, color="red", linestyle="--", linewidth=1, alpha=0.6)
            ax.axvline(p2, color="green", linestyle="--", linewidth=1, alpha=0.6)

        _highlight_players(
            ax, aux_df, players=players, font=font,
            show_labels=show_player_label,
            label_y_offsets=(label_y_offset, label_y_offset + 0.25),
            curve_rad=curve_rad
        )

        ax.set_title(metric, fontsize=10, fontproperties=font, color=FG)
        ax.set_yticks([])
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(FG)
        ax.spines["left"].set_color(FG)
        ax.tick_params(axis="x", colors=FG)
        ax.set_ylim(-0.5, 0.8)

    for j in range(len(metrics), len(axes)):
        fig.delaxes(axes[j])

    fig.tight_layout()
    return fig
