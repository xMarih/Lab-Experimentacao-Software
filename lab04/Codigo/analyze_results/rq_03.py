import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import numpy as np
from scipy.stats import mannwhitneyu

"RQ03 – Qual a diferença na quantidade de reviews entre releases positivas e negativas por gênero?"

# Diretórios
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, "resultados/classificacao_release")
GRAFICOS_DIR = os.path.join(BASE_DIR, "resultados/rqs/rq03")
os.makedirs(GRAFICOS_DIR, exist_ok=True)

# Configuração do logger
log_path = os.path.join(GRAFICOS_DIR, "log_facet_mannwhitney.log")
logging.basicConfig(
    filename=log_path,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def ler_tabela_tabulate(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = f.readlines()
    conteudo_tabela = [linha for linha in linhas if linha.startswith("|")]
    colunas = [col.strip() for col in conteudo_tabela[0].strip().split("|")[1:-1]]
    dados = []
    for linha in conteudo_tabela[2:]:
        valores = [val.strip() for val in linha.strip().split("|")[1:-1]]
        if len(valores) == len(colunas):
            dados.append(valores)
    return pd.DataFrame(dados, columns=colunas)

def preparar_dados():
    df_consolidado = []
    resultados = []

    for arquivo in os.listdir(INPUT_DIR):
        if arquivo.startswith("sentiment_releases_") and arquivo.endswith(".txt"):
            genero = arquivo.replace("sentiment_releases_", "").replace(".txt", "")
            caminho = os.path.join(INPUT_DIR, arquivo)

            try:
                df = ler_tabela_tabulate(caminho)
                df = df[df["label"].isin(["positive", "negative"])]
                df["review_count_total"] = pd.to_numeric(df["review_count_total"], errors="coerce")
                df["genero"] = genero
                df["label"] = df["label"].str.capitalize()
                df = df.dropna(subset=["review_count_total"])

                if df["label"].nunique() == 2:
                    grupo_pos = df[df["label"] == "Positive"]["review_count_total"]
                    grupo_neg = df[df["label"] == "Negative"]["review_count_total"]
                    stat, p_val = mannwhitneyu(grupo_pos, grupo_neg, alternative='two-sided')
                    resultados.append({"genero": genero, "p_valor": p_val})
                    df_consolidado.append(df)
                else:
                    logging.warning(f"[{genero}] Apenas uma classe presente, teste não aplicado.")

            except Exception as e:
                logging.error(f"Erro ao processar {arquivo}: {str(e)}")

    df_all = pd.concat(df_consolidado, ignore_index=True)
    df_stats = pd.DataFrame(resultados)
    return df_all, df_stats

def gerar_facetplot(df_all, df_stats):
    sns.set(style="whitegrid")
    g = sns.catplot(
        data=df_all,
        kind="bar",
        x="label",
        y="review_count_total",
        hue="label",  # Adicionado para eliminar o aviso
        col="genero",
        estimator=np.median,
        palette={"Positive": "#1f77b4", "Negative": "#d62728"},
        col_wrap=3,
        height=4,
        aspect=1,
        legend=False  # Oculta legenda duplicada
    )

    # Títulos com p-valor
    for ax, genero in zip(g.axes.flat, df_stats["genero"]):
        p = df_stats.loc[df_stats["genero"] == genero, "p_valor"].values[0]
        ax.set_title(f"{genero} (p = {p:.3f})")

    g.set_axis_labels("Classificação", "Mediana de Reviews")
    g.fig.subplots_adjust(top=0.9)
    g.fig.suptitle("Mediana de Reviews por Gênero e Classificação (Teste de Mann-Whitney)", fontsize=14)

    path = os.path.join(GRAFICOS_DIR, "facet_barplot_mannwhitney_por_genero.png")
    g.savefig(path)
    plt.close()
    logging.info(f"Gráfico salvo: {path}")

def main():
    df_all, df_stats = preparar_dados()
    if not df_all.empty:
        gerar_facetplot(df_all, df_stats)
    else:
        logging.warning("Nenhum dado válido encontrado para gerar o gráfico.")

if __name__ == "__main__":
    main()