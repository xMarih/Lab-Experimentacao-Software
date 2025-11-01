import os
import pandas as pd
import matplotlib.pyplot as plt
import logging
from tabulate import tabulate

# Diretório com os arquivos
DADOS_AGREGADOS_DIR = os.path.join(os.path.dirname(__file__), "resultados/dados_agregados")
GRAFICOS_DIR = os.path.join(os.path.dirname(__file__), "resultados/graficos_sentimento")
os.makedirs(DADOS_AGREGADOS_DIR, exist_ok=True)

# Configuração do logging
log_path = os.path.join(GRAFICOS_DIR, "log_evolução_sentimento.log")
logging.basicConfig(
    filename=log_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Busca arquivo dados_agregados por gênero
arquivos = [f for f in os.listdir(DADOS_AGREGADOS_DIR) if f.startswith("dados_agregados_") and f.endswith(".csv")]

for nome_arquivo in arquivos:
    genero = nome_arquivo.replace("dados_agregados_", "").replace(".csv", "")
    caminho = os.path.join(DADOS_AGREGADOS_DIR, nome_arquivo)

    df = pd.read_csv(caminho, parse_dates=["date"])
    df = df.sort_values("date")

    if "Sentiment" not in df.columns or "Release" not in df.columns:
        logging.warning(f"Coluna 'Sentiment' ou 'Release' ausente em {nome_arquivo}.")
        continue

    # Obter datas das releases
    release_dates = df[df["Release"] > 0]["date"].tolist()

    if len(release_dates) < 2:
        logging.warning(f"Menos de 2 releases para o gênero {genero}.")
        continue

    pontos = []

    for i in range(len(release_dates) - 1):
        start_date = release_dates[i]
        end_date = release_dates[i + 1]

        intervalo = df[(df["date"] >= start_date) & (df["date"] < end_date)]

        if not intervalo.empty:
            media_sentimento = intervalo["Sentiment"].mean()
            data_ref = start_date + (end_date - start_date) / 2  # ponto médio para plotar no gráfico
            pontos.append((data_ref, media_sentimento))

    # Criar gráfico com pontos por intervalo
    if pontos:
        x, y = zip(*pontos)

        plt.figure(figsize=(10, 5))
        plt.plot(x, y, marker='o', linestyle='-', color='blue', linewidth=1)
        plt.title(f"Evolução do Sentimento por Intervalo de Release - Gênero: {genero}")
        plt.xlabel("Intervalo entre Releases")
        plt.ylabel("Sentimento Médio no Intervalo")
        plt.grid(True)

        for release_date in release_dates:
            plt.axvline(x=release_date, color='red', linestyle='--', linewidth=0.8, alpha=0.6)

        plt.tight_layout()
        output_path = os.path.join(GRAFICOS_DIR, f"grafico_sentimento_intervalo_{genero}.png")
        plt.savefig(output_path)
        plt.close()

        logging.info(f"Gráfico salvo para o gênero '{genero}': {output_path}")

        # Gerar tabela resumo
        tabela = []
        for i in range(len(pontos)):
            data_release = release_dates[i].strftime("%Y-%m-%d")
            media_sent = round(pontos[i][1], 4)
            tabela.append([data_release, media_sent])

        tabela_str = tabulate(tabela, headers=["Data Release", "Sentimento Médio"], tablefmt="grid")
        logging.info(f"\nResumo de sentimento por intervalo - Gênero: {genero}\n{tabela_str}")

    else:
        logging.warning(f"Nenhum intervalo válido com sentimento para o gênero {genero}.")