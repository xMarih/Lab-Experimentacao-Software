import os
import matplotlib.pyplot as plt

class RQ03ReleasesCharts:
    @staticmethod
    def generate(releases, base_dir):
        median_releases = sorted(releases)[len(releases) // 2]

        # Histograma
        plt.figure(figsize=(8, 6))
        plt.hist(releases, bins=20, color='lightcoral', edgecolor='black')
        plt.axvline(median_releases, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_releases:.0f}')
        plt.title('RQ03 - Distribuição de Releases (Histograma)')
        plt.xlabel('Número de Releases')
        plt.ylabel('Frequência')
        plt.legend()
        hist_path = os.path.join(base_dir, 'rq03_releases_hist.png')
        plt.savefig(hist_path)
        plt.close()

        # Boxplot
        plt.figure(figsize=(8, 6))
        plt.boxplot(releases, vert=False, patch_artist=True, showfliers=False)
        plt.title('RQ03 - Releases (Box Plot)')
        plt.xlabel('Número de Releases')
        box_path = os.path.join(base_dir, 'rq03_releases_box.png')
        plt.savefig(box_path)
        plt.close()

        return hist_path, box_path
