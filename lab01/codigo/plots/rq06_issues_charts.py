import os
import matplotlib.pyplot as plt

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ06IssuesCharts:
    @staticmethod
    def generate(closed_ratios, base_dir, top_n):
        median_ratio = sorted(closed_ratios)[len(closed_ratios) // 2]

        # Histograma
        plt.figure(figsize=(8, 6))
        plt.hist(closed_ratios, bins=20, color='lightcoral', edgecolor='black')
        plt.axvline(median_ratio, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_ratio:.2f}%')
        plt.title(f'RQ06 - Distribuição do Percentual de Issues Fechadas (Histograma)\nMediana: {median_ratio:.2f}%')
        plt.xlabel('Percentual de Issues Fechadas')
        plt.ylabel('Frequência')
        plt.legend()
        hist_path = os.path.join(base_dir, f'rq06_issues_hist_{top_n}.png')
        BaseChart.save_chart(plt, hist_path)

        # Boxplot
        plt.figure(figsize=(8, 6))
        plt.boxplot(closed_ratios, vert=False, patch_artist=True, showfliers=False)
        plt.title(f'RQ06 - Percentual de Issues Fechadas (Box Plot)\nMediana: {median_ratio:.2f}%')
        plt.xlabel('Percentual de Issues Fechadas')
        box_path = os.path.join(base_dir, f'rq06_issues_box_{top_n}.png')
        BaseChart.save_chart(plt, box_path)

        hist_path =  f'./graficos/rq06_issues_hist_{top_n}.png'
        box_path =  f'./graficos/rq06_issues_box_{top_n}.png'

        return hist_path, box_path
