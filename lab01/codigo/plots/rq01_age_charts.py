import os
import matplotlib.pyplot as plt

class RQ01AgeCharts:
    @staticmethod
    def generate(ages, base_dir):
        median_age = sorted(ages)[len(ages) // 2]

        # Histograma
        plt.figure(figsize=(8, 6))
        plt.hist(ages, bins=20, color='skyblue', edgecolor='black')
        plt.axvline(median_age, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_age:.0f}')
        plt.title('RQ01 - Distribuição da Idade dos Repositórios (Histograma)')
        plt.xlabel('Idade (dias)')
        plt.ylabel('Frequência')
        plt.legend()
        hist_path = os.path.join(base_dir, 'rq01_idade_hist.png')
        plt.savefig(hist_path)
        plt.close()

        # Boxplot
        plt.figure(figsize=(8, 6))
        plt.boxplot(ages, vert=False, patch_artist=True, showfliers=False)
        plt.title('RQ01 - Idade dos Repositórios (Box Plot)')
        plt.xlabel('Idade (dias)')
        box_path = os.path.join(base_dir, 'rq01_idade_box.png')
        plt.savefig(box_path)
        plt.close()

        return hist_path, box_path
