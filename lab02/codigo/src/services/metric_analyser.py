import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Carrega o CSV
df = pd.read_csv(
    'lab02/codigo/src/services/ck_metrics/all_metrics_20250918_033515.csv'
)

# Diretório para salvar os gráficos
output_dir = 'lab02/relatorios/graficos'

os.makedirs(output_dir, exist_ok=True)

quality_metrics = [
    'quality_cbo_mean', 'quality_dit_mean', 'quality_lcom_mean'
]
process_metrics = {
    'Popularidade (stars)': 'popularity_stars',
    'Maturidade (anos)': 'maturity_years',
    'Atividade (releases)': 'activity_releases',
    'Tamanho (LOC)': 'size_loc',
    'Tamanho (comentários)': 'size_comments_loc'
}

def plot_relation(x_metric, y_metric, xlabel, ylabel, title, filename):
    plt.figure(figsize=(7, 5))
    sns.scatterplot(data=df, x=x_metric, y=y_metric)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.close()

def correlation_report(x_metric, y_metric):
    corr = df[x_metric].corr(df[y_metric])
    return corr

# RQ01: Popularidade vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Popularidade (stars)'], qm,
        'Popularidade (stars)', qm,
        f'Popularidade vs {qm}',
        f'popularidade_vs_{qm}.png'
    )
    print(f"Correlação entre Popularidade e {qm}: {correlation_report(process_metrics['Popularidade (stars)'], qm):.3f}")

# RQ02: Maturidade vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Maturidade (anos)'], qm,
        'Maturidade (anos)', qm,
        f'Maturidade vs {qm}',
        f'maturidade_vs_{qm}.png'
    )
    print(f"Correlação entre Maturidade e {qm}: {correlation_report(process_metrics['Maturidade (anos)'], qm):.3f}")

# RQ03: Atividade vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Atividade (releases)'], qm,
        'Atividade (releases)', qm,
        f'Atividade vs {qm}',
        f'atividade_vs_{qm}.png'
    )
    print(f"Correlação entre Atividade e {qm}: {correlation_report(process_metrics['Atividade (releases)'], qm):.3f}")

# RQ04: Tamanho vs Qualidade
for qm in quality_metrics:
    plot_relation(
        process_metrics['Tamanho (LOC)'], qm,
        'Tamanho (LOC)', qm,
        f'Tamanho LOC vs {qm}',
        f'tamanho_loc_vs_{qm}.png'
    )
    print(f"Correlação entre Tamanho LOC e {qm}: {correlation_report(process_metrics['Tamanho (LOC)'], qm):.3f}")

    plot_relation(
        process_metrics['Tamanho (comentários)'], qm,
        'Tamanho (comentários)', qm,
        f'Tamanho Comentários vs {qm}',
        f'tamanho_comentarios_vs_{qm}.png'
    )
    print(f"Correlação entre Tamanho Comentários e {qm}: {correlation_report(process_metrics['Tamanho (comentários)'], qm):.3f}")

