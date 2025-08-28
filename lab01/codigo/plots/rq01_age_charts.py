import os
import matplotlib.pyplot as plt

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ01AgeCharts:
    @staticmethod
    def generate(ages, base_dir):
        print("RQ01AgeCharts.generate foi chamado")
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
        print(f"Salvando histograma em: {hist_path}")
        BaseChart.save_chart(plt, hist_path)

        # Boxplot
        plt.figure(figsize=(8, 6))
        plt.boxplot(ages, vert=False, patch_artist=True, showfliers=False)
        plt.title('RQ01 - Idade dos Repositórios (Box Plot)')
        plt.xlabel('Idade (dias)')
        plt.ylabel(' ')
        box_path = os.path.join(base_dir, 'rq01_idade_box.png')
        print(f"Salvando boxplot em: {box_path}")
        BaseChart.save_chart(plt, box_path)

        return hist_path, box_path
