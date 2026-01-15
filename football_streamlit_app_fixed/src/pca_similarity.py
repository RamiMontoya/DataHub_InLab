import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import euclidean_distances

def run_pca_similarity(df_pos: pd.DataFrame, kpis: list[str], jugador: str, temporada: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Devuelve:
      - df_modelado: df_pos + PCA1, PCA2, distancia
      - df_similares: df_modelado sin el jugador objetivo, ordenado por distancia asc
    """
    df_pos = df_pos.copy()
    df_pos = df_pos.dropna(subset=kpis)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_pos[kpis])

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    df_pos["PCA1"] = X_pca[:, 0]
    df_pos["PCA2"] = X_pca[:, 1]

    ref = df_pos[(df_pos["Jugador"] == jugador) & (df_pos["Temporada"] == temporada)]
    if ref.empty:
        raise ValueError("No encontré el jugador+temporada en la base filtrada. Probá con otra temporada o relajá filtros.")

    dist = euclidean_distances(ref[["PCA1","PCA2"]], df_pos[["PCA1","PCA2"]])[0]
    df_pos["distancia"] = dist

    df_similares = df_pos[df_pos["Jugador"] != jugador].sort_values("distancia", ascending=True)
    return df_pos, df_similares
