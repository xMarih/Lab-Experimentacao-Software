import os
import matplotlib.pyplot as plt

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ05LanguagesCharts:
    @staticmethod
    def generate(top_languages, base_dir, top_n):
        langs, counts = zip(*top_languages)

        # Barras
        plt.figure(figsize=(10, 6))
        plt.bar(langs, counts, color='skyblue')
        plt.title('RQ05 - Linguagens Mais Populares')
        plt.xlabel('Linguagens')
        plt.ylabel('Número de Repositórios')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        bar_path = os.path.join(base_dir, f'rq05_linguagens_bar_{top_n}.png')
        BaseChart.save_chart(plt, bar_path)

        # Pizza
        plt.figure(figsize=(8, 6))
        plt.pie(counts, labels=langs, autopct='%1.1f%%', startangle=140)
        plt.title('RQ05 - Linguagens Mais Populares')
        plt.tight_layout()
        pie_path = os.path.join(base_dir, f'rq05_linguagens_pie_{top_n}.png')
        BaseChart.save_chart(plt, pie_path)
        bar_path =  f'./graficos/rq05_linguagens_bar_{top_n}.png'
        pie_path =  f'./graficos/rq05_linguagens_pie_{top_n}.png'

        return bar_path, pie_path
