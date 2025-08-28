import os
import matplotlib.pyplot as plt

class RQ05LanguagesCharts:
    @staticmethod
    def generate(top_languages, base_dir):
        langs, counts = zip(*top_languages)

        # Barras
        plt.figure(figsize=(10, 6))
        plt.bar(langs, counts, color='skyblue')
        plt.title('RQ05 - Linguagens Mais Populares (Barras)')
        plt.xlabel('Linguagens')
        plt.ylabel('Número de Repositórios')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        bar_path = os.path.join(base_dir, 'rq05_linguagens_bar.png')
        plt.savefig(bar_path)
        plt.close()

        # Pizza
        plt.figure(figsize=(8, 6))
        plt.pie(counts, labels=langs, autopct='%1.1f%%', startangle=140)
        plt.title('RQ05 - Linguagens Mais Populares (Pizza)')
        plt.tight_layout()
        pie_path = os.path.join(base_dir, 'rq05_linguagens_pie.png')
        plt.savefig(pie_path)
        plt.close()

        return bar_path, pie_path
