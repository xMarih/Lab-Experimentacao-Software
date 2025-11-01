import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from scipy.stats import chi2_contingency

# Diretórios e configuração de logger
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, "resultados/classificacao_release")
GRAFICOS_DIR = os.path.join(BASE_DIR, "resultados/rqs/rq02")
os.makedirs(GRAFICOS_DIR, exist_ok=True)

log_path = os.path.join(GRAFICOS_DIR, "log_percentual_por_genero.log")
logging.basicConfig(
    filename=log_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def ler_tabela_tabulate(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    conteudo_tabela = [linha for linha in linhas if linha.startswith("|")]
    if not conteudo_tabela:
        raise ValueError("Tabela vazia ou mal formatada.")

    colunas = [col.strip() for col in conteudo_tabela[0].strip().split("|")[1:-1]]
    dados = []
    for linha in conteudo_tabela[2:]:
        valores = [val.strip() for val in linha.strip().split("|")[1:-1]]
        if len(valores) == len(colunas):
            dados.append(valores)

    return pd.DataFrame(dados, columns=colunas)

def calcular_percentuais(df, genero):
    df["label"] = df["label"].str.strip()
    total = len(df[df["label"].isin(["positive", "negative"])])
    if total == 0:
        return 0.0, 0.0
    positivas = len(df[df["label"] == "positive"])
    negativas = len(df[df["label"] == "negative"])
    perc_pos = round(100 * positivas / total, 2)
    perc_neg = round(100 * negativas / total, 2)
    logging.info(f"Gênero: {genero} | Total classificadas: {total} | Positivas: {positivas} ({perc_pos}%) | Negativas: {negativas} ({perc_neg}%)")
    return perc_pos, perc_neg

def gerar_grafico_barras(dados, matriz_qui2):
    sns.set(style="whitegrid")
    generos = list(dados.keys())
    df_plot = pd.DataFrame([
        {"Gênero": g, "Classificação": "Positivas", "Percentual": dados[g]["positive"]} for g in generos
    ] + [
        {"Gênero": g, "Classificação": "Negativas", "Percentual": dados[g]["negative"]} for g in generos
    ])

    # Cálculo do Qui-Quadrado
    chi2, p, _, _ = chi2_contingency(matriz_qui2)
    chi2_text = f"Qui² = {chi2:.2f}, p = {p:.3f}"

    plt.figure(figsize=(14, 6))
    cores = {"Positivas": "#1f4eb4", "Negativas": "#d62728"}
    ax = sns.barplot(data=df_plot, x="Gênero", y="Percentual", hue="Classificação", palette=cores)
    plt.title("Percentual de Releases Positivas e Negativas por Gênero", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    plt.text(0.01, 1.02, chi2_text, transform=ax.transAxes, fontsize=12, color='black')
    plt.tight_layout()

    grafico_path = os.path.join(GRAFICOS_DIR, "percentual_releases_por_genero_moderno.png")
    plt.savefig(grafico_path)
    plt.close()
    logging.info(f"Gráfico moderno salvo em: {grafico_path}")

def main():
    dados_percentuais = {}
    matriz_qui2 = []

    for arquivo in os.listdir(INPUT_DIR):
        if arquivo.startswith("sentiment_releases_") and arquivo.endswith(".txt"):
            genero = arquivo.replace("sentiment_releases_", "").replace(".txt", "")
            caminho = os.path.join(INPUT_DIR, arquivo)

            try:
                df = ler_tabela_tabulate(caminho)
                df["label"] = df["label"].str.strip()
                positivas = len(df[df["label"] == "positive"])
                negativas = len(df[df["label"] == "negative"])
                matriz_qui2.append([positivas, negativas])
                perc_pos, perc_neg = calcular_percentuais(df, genero)
                dados_percentuais[genero] = {"positive": perc_pos, "negative": perc_neg}
            except Exception as e:
                logging.error(f"Erro ao processar {arquivo}: {str(e)}")

    if dados_percentuais and matriz_qui2:
        gerar_grafico_barras(dados_percentuais, matriz_qui2)
    else:
        logging.info("Nenhum dado disponível para gerar o gráfico.")

if __name__ == "__main__":
    main()