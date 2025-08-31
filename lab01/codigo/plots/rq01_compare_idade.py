import matplotlib.pyplot as plt
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
        median_age_all = sorted(all_ages)[len(all_ages) // 2]
        median_age_top10 = sorted(top10_ages)[len(top10_ages) // 2]
        plt.figure(figsize=(8, 6))
        plt.hist(all_ages, bins=20, alpha=0.5, label='Todos os Repositórios', color='skyblue')
        plt.hist(top10_ages, bins=20, alpha=0.5, label='Top 10 Repositórios', color='lightcoral')
        plt.axvline(median_age_all, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_age_all:.0f}')
        plt.axvline(median_age_top10, color='red', linestyle='dashed', linewidth=1, label=f'Mediana: {median_age_top10:.0f}')
        
        
        plt.title('RQ01 - Comparação da Distribuição da Idade dos Repositórios')
        plt.xlabel('Idade (dias)')
        plt.ylabel('Frequência')
        plt.legend()
        plt.savefig(os.path.join(base_dir, 'rq01_comparacao_idade.png'))
        plt.close()
        compare_path =  f'./graficos/rq01_compare_idade.png'
        return compare_path