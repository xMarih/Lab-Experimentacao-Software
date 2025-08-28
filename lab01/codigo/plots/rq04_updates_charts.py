import os
import matplotlib.pyplot as plt

class RQ04UpdatesCharts:
    @staticmethod
    def generate(days_since_updates, base_dir):
        median_days = sorted(days_since_updates)[len(days_since_updates) // 2]

        # Histograma
        plt.figure(figsize=(8, 6))
        plt.hist(days_since_updates, bins=20, color='lightyellow', edgecolor='black')
        plt.axvline(median_days, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_days:.0f}')
        plt.title('RQ04 - Distribuição de Dias Desde a Última Atualização (Histograma)')
        plt.xlabel('Dias Desde a Última Atualização')
        plt.ylabel('Frequência')
        plt.legend()
        hist_path = os.path.join(base_dir, 'rq04_dias_hist.png')
        plt.savefig(hist_path)
        plt.close()

        # Boxplot
        plt.figure(figsize=(8, 6))
        plt.boxplot(days_since_updates, vert=False, patch_artist=True, showfliers=False)
        plt.title('RQ04 - Dias Desde a Última Atualização (Box Plot)')
        plt.xlabel('Dias Desde a Última Atualização')
        box_path = os.path.join(base_dir, 'rq04_dias_box.png')
        plt.savefig(box_path)
        plt.close()

        return hist_path, box_path
