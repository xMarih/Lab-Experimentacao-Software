import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, spearmanr, pearsonr, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')
import os

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class PRDataAnalyzer:
    def __init__(self, repos_file, prs_file):
        self.repos_df = pd.read_csv(repos_file)
        self.prs_df = pd.read_csv(prs_file)
        self.results = {}
        self.normality_results = {}
        
    def prepare_data(self):
        print("📊 Preparando dados para análise...")
        
        self.prs_df['diff_size'] = self.prs_df['additions'] + self.prs_df['deletions']
        self.prs_df['body_length_chars'] = self.prs_df['body'].fillna('').str.len()
        self.prs_df['total_comments'] = self.prs_df['comments'] + self.prs_df['review_comments']
        
        self.prs_df = self.prs_df[self.prs_df['state'].isin(['MERGED', 'CLOSED'])]
        
        self.prs_df['merged_bool'] = self.prs_df['merged'] == True
        
        numeric_cols = ['diff_size', 'files_changed', 'time_to_close_hours', 
                       'body_length_chars', 'participant_count', 'total_comments', 'review_count']
        
        for col in numeric_cols:
            if col in self.prs_df.columns:
                q99 = self.prs_df[col].quantile(0.99)
                self.prs_df = self.prs_df[self.prs_df[col] <= q99]
        
        print(f"✅ Dados preparados: {len(self.prs_df)} PRs válidos")
        
    def test_normality_comprehensive(self):
        print("\n" + "="*60)
        print("📈 ANÁLISE DE NORMALIDADE DOS DADOS")
        print("="*60)
        
        numeric_vars = ['diff_size', 'files_changed', 'time_to_close_hours', 
                       'body_length_chars', 'participant_count', 'total_comments', 'review_count']
        
        normality_table = []
        
        for var in numeric_vars:
            if var in self.prs_df.columns:
                data = self.prs_df[var].dropna()
                
                if len(data) > 5000:
                    data_sample = data.sample(5000, random_state=42)
                else:
                    data_sample = data
                
                shapiro_stat, shapiro_p = shapiro(data_sample)
                
                skewness = stats.skew(data)
                kurtosis = stats.kurtosis(data)
                
                is_normal = shapiro_p > 0.05
                normality_class = "Normal" if is_normal else "Não-Normal"
                
                normality_table.append({
                    'Variável': var,
                    'n': len(data),
                    'Média': data.mean(),
                    'Mediana': data.median(),
                    'Desvio Padrão': data.std(),
                    'Assimetria (Skewness)': f"{skewness:.4f}",
                    'Curtose (Kurtosis)': f"{kurtosis:.4f}",
                    'Shapiro-Wilk p-value': f"{shapiro_p:.6f}",
                    'Normalidade': normality_class
                })
                
                self.normality_results[var] = {
                    'is_normal': is_normal,
                    'shapiro_p': shapiro_p,
                    'skewness': skewness,
                    'kurtosis': kurtosis
                }
        
        normality_df = pd.DataFrame(normality_table)
        print("\n📋 RESUMO DA ANÁLISE DE NORMALIDADE:")
        print(normality_df.to_string(index=False))
        
        normality_df.to_csv('results/normality_analysis.csv', index=False)
        print(f"\n💾 Tabela de normalidade salva em: results/normality_analysis.csv")
        
        return normality_df
    
    def plot_normality_analysis(self):
        print("\n📊 Gerando visualizações de normalidade...")
        
        numeric_vars = ['diff_size', 'files_changed', 'time_to_close_hours', 
                       'body_length_chars', 'participant_count', 'total_comments', 'review_count']
        
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        axes = axes.ravel()
        
        for i, var in enumerate(numeric_vars):
            if i < len(axes) and var in self.prs_df.columns:
                data = self.prs_df[var].dropna()
                
                ax = axes[i]
                n, bins, patches = ax.hist(data, bins=30, alpha=0.7, density=True, color='skyblue')
                
                xmin, xmax = ax.get_xlim()
                x = np.linspace(xmin, xmax, 100)
                p = stats.norm.pdf(x, data.mean(), data.std())
                ax.plot(x, p, 'k', linewidth=2, label='Distribuição Normal')
                
                ax.set_title(f'Distribuição de {var}\n(p-value: {self.normality_results[var]["shapiro_p"]:.4f})')
                ax.set_xlabel(var)
                ax.set_ylabel('Densidade')
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        for i in range(len(numeric_vars), len(axes)):
            fig.delaxes(axes[i])
        
        plt.tight_layout()
        plt.savefig('plots/normality_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        axes = axes.ravel()
        
        for i, var in enumerate(numeric_vars):
            if i < len(axes) and var in self.prs_df.columns:
                data = self.prs_df[var].dropna()
                
                stats.probplot(data, dist="norm", plot=axes[i])
                axes[i].set_title(f'Q-Q Plot: {var}')
                axes[i].grid(True, alpha=0.3)
        
        for i in range(len(numeric_vars), len(axes)):
            fig.delaxes(axes[i])
        
        plt.tight_layout()
        plt.savefig('plots/qq_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Visualizações de normalidade salvas em: plots/normality_analysis.png e plots/qq_plots.png")
    
    def calculate_correlation(self, x, y):
        x_normal = self.normality_results.get(x, {}).get('is_normal', False)
        y_normal = self.normality_results.get(y, {}).get('is_normal', False)
        
        if x_normal and y_normal:
            method = 'pearson'
            corr, p_value = pearsonr(self.prs_df[x].dropna(), self.prs_df[y].dropna())
        else:
            method = 'spearman'
            corr, p_value = spearmanr(self.prs_df[x].dropna(), self.prs_df[y].dropna())
        
        return corr, p_value, method
    
    def analyze_all_rqs(self):
        print("\n" + "="*60)
        print("🔬 ANÁLISE DAS RESEARCH QUESTIONS")
        print("="*60)
        
        self.analyze_rq01()
        
        self.analyze_rq02()
        
        self.analyze_rq03()
        
        self.analyze_rq04()
        
        self.analyze_rq05()
        
        self.analyze_rq06()
        
        self.analyze_rq07()
        
        self.analyze_rq08()
    
    def analyze_rq01(self):
        print("\n📏 RQ01: Tamanho dos PRs vs Feedback Final")
        
        merged = self.prs_df[self.prs_df['merged_bool'] == True]
        closed = self.prs_df[self.prs_df['merged_bool'] == False]
        
        corr, p_value, method = self.calculate_correlation('diff_size', 'merged_bool')
        
        stat, p_mw = mannwhitneyu(merged['diff_size'], closed['diff_size'])
        
        self.results['RQ01'] = {
            'merged_median_size': merged['diff_size'].median(),
            'closed_median_size': closed['diff_size'].median(),
            'correlation': corr,
            'p_value': p_value,
            'method': method,
            'mann_whitney_p': p_mw,
            'effect_size': (merged['diff_size'].median() - closed['diff_size'].median()) / self.prs_df['diff_size'].std()
        }
        
        print(f"   📊 Mediana tamanho (merged): {merged['diff_size'].median():.2f}")
        print(f"   📊 Mediana tamanho (closed): {closed['diff_size'].median():.2f}")
        print(f"   📈 Correlação ({method}): {corr:.4f} (p-value: {p_value:.6f})")
        print(f"   🎯 Mann-Whitney U: p-value = {p_mw:.6f}")
    
    def analyze_rq02(self):
        print("\n⏱️  RQ02: Tempo de Análise vs Feedback Final")
        
        merged = self.prs_df[self.prs_df['merged_bool'] == True]
        closed = self.prs_df[self.prs_df['merged_bool'] == False]
        
        corr, p_value, method = self.calculate_correlation('time_to_close_hours', 'merged_bool')
        
        self.results['RQ02'] = {
            'merged_median_time': merged['time_to_close_hours'].median(),
            'closed_median_time': closed['time_to_close_hours'].median(),
            'correlation': corr,
            'p_value': p_value,
            'method': method
        }
        
        print(f"   📊 Mediana tempo (merged): {merged['time_to_close_hours'].median():.2f} horas")
        print(f"   📊 Mediana tempo (closed): {closed['time_to_close_hours'].median():.2f} horas")
        print(f"   📈 Correlação ({method}): {corr:.4f} (p-value: {p_value:.6f})")
    
    def analyze_rq03(self):
        print("\n📝 RQ03: Descrição dos PRs vs Feedback Final")
        
        merged = self.prs_df[self.prs_df['merged_bool'] == True]
        closed = self.prs_df[self.prs_df['merged_bool'] == False]
        
        corr, p_value, method = self.calculate_correlation('body_length_chars', 'merged_bool')
        
        self.results['RQ03'] = {
            'merged_median_desc': merged['body_length_chars'].median(),
            'closed_median_desc': closed['body_length_chars'].median(),
            'correlation': corr,
            'p_value': p_value,
            'method': method
        }
        
        print(f"   📊 Mediana descrição (merged): {merged['body_length_chars'].median():.2f} chars")
        print(f"   📊 Mediana descrição (closed): {closed['body_length_chars'].median():.2f} chars")
        print(f"   📈 Correlação ({method}): {corr:.4f} (p-value: {p_value:.6f})")
    
    def analyze_rq04(self):
        print("\n💬 RQ04: Interações nos PRs vs Feedback Final")
        
        metrics = ['participant_count', 'total_comments', 'review_count']
        
        for metric in metrics:
            if metric in self.prs_df.columns:
                corr, p_value, method = self.calculate_correlation(metric, 'merged_bool')
                self.results[f'RQ04_{metric}'] = {
                    'correlation': corr,
                    'p_value': p_value,
                    'method': method
                }
                print(f"   📈 {metric}: {corr:.4f} (p-value: {p_value:.6f})")
    
    def analyze_rq05(self):
        print("\n📏 RQ05: Tamanho dos PRs vs Número de Revisões")
        
        corr, p_value, method = self.calculate_correlation('diff_size', 'review_count')
        
        self.results['RQ05'] = {
            'correlation': corr,
            'p_value': p_value,
            'method': method
        }
        
        print(f"   📈 Correlação ({method}): {corr:.4f} (p-value: {p_value:.6f})")
    
    def analyze_rq06(self):
        print("\n⏱️  RQ06: Tempo de Análise vs Número de Revisões")
        
        corr, p_value, method = self.calculate_correlation('time_to_close_hours', 'review_count')
        
        self.results['RQ06'] = {
            'correlation': corr,
            'p_value': p_value,
            'method': method
        }
        
        print(f"   📈 Correlação ({method}): {corr:.4f} (p-value: {p_value:.6f})")
    
    def analyze_rq07(self):
        print("\n📝 RQ07: Descrição dos PRs vs Número de Revisões")
        
        corr, p_value, method = self.calculate_correlation('body_length_chars', 'review_count')
        
        self.results['RQ07'] = {
            'correlation': corr,
            'p_value': p_value,
            'method': method
        }
        
        print(f"   📈 Correlação ({method}): {corr:.4f} (p-value: {p_value:.6f})")
    
    def analyze_rq08(self):
        print("\n💬 RQ08: Interações nos PRs vs Número de Revisões")
        
        metrics = ['participant_count', 'total_comments']
        
        for metric in metrics:
            if metric in self.prs_df.columns:
                corr, p_value, method = self.calculate_correlation(metric, 'review_count')
                self.results[f'RQ08_{metric}'] = {
                    'correlation': corr,
                    'p_value': p_value,
                    'method': method
                }
                print(f"   📈 {metric}: {corr:.4f} (p-value: {p_value:.6f})")
    
    def generate_summary_tables(self):
        print("\n" + "="*60)
        print("📋 GERANDO TABELAS SUMARIZADAS")
        print("="*60)
        
        numeric_vars = ['diff_size', 'files_changed', 'time_to_close_hours', 
                       'body_length_chars', 'participant_count', 'total_comments', 'review_count']
        
        desc_stats = []
        for var in numeric_vars:
            if var in self.prs_df.columns:
                data = self.prs_df[var].dropna()
                desc_stats.append({
                    'Variável': var,
                    'n': len(data),
                    'Média': f"{data.mean():.2f}",
                    'Mediana': f"{data.median():.2f}",
                    'Desvio Padrão': f"{data.std():.2f}",
                    'Mínimo': f"{data.min():.2f}",
                    'Máximo': f"{data.max():.2f}"
                })
        
        desc_df = pd.DataFrame(desc_stats)
        desc_df.to_csv('results/descriptive_statistics.csv', index=False)
        print("✅ Tabela de estatísticas descritivas salva")
        
        merged = self.prs_df[self.prs_df['merged_bool'] == True]
        closed = self.prs_df[self.prs_df['merged_bool'] == False]
        
        comparison_stats = []
        for var in numeric_vars:
            if var in self.prs_df.columns:
                comparison_stats.append({
                    'Variável': var,
                    'Merged_Mediana': f"{merged[var].median():.2f}",
                    'Closed_Mediana': f"{closed[var].median():.2f}",
                    'Merged_Média': f"{merged[var].mean():.2f}",
                    'Closed_Média': f"{closed[var].mean():.2f}",
                    'Diferença_Medianas': f"{(merged[var].median() - closed[var].median()):.2f}"
                })
        
        comp_df = pd.DataFrame(comparison_stats)
        comp_df.to_csv('results/merged_vs_closed_comparison.csv', index=False)
        print("✅ Tabela de comparação Merged vs Closed salva")
        
        corr_results = []
        for rq, result in self.results.items():
            if 'correlation' in result:
                corr_results.append({
                    'Research Question': rq,
                    'Correlação': f"{result['correlation']:.4f}",
                    'p-value': f"{result['p_value']:.6f}",
                    'Método': result['method'],
                    'Significância': '***' if result['p_value'] < 0.001 else '**' if result['p_value'] < 0.01 else '*' if result['p_value'] < 0.05 else 'ns'
                })
        
        corr_df = pd.DataFrame(corr_results)
        corr_df.to_csv('results/correlation_results.csv', index=False)
        print("✅ Tabela de resultados de correlação salva")
        
        return desc_df, comp_df, corr_df
    
    def create_visualizations(self):
        print("\n" + "="*60)
        print("🎨 CRIANDO VISUALIZAÇÕES")
        print("="*60)
        
        os.makedirs('plots', exist_ok=True)
        
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='merged_bool', y='diff_size', data=self.prs_df)
        plt.title('RQ01: Tamanho do PR vs Status (Merged/Closed)')
        plt.xlabel('Status (False=Closed, True=Merged)')
        plt.ylabel('Tamanho do PR (adições + deleções)')
        plt.savefig('plots/rq01_size_vs_status.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='merged_bool', y='time_to_close_hours', data=self.prs_df)
        plt.title('RQ02: Tempo de Análise vs Status (Merged/Closed)')
        plt.xlabel('Status (False=Closed, True=Merged)')
        plt.ylabel('Tempo para fechamento (horas)')
        plt.savefig('plots/rq02_time_vs_status.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        plt.figure(figsize=(10, 6))
        plt.scatter(self.prs_df['diff_size'], self.prs_df['review_count'], alpha=0.5)
        plt.title('RQ05: Tamanho do PR vs Número de Revisões')
        plt.xlabel('Tamanho do PR (adições + deleções)')
        plt.ylabel('Número de Revisões')
        plt.savefig('plots/rq05_size_vs_reviews.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✅ Visualizações salvas na pasta 'plots/'")
    
    def run_complete_analysis(self):
        print("🚀 INICIANDO ANÁLISE COMPLETA DOS DADOS")
        print("="*60)
        
        os.makedirs('results', exist_ok=True)
        os.makedirs('plots', exist_ok=True)
        
        self.prepare_data()
        
        normality_df = self.test_normality_comprehensive()
        self.plot_normality_analysis()
        
        self.analyze_all_rqs()

        desc_df, comp_df, corr_df = self.generate_summary_tables()
        self.create_visualizations()
        
        print("\n" + "="*60)
        print("🎉 ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print("📁 Arquivos gerados:")
        print("   📊 results/normality_analysis.csv")
        print("   📊 results/descriptive_statistics.csv")
        print("   📊 results/merged_vs_closed_comparison.csv")
        print("   📊 results/correlation_results.csv")
        print("   🎨 plots/normality_analysis.png")
        print("   🎨 plots/qq_plots.png")
        print("   🎨 plots/rq01_size_vs_status.png")
        print("   🎨 plots/rq02_time_vs_status.png")
        print("   🎨 plots/rq05_size_vs_reviews.png")
        print("="*60)

if __name__ == "__main__":
    REPOS_FILE = "data/cloned_repos.csv"
    PRS_FILE = "data/collected_prs_details.csv"
    
    if not os.path.exists(REPOS_FILE) or not os.path.exists(PRS_FILE):
        print("❌ ERRO: Arquivos de dados não encontrados!")
        print("   Certifique-se de que os arquivos existem:")
        print(f"   - {REPOS_FILE}")
        print(f"   - {PRS_FILE}")
        exit(1)
    
    analyzer = PRDataAnalyzer(REPOS_FILE, PRS_FILE)
    analyzer.run_complete_analysis()