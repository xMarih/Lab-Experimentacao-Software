import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
import logging

"RQ01 – Qual a correlação entre a variação no número de jogadores e o sentimento médio das avaliações?"

# Diretórios
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, "resultados/dados_agregados")
OUTPUT_DIR = os.path.join(BASE_DIR, "resultados/rqs/rq01")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Logging
log_path = os.path.join(OUTPUT_DIR, "log_correlacao_players_sentiment.log")
logging.basicConfig(
    filename=log_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def calcular_correlacao_por_genero():
    resultados = []
    df_plot = pd.DataFrame()

    for file in os.listdir(INPUT_DIR):
        if not file.endswith(".csv") or not file.startswith("dados_agregados_"):
            continue

        genero = file.replace("dados_agregados_", "").replace(".csv", "")
        caminho = os.path.join(INPUT_DIR, file)

        try:
            df = pd.read_csv(caminho)
            df = df[["Players", "Sentiment"]].dropna()

            if len(df) < 5:
                logging.warning(f"[Ignorado] Gênero: {genero} - Menos de 5 registros válidos")
                continue

            correlacao, p_valor = spearmanr(df["Players"], df["Sentiment"])
            resultados.append({
                "genero": genero,
                "correlacao": correlacao,
                "p_valor": p_valor
            })

            df["genero"] = genero
            df_plot = pd.concat([df_plot, df], ignore_index=True)

            logging.info(f"[{genero}] Spearman: rho = {correlacao:.4f}, p = {p_valor:.4g}")

        except Exception as e:
            logging.error(f"[{genero}] Erro ao processar: {str(e)}")

    return df_plot, pd.DataFrame(resultados)

def plotar_boxplot(df_plot, df_corr):
    plt.figure(figsize=(12, 6))
    ax = sns.boxplot(data=df_plot, x="genero", y="Sentiment", hue="genero", palette="Set2", legend=False)
    plt.title("Distribuição do Sentimento Médio por Gênero (com correlação Spearman entre Players e Sentiment)")
    plt.ylabel("Sentimento Médio")
    plt.xlabel("Gênero")

    for i, genero in enumerate(df_corr["genero"]):
        rho = df_corr.loc[df_corr["genero"] == genero, "correlacao"].values[0]
        pval = df_corr.loc[df_corr["genero"] == genero, "p_valor"].values[0]
        y_max = df_plot[df_plot["genero"] == genero]["Sentiment"].max()
        texto = f"ρ = {rho:.2f}\np = {pval:.3f}"
        ax.text(i, y_max + y_max * 0.02, texto, ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    path_plot = os.path.join(OUTPUT_DIR, "boxplot_sentiment_genero.png")
    plt.savefig(path_plot)
    plt.close()
    logging.info(f"Gráfico salvo em: {path_plot}")

def salvar_csv_resultados(df_corr):
    caminho_csv = os.path.join(OUTPUT_DIR, "correlacao_players_sentiment.csv")
    df_corr.to_csv(caminho_csv, index=False)
    logging.info(f"Resumo salvo em: {caminho_csv}")

def main():
    df_plot, df_corr = calcular_correlacao_por_genero()
    if not df_plot.empty:
        plotar_boxplot(df_plot, df_corr)
        salvar_csv_resultados(df_corr)
    else:
        logging.warning("Nenhum dado válido encontrado para plotagem ou correlação.")

if __name__ == "__main__":
    main()