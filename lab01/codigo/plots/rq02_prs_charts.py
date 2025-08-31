import os
import matplotlib.pyplot as plt

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ02PRsCharts:
    @staticmethod
    def generate(merged_prs, base_dir, top_n):
        median_prs = sorted(merged_prs)[len(merged_prs) // 2]

        # Histograma
        plt.figure(figsize=(8, 6))
        plt.hist(merged_prs, bins=20, color='lightgreen', edgecolor='black')
        plt.axvline(median_prs, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_prs:.0f}')
        plt.title(f'RQ02 - Distribuição de Pull Requests Aceitas (Histograma)\nMediana: {median_prs:.0f}')  # Adicionado ao título
        plt.xlabel('Número de Pull Requests')
        plt.ylabel('Frequência')
        plt.legend()
        hist_path = os.path.join(base_dir, f'rq02_prs_hist_{top_n}.png')
        BaseChart.save_chart(plt, hist_path)
        
        # Boxplot
        plt.figure(figsize=(8, 6))
        plt.boxplot(merged_prs, vert=False, patch_artist=True, showfliers=False)
        plt.title(f'RQ02 - Pull Requests Aceitas (Box Plot)\nMediana: {median_prs:.0f}') # Adicionado ao título
        plt.xlabel('Número de Pull Requests')
        box_path = os.path.join(base_dir, f'rq02_prs_box_{top_n}.png')
        BaseChart.save_chart(plt, box_path)
        hist_path =  f'./graficos/rq02_prs_hist_{top_n}.png'
        box_path =  f'./graficos/rq02_prs_box_{top_n}.png'

        return hist_path, box_path
