from __future__ import annotations

from typing import Sequence, Optional, Dict, Set
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Radar, grid

from src.theme import (
    BG_DARK,
    FG_LIGHT,
    INLAB_BLUE,
    ACCENT_ORANGE,
    fonts,
    apply_mpl_theme,
)

# =========================================================
# PREPARACIÓN DE DATOS
# =========================================================
def prepare_radar_values(
    df: pd.DataFrame,
    metrics: Sequence[str],
    player_col: str,
    players: Sequence[str],
    lower_is_better: Set[str] | None = None,
    q_low: float = 0.10,
    q_high: float = 0.90,
):
    """
    Calcula:
    - params válidos
    - rangos (low / high)
    - media / mediana
    - valores por jugador
    """
    lower_is_better = lower_is_better or set()

    params = [
        m for m in metrics
        if m in df.columns and pd.api.types.is_numeric_dtype(df[m])
    ]

    if not params:
        raise ValueError("❌ No hay métricas numéricas válidas para radar.")

    low = df[params].quantile(q_low).tolist()
    high = df[params].quantile(q_high).tolist()
    mean_vals = df[params].mean().tolist()
    median_vals = df[params].median().tolist()

    player_vals: Dict[str, list[float]] = {}
    for p in players:
        row = df[df[player_col].astype(str).str.strip() == str(p).strip()]
        if row.empty:
            player_vals[p] = [np.nan] * len(params)
        else:
            player_vals[p] = row[params].iloc[0].astype(float).tolist()

    return params, low, high, mean_vals, median_vals, player_vals


# =========================================================
# RADAR – InLab v2.0
# =========================================================
def graficar_radar(
    df: pd.DataFrame,
    jugadores: Sequence[str],
    metricas: Sequence[str],
    referencia: Optional[str] = None,  # None | "media" | "mediana"
    colores_jugadores: Optional[Sequence[str]] = None,
    color_referencia: Optional[str] = None,
    player_col: str = "Jugador",
    lower_is_better: Set[str] | None = None,
    q_low: float = 0.10,
    q_high: float = 0.90,
    guardar: bool = False,
    filename: str = "radar.png",
):
    """
    Radar InLab v2.0
    - Tema dark
    - Tipografía Inter
    - Fondo sólido (copy & export)
    - Referencia media / mediana
    """

    # =========================================================
    # THEME
    # =========================================================
    apply_mpl_theme()
    f = fonts()
    lower_is_better = lower_is_better or set()

    params, low, high, mean_vals, median_vals, player_vals = prepare_radar_values(
        df=df,
        metrics=metricas,
        player_col=player_col,
        players=jugadores,
        lower_is_better=lower_is_better,
        q_low=q_low,
        q_high=q_high,
    )

    names = list(jugadores)
    values = [player_vals[j] for j in jugadores]

    # =========================================================
    # REFERENCIA (media / mediana)
    # =========================================================
    if referencia == "media":
        names.append("Media")
        values.append(mean_vals)
        color_ref = color_referencia or "#aaaaaa"

    elif referencia == "mediana":
        names.append("Mediana")
        values.append(median_vals)
        color_ref = color_referencia or "#888888"

    # =========================================================
    # COLORES
    # =========================================================
    if colores_jugadores is None:
        colores = [INLAB_BLUE, ACCENT_ORANGE, "#7AC3FF", "#FFD580"]
    else:
        colores = list(colores_jugadores)

    if referencia in ("media", "mediana"):
        colores.append(color_ref)

    if len(colores) < len(names):
        colores = (colores * 3)[:len(names)]

    # =========================================================
    # RADAR BASE
    # =========================================================
    radar = Radar(
        params,
        low,
        high,
        lower_is_better=list(lower_is_better),
        round_int=[False] * len(params),
        num_rings=4,
        ring_width=1,
        center_circle_radius=1,
    )

    fig, axs = grid(
        figheight=14,
        grid_height=0.82,      # 🎛️ AJUSTE: tamaño del radar
        title_height=0.08,     # 🎛️ AJUSTE: espacio títulos
        endnote_height=0.03,
        title_space=0.01,
        endnote_space=0.01,
        axis=False,
        grid_key="radar",
    )

    # =========================================================
    # FONDO SÓLIDO (preview + copiar imagen)
    # =========================================================
    fig.set_facecolor(BG_DARK)
    fig.patch.set_alpha(1)

    fig.add_artist(
        plt.Rectangle(
            (0, 0),
            1,
            1,
            transform=fig.transFigure,
            color=BG_DARK,
            zorder=-100,
        )
    )

    radar.setup_axis(ax=axs["radar"], facecolor="None")

    radar.draw_circles(
        ax=axs["radar"],
        facecolor="#2a2a2a",
        edgecolor="#555555",
        lw=1.2,
    )

    # =========================================================
    # ETIQUETAS DE MÉTRICAS (↑ 20%)
    # =========================================================
    radar.draw_param_labels(
        ax=axs["radar"],
        fontsize=24,              # 🎛️ AJUSTE: tamaño nombres métricas
        color=FG_LIGHT,
        fontproperties=f["regular"],
    )

    # =========================================================
    # DIBUJAR JUGADORES
    # =========================================================
    for name, vals, color in zip(names, values, colores):

        _, _, vertices = radar.draw_radar(
            values=vals,
            ax=axs["radar"],
            kwargs_radar=dict(facecolor=color, alpha=0.45),
            kwargs_rings=dict(facecolor="None"),
        )

        for (x, y), v in zip(vertices, vals):
            r = np.sqrt(x**2 + y**2)
            ang = np.arctan2(y, x)

            xt = (r + 0.35) * np.cos(ang)   # 🎛️ AJUSTE: distancia label
            yt = (r + 0.35) * np.sin(ang)

            axs["radar"].scatter(
                x,
                y,
                s=70,                       # 🎛️ AJUSTE: tamaño punto
                c=BG_DARK,
                edgecolors=color,
                linewidths=1.5,
                zorder=3,
            )

            axs["radar"].text(
                xt,
                yt,
                f"{v:.2f}",
                fontsize=11,                # 🎛️ AJUSTE: tamaño valor (+20%)
                color=FG_LIGHT,
                ha="center",
                va="center",
                fontproperties=f["light"],
                bbox=dict(
                    facecolor=color,
                    alpha=0.90,
                    edgecolor="none",
                    boxstyle="round,pad=0.28",
                ),
            )

    # =========================================================
    # TÍTULOS (↑ 20%)
    # =========================================================
    if len(names) == 1:
        axs["title"].text(
            0.5,
            0.6,
            names[0],
            fontsize=32,             # 🎛️ AJUSTE: tamaño título
            fontproperties=f["semibold"],
            ha="center",
            va="center",
            color=colores[0],
        )

    elif len(names) >= 2:
        axs["title"].text(
            0.02,
            0.6,
            names[0],
            fontsize=28,             # 🎛️ AJUSTE
            fontproperties=f["semibold"],
            ha="left",
            va="center",
            color=colores[0],
        )

        axs["title"].text(
            0.98,
            0.6,
            names[1],
            fontsize=28,             # 🎛️ AJUSTE
            fontproperties=f["semibold"],
            ha="right",
            va="center",
            color=colores[1],
        )

    # =========================================================
    # EXPORT
    # =========================================================
    if guardar:
        fig.canvas.draw()
        fig.savefig(
            filename,
            dpi=300,
            transparent=True,        # PNG limpio
            bbox_inches="tight",
            pad_inches=0.8,
        )

    return fig