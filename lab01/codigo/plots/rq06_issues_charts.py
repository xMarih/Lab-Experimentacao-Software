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
    def generate(closed_ratios, base_dir):
        median_ratio = sorted(closed_ratios)[len(closed_ratios) // 2]

        # Histograma
        plt.figure(figsize=(8, 6))
        plt.hist(closed_ratios, bins=20, color='lightcoral', edgecolor='black')
        plt.axvline(median_ratio, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_ratio:.2f}%')
        plt.title('RQ06 - Distribuição do Percentual de Issues Fechadas (Histograma)')
        plt.xlabel('Percentual de Issues Fechadas')
        plt.ylabel('Frequência')
        plt.legend()
        hist_path = os.path.join(base_dir, 'rq06_issues_hist.png')
        BaseChart.save_chart(plt, hist_path)

        # Boxplot
        plt.figure(figsize=(8, 6))
        plt.boxplot(closed_ratios, vert=False, patch_artist=True, showfliers=False)
        plt.title('RQ06 - Percentual de Issues Fechadas (Box Plot)')
        plt.xlabel('Percentual de Issues Fechadas')
        box_path = os.path.join(base_dir, 'rq06_issues_box.png')
        BaseChart.save_chart(plt, box_path)

        return hist_path, box_path
