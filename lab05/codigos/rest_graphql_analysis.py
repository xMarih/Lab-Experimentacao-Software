from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
LAB_ROOT = BASE_DIR.parent
RELATORIOS_DIR = LAB_ROOT / "relatorios"
RESULTS_FILE = RELATORIOS_DIR / "experiment_results.csv"
SUMMARY_FILE = RELATORIOS_DIR / "experiment_summary.csv"


def load_results(csv_path: Path) -> pd.DataFrame:
    """Load the experiment output as a DataFrame."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find results file at '{csv_path}'")
    return pd.read_csv(csv_path)


def describe_by_api(df: pd.DataFrame) -> None:
    """Print descriptive statistics for each API type."""
    for api_name, subset in df.groupby("API_Type"):
        print(f"\n--- {api_name} ---")
        print("Tempo de resposta (s):")
        print(subset["Response_Time"].describe())
        print("\nTamanho da resposta (bytes):")
        print(subset["Response_Size"].describe())


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate aggregated metrics grouped by API type."""
    aggregations = {
        "Response_Time": ["mean", "std"],
        "Response_Size": ["mean", "std"],
    }
    summary = df.groupby("API_Type").agg(aggregations)
    summary.columns = ["_".join(col).strip() for col in summary.columns.to_flat_index()]
    return summary


def persist_summary(summary: pd.DataFrame, csv_path: Path) -> None:
    """Persist the aggregated summary to disk."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(csv_path)
    print(f"\nResumo salvo em '{csv_path.name}'.")


def run_analysis(
    results_path: Path = RESULTS_FILE, summary_path: Path = SUMMARY_FILE
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """High-level helper that mirrors the original script behaviour."""
    results = load_results(results_path)
    describe_by_api(results)
    summary = build_summary(results)
    persist_summary(summary, summary_path)
    return results, summary


if __name__ == "__main__":
    run_analysis()
