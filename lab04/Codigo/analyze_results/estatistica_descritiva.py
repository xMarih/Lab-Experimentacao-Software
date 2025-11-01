import os
import pandas as pd
from tabulate import tabulate
from datetime import datetime, timedelta

RESULTADOS_DIR = os.path.join(os.path.dirname(__file__), "resultados/dados_agregados")
ESTATISTICAS_DIR = os.path.join(os.path.dirname(__file__), "resultados/estatistica_descritiva")
os.makedirs(RESULTADOS_DIR, exist_ok=True)
os.makedirs(ESTATISTICAS_DIR, exist_ok=True)

def gerar_estatisticas_comparativas():
    arquivos = [f for f in os.listdir(RESULTADOS_DIR) if f.startswith("dados_agregados_") and f.endswith(".csv")]

    if not arquivos:
        print("Nenhum arquivo 'dados_agregados_*.csv' encontrado no diretório de resultados.")
        return

    dados_por_genero = {}

    for arquivo in arquivos:
        caminho = os.path.join(RESULTADOS_DIR, arquivo)
        genero = arquivo.replace("dados_agregados_", "").replace(".csv", "")

        try:
            df = pd.read_csv(caminho)
        except Exception as e:
            print(f"Erro ao ler o arquivo '{arquivo}': {e}")
            continue

        if df.empty:
            print(f"Arquivo '{arquivo}' está vazio.")
            continue

        df.columns = df.columns.str.strip()

        # Filtrar por data
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            limite_data = datetime.now() - timedelta(days=365)
            df = df[df["date"] >= limite_data]
            print(f"[{genero}] Filtrando dados a partir de {limite_data.date()} – {len(df)} registros restantes.")

        dados_por_genero[genero] = df

    if not dados_por_genero:
        print("Nenhum dado válido encontrado para comparação.")
        return

    colunas_numericas = set()
    for df in dados_por_genero.values():
        colunas_numericas.update(df.select_dtypes(include=["float64", "int64"]).columns)

    for coluna in sorted(colunas_numericas):
        estatisticas = []
        for genero, df in dados_por_genero.items():
            if coluna in df.columns:
                desc = df[coluna].describe()
                estatisticas.append({
                    "index": genero,
                    "count": int(desc.get("count", 0)),
                    "mean": round(desc.get("mean", 0), 2),
                    "std": round(desc.get("std", 0), 2),
                    "min": round(desc.get("min", 0), 2),
                    "25%": round(desc.get("25%", 0), 2),
                    "50%": round(desc.get("50%", 0), 2),
                    "75%": round(desc.get("75%", 0), 2),
                    "max": round(desc.get("max", 0), 2),
                })

        if estatisticas:
            df_stats = pd.DataFrame(estatisticas)
            tabela = tabulate(df_stats, headers="keys", tablefmt="grid", showindex=False)
            print(f"\nEstatísticas para coluna: {coluna}\n")
            print(tabela)

            txt_path = os.path.join(ESTATISTICAS_DIR, f"estatísticas_{coluna.replace(' ', '_')}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(tabela)

            print(f"Salvo em: {txt_path}")

if __name__ == "__main__":
    gerar_estatisticas_comparativas()