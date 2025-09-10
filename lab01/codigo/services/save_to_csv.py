import csv
import os
from typing import Dict, List
from collections import defaultdict

import os
import matplotlib.pyplot as plt

class SaveToCSV:
    @staticmethod
    def save_to_csv(self, repositories: List[Dict], filename: str = 'github_repositories.csv'):
        """
        Salva os dados dos repositórios em arquivo CSV

        Args:
            repositories: Lista de repositórios
            filename: Nome do arquivo CSV
        """
        # Verifica se o diretório existe e cria se não existir
        dir_name = os.path.dirname(filename)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        if not repositories:
            print("Nenhum dado para salvar.")
            return

        fieldnames = repositories[0].keys()

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(repositories)

        print(f"Dados salvos em {filename}")