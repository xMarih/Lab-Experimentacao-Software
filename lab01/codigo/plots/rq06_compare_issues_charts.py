import matplotlib.pyplot as plt
import os

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ06CompareIssuesCharts:
    @staticmethod
    def generate(all_ratios, top10_ratios, base_dir):
        """
        Gera um boxplot comparando o percentual de issues fechadas entre todos os repositórios e os top 10.
        """
        plt.figure(figsize=(8, 6))

        # Calcula as medianas
        median_ratios_all = sorted(all_ratios)[len(all_ratios) // 2]
        median_ratios_top10 = sorted(top10_ratios)[len(top10_ratios) // 2]

        # Cria o boxplot
        plt.boxplot([all_ratios, top10_ratios], labels=['Todos os Repositórios', 'Top 10 Repositórios'], patch_artist=True)

        # Configurações do gráfico
        plt.title(f'RQ06 - Comparação do Percentual de Issues Fechadas (Boxplot)\nMediana (Todos): {median_ratios_all:.2f}%, Mediana (Top 10): {median_ratios_top10:.2f}%')
        plt.ylabel('Percentual de Issues Fechadas')

        # Salva o gráfico
        compare_path = os.path.join(base_dir, 'rq06_comparacao_issues_boxplot.png')
        BaseChart.save_chart(plt, compare_path)
        compare_path =  f'./graficos/rq06_comparacao_issues_boxplot.png'
        return compare_path