import matplotlib.pyplot as plt
import os

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ02ComparePRsCharts:
    @staticmethod
    def generate(all_prs, top10_prs, base_dir):
        """
        Gera um boxplot comparando o número de pull requests aceitas entre todos os repositórios e os top 10.
        """
        plt.figure(figsize=(8, 6))

        # Calcula as medianas
        median_prs_all = sorted(all_prs)[len(all_prs) // 2]
        median_prs_top10 = sorted(top10_prs)[len(top10_prs) // 2]

        # Cria o boxplot
        plt.boxplot([all_prs, top10_prs], labels=['Todos os Repositórios', 'Top 10 Repositórios'], patch_artist=True)

        # Configurações do gráfico
        plt.title(f'RQ02 - Comparação do Número de Pull Requests Aceitas\nMediana (Todos): {median_prs_all:.0f}, Mediana (Top 10): {median_prs_top10:.0f}')
        plt.ylabel('Número de Pull Requests Aceitas')

        # Salva o gráfico
        compare_path = os.path.join(base_dir, 'rq02_comparacao_prs_boxplot.png')
        BaseChart.save_chart(plt, compare_path)

        compare_path =  f'./graficos/rq02_comparacao_prs_boxplot.png'

        return compare_path