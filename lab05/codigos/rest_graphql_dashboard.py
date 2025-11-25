from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
LAB_ROOT = BASE_DIR.parent
GRAPH_DIR = LAB_ROOT / "Graficos"
CSV_PATH = LAB_ROOT / "relatorios" / "experiment_results.csv"


def ensure_graph_dir(directory: Path) -> Path:
    """Guarantee that the output directory exists."""
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def load_results(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Resultados nao encontrados em '{csv_path}'")
    return pd.read_csv(csv_path)


def plot_histogram(data: pd.DataFrame, column: str, title: str, xlabel: str, target: Path) -> None:
    plt.figure()
    for api_name, subset in data.groupby("API_Type"):
        plt.hist(subset[column], bins=10, alpha=0.5, label=api_name)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frequencia")
    plt.legend()
    plt.tight_layout()
    plt.savefig(target)
    plt.close()
    print(f"Grafico salvo: {target}")


def plot_response_size_bar(data: pd.DataFrame, target: Path) -> None:
    means = data.groupby("API_Type")["Response_Size"].mean()
    plt.figure()
    means.plot(kind="bar", color=["skyblue", "orange"])
    plt.title("Tamanho medio da resposta por API")
    plt.ylabel("Tamanho da resposta (bytes)")
    plt.xlabel("Tipo de API")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(target)
    plt.close()
    print(f"Grafico salvo: {target}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera graficos a partir de experiment_results.csv")
    parser.add_argument("--time-out", dest="time_out", default="response_time_distribution.png")
    parser.add_argument("--size-out", dest="size_out", default="response_size_distribution.png")
    parser.add_argument("--csv", dest="csv_path", default=str(CSV_PATH))
    parser.add_argument("--out-dir", dest="out_dir", default=str(GRAPH_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_path = Path(args.csv_path)
    out_dir = ensure_graph_dir(Path(args.out_dir))
    df = load_results(csv_path)

    plot_histogram(
        df,
        column="Response_Time",
        title="Distribuicao do tempo de resposta (GitHub API)",
        xlabel="Tempo (s)",
        target=out_dir / args.time_out,
    )

    plot_response_size_bar(
        df,
        target=out_dir / args.size_out,
    )


if __name__ == "__main__":
    main()
