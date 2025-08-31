import matplotlib.pyplot as plt
import os

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ04CompareUpdatesCharts:
    @staticmethod
    def generate(all_updates, top10_updates, base_dir):
        """
        Gera um boxplot comparando os dias desde a última atualização entre todos os repositórios e os top 10.
        """
        plt.figure(figsize=(8, 6))

        # Cria o boxplot
        plt.boxplot([all_updates, top10_updates], labels=['Todos os Repositórios', 'Top 10 Repositórios'], patch_artist=True)

        # Configurações do gráfico
        plt.title('RQ04 - Comparação dos Dias Desde a Última Atualização (Boxplot)')
        plt.ylabel('Dias Desde a Última Atualização')

        # Salva o gráfico
        compare_path = os.path.join(base_dir, 'rq04_comparacao_updates_boxplot.png')
        BaseChart.save_chart(plt, compare_path)
        compare_path =  f'./graficos/rq04_comparacao_updates_boxplot.png'
        return compare_path