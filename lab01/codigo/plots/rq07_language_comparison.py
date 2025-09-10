import os
import matplotlib.pyplot as plt

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ07LanguageComparisonCharts:
    @staticmethod
    def generate(popular_stats, other_stats, base_dir):
        """
        Gera gráficos comparando linguagens populares com outras linguagens (RQ07).
        """
        # Preparar dados para o gráfico de barras
        metrics = ['Mediana PRs Aceitas', 'Mediana Releases', 'Mediana Dias Update']
        popular_values = [popular_stats['median_prs'], popular_stats['median_releases'], popular_stats['median_days_update']]
        other_values = [other_stats['median_prs'], other_stats['median_releases'], other_stats['median_days_update']]

        x = range(len(metrics))  # Localização das barras
        width = 0.35  # Largura das barras

        # Criar gráfico de barras
        plt.figure(figsize=(10, 6))
        plt.bar([i - width/2 for i in x], popular_values, width, label='Populares', color='skyblue')
        plt.bar([i + width/2 for i in x], other_values, width, label='Outras', color='lightcoral')

        # Adicionar rótulos e título
        plt.xlabel('Métricas')
        plt.ylabel('Valores')
        plt.title('RQ07 - Comparação entre Linguagens Populares e Outras')
        plt.xticks(x, metrics)
        plt.legend()

        # Salvar gráfico de barras
        bar_path = os.path.join(base_dir, 'rq07_comparacao_bar.png')
        BaseChart.save_chart(plt, bar_path)

        bar_path =  './graficos/rq07_comparacao_bar.png'
        return bar_path