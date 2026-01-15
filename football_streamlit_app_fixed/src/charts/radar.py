from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Optional, Dict, Tuple, Set

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from mplsoccer import Radar, grid

BG = "#191919"

def prepare_radar_values(
    df: pd.DataFrame,
    metrics: Sequence[str],
    player_col: str = "Jugador",
    players: Sequence[str] = (),
    lower_is_better: Set[str] | None = None,
    q_low: float = 0.10,
    q_high: float = 0.90,
) -> tuple[list[str], list[float], list[float], list[float], list[float], dict[str, list[float]]]:
    """Compute params, low/high (q_low/q_high), mean, median and values per player."""
    lower_is_better = lower_is_better or set()

    params = [m for m in metrics if m in df.columns and pd.api.types.is_numeric_dtype(df[m])]
    if not params:
        raise ValueError("No hay métricas numéricas válidas para radar.")

    low = df[params].quantile(q_low).tolist()
    high = df[params].quantile(q_high).tolist()
    mean_vals = df[params].mean().tolist()
    median_vals = df[params].quantile(0.50).tolist()

    vals_by_player: Dict[str, list[float]] = {}
    for p in players:
        row = df[df[player_col].astype(str).str.strip() == str(p).strip()]
        if row.empty:
            vals_by_player[str(p)] = [float("nan")] * len(params)
        else:
            vals_by_player[str(p)] = row[params].iloc[0].astype(float).tolist()

    return params, low, high, mean_vals, median_vals, vals_by_player


def plot_radar(
    params: Sequence[str],
    low: Sequence[float],
    high: Sequence[float],
    names: Sequence[str],
    values: Sequence[Sequence[float]],
    colors: Optional[Sequence[str]] = None,
    lower_is_better: Sequence[str] | None = None,
    show_max_labels: bool = False,
    font_thin: Optional[FontProperties] = None,
    font_bold: Optional[FontProperties] = None,
    title_left: str = "",
    title_right: str = "",
) -> plt.Figure:
    """Your style: dark bg, labels, value callouts, transparent-friendly."""
    assert len(names) == len(values), "names y values deben tener misma longitud"

    if colors is None:
        colors = ["#4b4efb", "#FB8E4B", "#109fd5", "#7AC3FF", "#FFD580"]
    if len(colors) < len(names):
        colors = list(colors) * ((len(names) // len(colors)) + 1)
        colors = colors[:len(names)]

    lower_is_better = list(lower_is_better) if lower_is_better else []

    radar = Radar(
        list(params),
        list(low),
        list(high),
        lower_is_better=lower_is_better,
        round_int=[False]*len(params),
        num_rings=4,
        ring_width=1,
        center_circle_radius=1,
    )

    fig, axs = grid(
        figheight=14,
        grid_height=0.915,
        title_height=0.06,
        endnote_height=0.025,
        title_space=0,
        endnote_space=0,
        grid_key="radar",
        axis=False,
    )
    fig.set_facecolor(BG)

    radar.setup_axis(ax=axs["radar"], facecolor="None")

    radar.draw_circles(
        ax=axs["radar"],
        facecolor="#3A3A3A",
        edgecolor="#5A5A5A",
        lw=1.5,
    )

    # optional max labels (high)
    if show_max_labels:
        num_vars = len(params)
        angles = np.linspace(0, 2*np.pi, num_vars, endpoint=False).tolist()
        for angle, h in zip(angles, high):
            x = (radar.ring_width * radar.num_rings + 0.15) * np.cos(angle)
            y = (radar.ring_width * radar.num_rings + 0.15) * np.sin(angle)
            axs["radar"].text(
                x, y, f"{h:.0f}",
                fontsize=12, ha="center", va="center",
                color="white", fontproperties=font_thin
            )

    radar.draw_param_labels(
        ax=axs["radar"],
        fontsize=21,
        color="#ffffff",
        fontproperties=font_thin
    )

    for (name, vals, color) in zip(names, values, colors):
        _, _, vertices = radar.draw_radar(
            values=list(vals),
            ax=axs["radar"],
            kwargs_radar={"facecolor": color, "alpha": 0.45},
            kwargs_rings={"facecolor": "None"},
        )

        # value labels + points
        for (x, y), v in zip(vertices, vals):
            r = np.sqrt(x*x + y*y)
            ang = np.arctan2(y, x)
            x_text = (r + 0.30) * np.cos(ang)
            y_text = (r + 0.30) * np.sin(ang)

            axs["radar"].scatter(x, y, c="#101010", edgecolors=color, s=80, zorder=3)
            axs["radar"].text(
                x_text, y_text, f"{float(v):.2f}" if np.isfinite(v) else "NA",
                fontsize=10, color="white",
                ha="center", va="center",
                bbox=dict(facecolor=color, alpha=0.90, edgecolor="none", boxstyle="round,pad=0.28"),
            )

    # titles
    if len(names) == 1:
        axs["title"].text(
            0.5, 0.65, names[0],
            fontsize=28, fontproperties=font_bold,
            ha="center", va="center", color=colors[0],
            bbox=dict(facecolor="none", edgecolor="none", pad=20),
        )
    elif len(names) >= 2:
        left = title_left or names[0]
        right = title_right or names[1]
        axs["title"].text(
            0.01, 0.65, left,
            fontsize=28, fontproperties=font_bold,
            ha="left", va="center", color=colors[0],
            bbox=dict(facecolor="none", edgecolor="none", pad=20),
        )
        axs["title"].text(
            0.99, 0.65, right,
            fontsize=28, fontproperties=font_bold,
            ha="right", va="center", color=colors[1],
            bbox=dict(facecolor="none", edgecolor="none", pad=20),
        )

    return fig
