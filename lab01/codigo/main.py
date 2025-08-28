import pandas as pd
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from services.git import GitHubService
from typing import Dict, List
from collections import defaultdict

from services.save_to_csv import SaveToCSV
from services.print_summary import CalculateMetrics


class MetricsAnalyzer:
    def __init__(self):
        pass



def main():
    with open("token.txt") as f:
        TOKEN = f.read().strip()

    # Coletar 1000 repositórios, conforme a especificação do laboratório
    # github_service = GitHubService(TOKEN)
    # data = github_service.collect_repositories(1000)

    # Define o diretório base para os arquivos
    base_dir = './lab01/relatorios'
    csv_path = os.path.join(base_dir, 'lab01s01_repositories.csv')
    
    # Salva CSV em relatorios/
    # SaveToCSV.save_to_csv(data, csv_path)
    df = pd.read_csv(csv_path, encoding='utf-8') # Ajuste o encoding se necessário
    repositories = df.to_dict(orient='records')

    print(f"Total repositories loaded: {len(repositories)}")
    CalculateMetrics.print_summary(repositories, os.path.join(base_dir, 'lab01s01_summary.md'))


if __name__ == "__main__":
    main()