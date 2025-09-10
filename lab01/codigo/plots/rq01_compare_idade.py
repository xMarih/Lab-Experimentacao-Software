import matplotlib.pyplot as plt
import matplotlib.pyplot as np
import os

class BaseChart:
    @staticmethod
    def save_chart(plt, filename):
        """Salva o gráfico em um arquivo."""
        plt.savefig(filename)
        plt.close()

class RQ01CompareAgeCharts:
    @staticmethod
    def generate(all_ages, top10_ages, base_dir):
        """
        Gera um boxplot comparando a idade de todos os repositórios com os top 10.
        """
        plt.figure(figsize=(8, 6))

        # Calcula as medianas
        median_age_all = sorted(all_ages)[len(all_ages) // 2]
        median_age_top10 = sorted(top10_ages)[len(top10_ages) // 2]

        # Calcula o desvio padrão
        std_age_all = np.std(all_ages)
        std_age_top10 = np.std(top10_ages)

        # Cria o boxplot
        plt.boxplot([all_ages, top10_ages], labels=['Todos os Repositórios', 'Top 10 Repositórios'], patch_artist=True)

        # Configurações do gráfico
        plt.title(
            f'RQ01 - Comparação da Idade dos Repositórios\n'
            f'Mediana (Todos): {median_age_all:.0f} dias, Desvio Padrão: {std_age_all:.0f}\n'
            f'Mediana (Top 10): {median_age_top10:.0f} dias, Desvio Padrão: {std_age_top10:.0f}'
        )
        plt.ylabel('Idade (dias)')

        # Salva o gráfico
        compare_path = os.path.join(base_dir, 'rq01_comparacao_idade.png')
        BaseChart.save_chart(plt, compare_path)

        compare_path =  f'./graficos/rq01_comparacao_idade.png'
        return compare_path