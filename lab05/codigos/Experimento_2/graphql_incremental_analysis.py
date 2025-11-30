from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr

BASE_DIR = Path(__file__).resolve().parent
LAB_ROOT = BASE_DIR.parents[1]
RELATORIOS_DIR = LAB_ROOT / "relatorios" / "Experimento_2"
CSV_PATH = RELATORIOS_DIR / "experiment_graphql_incremental.csv"
GRAPH_DIR = LAB_ROOT / "Experimento_2" / "Graficos_Incremental"


def load_results(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Nao encontrei os resultados em '{csv_path}'")
    return pd.read_csv(csv_path)


def derive_query_level(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    enriched["Query_Level"] = enriched["Trial_Name"].str.extract(r"(\d+)").astype(int)
    return enriched


def aggregate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("Query_Level").agg(
        Response_Time_mean=("Response_Time", "mean"),
        Response_Time_std=("Response_Time", "std"),
        Response_Size_mean=("Response_Size", "mean"),
        Response_Size_std=("Response_Size", "std"),
    )
    return grouped.reset_index()


def compute_spearman(df: pd.DataFrame, column: str) -> spearmanr:
    return spearmanr(df["Query_Level"], df[column])


def plot_with_error_bars(
    aggregated: pd.DataFrame,
    value_col: str,
    error_col: str,
    title: str,
    ylabel: str,
    output: Path,
    annotation: str,
    color: str,
) -> None:
    plt.figure()
    plt.errorbar(
        aggregated["Query_Level"],
        aggregated[value_col],
        yerr=aggregated[error_col],
        fmt="-o",
        color=color,
    )
    plt.xticks(aggregated["Query_Level"])
    plt.xlabel("Nivel logico da query (Trial_Name)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.text(
        0.95,
        0.05,
        annotation,
        transform=plt.gca().transAxes,
        ha="right",
        va="bottom",
        bbox=dict(facecolor="white", alpha=0.7),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    print(f"Grafico salvo: {output}")


def main() -> None:
    df = derive_query_level(load_results(CSV_PATH))
    aggregated = aggregate_metrics(df)

    time_corr = compute_spearman(df, "Response_Time")
    size_corr = compute_spearman(df, "Response_Size")

    print(
        f"Correlacao (Query_Level vs Tempo): rho = {time_corr.correlation:.4f}, p = {time_corr.pvalue:.4g}"
    )
    print(
        f"Correlacao (Query_Level vs Tamanho): rho = {size_corr.correlation:.4f}, p = {size_corr.pvalue:.4g}"
    )

    plot_with_error_bars(
        aggregated,
        value_col="Response_Time_mean",
        error_col="Response_Time_std",
        title="Tempo de resposta vs complexidade logica da query",
        ylabel="Tempo medio de resposta (s)",
        output=GRAPH_DIR / "tempo_vs_trialname.png",
        annotation=f"rho = {time_corr.correlation:.3f}\np = {time_corr.pvalue:.4f}",
        color="blue",
    )

    plot_with_error_bars(
        aggregated,
        value_col="Response_Size_mean",
        error_col="Response_Size_std",
        title="Tamanho da resposta vs complexidade logica da query",
        ylabel="Tamanho medio da resposta (bytes)",
        output=GRAPH_DIR / "tamanho_vs_trialname.png",
        annotation=f"rho = {size_corr.correlation:.3f}\np = {size_corr.pvalue:.4f}",
        color="green",
    )

    print(f"Graficos gerados em '{GRAPH_DIR}'")


if __name__ == "__main__":
    main()
