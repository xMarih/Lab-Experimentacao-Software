import matplotlib.pyplot as plt
import os

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ03CompareReleasesCharts:
    @staticmethod
    def generate(all_releases, top10_releases, base_dir):
        """
        Gera um boxplot comparando o número de releases entre todos os repositórios e os top 10.
        """
        plt.figure(figsize=(8, 6))

        # Calcula as medianas
        median_releases_all = sorted(all_releases)[len(all_releases) // 2]
        median_releases_top10 = sorted(top10_releases)[len(top10_releases) // 2]

        # Cria o boxplot
        plt.boxplot([all_releases, top10_releases], labels=['Todos os Repositórios', 'Top 10 Repositórios'], patch_artist=True)

        # Configurações do gráfico
        plt.title(f'RQ03 - Comparação do Número de Releases (Boxplot)\nMediana (Todos): {median_releases_all:.0f}, Mediana (Top 10): {median_releases_top10:.0f}')
        plt.ylabel('Número de Releases')

        # Salva o gráfico
        compare_path = os.path.join(base_dir, 'rq03_comparacao_releases_boxplot.png')
        BaseChart.save_chart(plt, compare_path)
        compare_path =  f'./graficos/rq03_comparacao_releases_boxplot.png'
        return compare_path