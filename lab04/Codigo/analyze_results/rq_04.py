import os
import logging
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict

"RQ04 – Qual a relação entre o tipo de release e os sentimentos dos jogadores?"

# Diretórios
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR_COERENCIA = os.path.join(BASE_DIR, "resultados/coerencia")
INPUT_DIR_LDA = os.path.join(BASE_DIR, "resultados/lda_patchnotes")
INPUT_DIR_CLASSIFICACAO = os.path.join(BASE_DIR, "resultados/classificacao_release")
INPUT_DIR_GPT = os.path.join(BASE_DIR, "resultados/respostas_chatgpt")
GRAFICOS_DIR = os.path.join(BASE_DIR, "resultados/rqs/rq04")
os.makedirs(GRAFICOS_DIR, exist_ok=True)

# Configuração do logger
log_path = os.path.join(GRAFICOS_DIR, "log_feelings_by_release.log")
logging.basicConfig(
    filename=log_path,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def calcular_sentimento_por_topico(releases, topicos):
    try:
        resultados = []
        
        textos_releases = [r['contents'].lower() for r in releases]
        sentimentos_releases = [r['avg_sentiment'] for r in releases]
        
        for topico in topicos:
            releases_relacionadas = []
            palavras_chave = [palavra.lower() for palavra in topico['palavras_chave']]
            
            for idx, texto in enumerate(textos_releases):
                if any(palavra in texto for palavra in palavras_chave):
                    releases_relacionadas.append(sentimentos_releases[idx])
            
            sentimento_medio = np.mean(releases_relacionadas) if releases_relacionadas else 0
            contagem_releases = len(releases_relacionadas)
            
            topico_com_sentimento = topico.copy()
            topico_com_sentimento.update({
                'sentimento_medio': sentimento_medio,
                'releases_relacionadas': contagem_releases
            })
            resultados.append(topico_com_sentimento)
        
        return resultados
        
    except Exception as e:
        logging.error(f"Erro ao calcular sentimento por tópico: {str(e)}")
        raise

def preparar_dados_para_tabela_recomendacoes():
    logging.info("Preparando dados para tabela de recomendações")
    
    dados_consolidados = defaultdict(lambda: {
        "positivas": {"releases": [], "coerencia": None, "topicos": []},
        "negativas": {"releases": [], "coerencia": None, "topicos": []}
    })
    
    try:
        arquivos_classificacao = [f for f in os.listdir(INPUT_DIR_CLASSIFICACAO) 
                                if f.startswith("releases_classificadas_") and f.endswith(".json")]
        
        for arquivo in arquivos_classificacao:
            genero = arquivo.replace("releases_classificadas_", "").replace(".json", "")
            caminho = os.path.join(INPUT_DIR_CLASSIFICACAO, arquivo)
            
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            dados_consolidados[genero]["positivas"]["releases"] = dados.get("releases_positivas", [])
            dados_consolidados[genero]["negativas"]["releases"] = dados.get("releases_negativas", [])

        arquivos_lda = [f for f in os.listdir(INPUT_DIR_LDA) 
                      if f.startswith("lda_patchnotes_") and f.endswith(".json")]
        
        for arquivo in arquivos_lda:
            genero = arquivo.replace("lda_patchnotes_", "").replace(".json", "")
            caminho = os.path.join(INPUT_DIR_LDA, arquivo)
            
            with open(caminho, "r", encoding="utf-8") as f:
                dados_lda = json.load(f)
            
            caminho_ia = os.path.join(INPUT_DIR_GPT, f"resposta_{genero}.json")
            if os.path.exists(caminho_ia):
                with open(caminho_ia, "r", encoding="utf-8") as f:
                    dados_ia = json.load(f)
            else:
                logging.warning(f"Arquivo de IA não encontrado para {genero}")
                dados_ia = []

            topicos_positivos = []
            for topico_lda, topico_ia in zip(
                dados_lda["releases_positivas"]["topicos"].values(),
                [t for t in dados_ia if t["sentimento"] == "positivo"]
            ):
                topicos_positivos.append({
                    "palavras_chave": topico_lda,
                    "titulo": topico_ia.get("topico", ""),
                    "descricao": topico_ia.get("descricao", "")
                })

            topicos_negativos = []
            for topico_lda, topico_ia in zip(
                dados_lda["releases_negativas"]["topicos"].values(),
                [t for t in dados_ia if t["sentimento"] == "negativo"]
            ):
                topicos_negativos.append({
                    "palavras_chave": topico_lda,
                    "titulo": topico_ia.get("topico", ""),
                    "descricao": topico_ia.get("descricao", "")
                })
            
            dados_consolidados[genero]["positivas"]["topicos"] = topicos_positivos
            dados_consolidados[genero]["negativas"]["topicos"] = topicos_negativos

        arquivos_coerencia = [f for f in os.listdir(INPUT_DIR_COERENCIA) 
                            if f.startswith("coerencia_resultados") and f.endswith(".json")]
        
        if arquivos_coerencia:
            caminho = os.path.join(INPUT_DIR_COERENCIA, arquivos_coerencia[0])
            with open(caminho, "r", encoding="utf-8") as f:
                dados_coerencia = json.load(f)
            
            for genero in dados_coerencia:
                if genero in dados_consolidados:
                    dados_consolidados[genero]["positivas"]["coerencia"] = dados_coerencia[genero]["positivas"]
                    dados_consolidados[genero]["negativas"]["coerencia"] = dados_coerencia[genero]["negativas"]

        # 4. Calcular sentimento por tópico
        for genero in dados_consolidados:
            dados_consolidados[genero]["positivas"]["topicos"] = calcular_sentimento_por_topico(
                dados_consolidados[genero]["positivas"]["releases"],
                dados_consolidados[genero]["positivas"]["topicos"]
            )
            
            dados_consolidados[genero]["negativas"]["topicos"] = calcular_sentimento_por_topico(
                dados_consolidados[genero]["negativas"]["releases"],
                dados_consolidados[genero]["negativas"]["topicos"]
            )

        return dados_consolidados
        
    except Exception as e:
        logging.error(f"Erro ao preparar dados para recomendações: {str(e)}")
        raise

def preparar_dados_para_tabela_resumo():
    logging.info("Iniciando preparação dos dados para análise de sentimento por tipo de release")
    
    dados_consolidados = defaultdict(lambda: {
        "positivas": {"sentimentos": [], "coerencia": None, "topicos": None, "topicos_ia": []},
        "negativas": {"sentimentos": [], "coerencia": None, "topicos": None, "topicos_ia": []}
    })
    
    try:
        arquivos_classificacao = [f for f in os.listdir(INPUT_DIR_CLASSIFICACAO) 
                                if f.startswith("releases_classificadas_") and f.endswith(".json")]
        
        for arquivo in arquivos_classificacao:
            genero = arquivo.replace("releases_classificadas_", "").replace(".json", "")
            caminho = os.path.join(INPUT_DIR_CLASSIFICACAO, arquivo)
            
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            dados_consolidados[genero]["positivas"]["sentimentos"] = [
                r["avg_sentiment"] for r in dados.get("releases_positivas", [])
            ]
            dados_consolidados[genero]["negativas"]["sentimentos"] = [
                r["avg_sentiment"] for r in dados.get("releases_negativas", [])
            ]
        
        arquivos_lda = [f for f in os.listdir(INPUT_DIR_LDA) 
                      if f.startswith("lda_patchnotes_") and f.endswith(".json")]
        
        for arquivo in arquivos_lda:
            genero = arquivo.replace("lda_patchnotes_", "").replace(".json", "")
            caminho = os.path.join(INPUT_DIR_LDA, arquivo)
            
            with open(caminho, "r", encoding="utf-8") as f:
                dados_lda = json.load(f)
            
            caminho_ia = os.path.join(INPUT_DIR_GPT, f"resposta_{genero}.json")
            if os.path.exists(caminho_ia):
                with open(caminho_ia, "r", encoding="utf-8") as f:
                    dados_ia = json.load(f)
            else:
                logging.warning(f"Arquivo de IA não encontrado para {genero}")
                dados_ia = []

            topicos_positivos_lda = dados_lda["releases_positivas"]["topicos"]
            topicos_positivos_ia = [t for t in dados_ia if t["sentimento"] == "positivo"]
            topicos_positivos_combinados = []
            for i, (topico_lda, topico_ia) in enumerate(zip(topicos_positivos_lda.values(), topicos_positivos_ia)):
                topicos_positivos_combinados.append({
                    "id": i,
                    "palavras_chave": topico_lda,
                    "titulo": topico_ia.get("topico", ""),
                    "descricao": topico_ia.get("descricao", "")
                })

            topicos_negativos_lda = dados_lda["releases_negativas"]["topicos"]
            topicos_negativos_ia = [t for t in dados_ia if t["sentimento"] == "negativo"]
            
            topicos_negativos_combinados = []
            for i, (topico_lda, topico_ia) in enumerate(zip(topicos_negativos_lda.values(), topicos_negativos_ia)):
                topicos_negativos_combinados.append({
                    "id": i,
                    "palavras_chave": topico_lda,
                    "titulo": topico_ia.get("topico", ""),
                    "descricao": topico_ia.get("descricao", "")
                })
            
            dados_consolidados[genero]["positivas"]["topicos"] = topicos_positivos_combinados
            dados_consolidados[genero]["negativas"]["topicos"] = topicos_negativos_combinados
        
        arquivos_coerencia = [f for f in os.listdir(INPUT_DIR_COERENCIA) 
                            if f.startswith("coerencia_resultados") and f.endswith(".json")]
        
        if arquivos_coerencia:
            caminho = os.path.join(INPUT_DIR_COERENCIA, arquivos_coerencia[0])
            with open(caminho, "r", encoding="utf-8") as f:
                dados_coerencia = json.load(f)
            
            for genero in dados_coerencia:
                if genero in dados_consolidados:
                    dados_consolidados[genero]["positivas"]["coerencia"] = dados_coerencia[genero]["positivas"]
                    dados_consolidados[genero]["negativas"]["coerencia"] = dados_coerencia[genero]["negativas"]
        
        resultados = {}
        for genero, dados in dados_consolidados.items():
            resultados[genero] = {
                "positivas": {
                    "quantidade": len(dados["positivas"]["sentimentos"]),
                    "sentimento_medio": np.mean(dados["positivas"]["sentimentos"]) if dados["positivas"]["sentimentos"] else 0,
                    "sentimento_desvio_padrao": np.std(dados["positivas"]["sentimentos"]) if dados["positivas"]["sentimentos"] else 0,
                    "coerencia": dados["positivas"]["coerencia"],
                    "topicos": dados["positivas"]["topicos"]
                },
                "negativas": {
                    "quantidade": len(dados["negativas"]["sentimentos"]),
                    "sentimento_medio": np.mean(dados["negativas"]["sentimentos"]) if dados["negativas"]["sentimentos"] else 0,
                    "sentimento_desvio_padrao": np.std(dados["negativas"]["sentimentos"]) if dados["negativas"]["sentimentos"] else 0,
                    "coerencia": dados["negativas"]["coerencia"],
                    "topicos": dados["negativas"]["topicos"]
                }
            }
        
        logging.info(f"Total de gêneros processados: {len(resultados)}")
        
        return resultados
        
    except Exception as e:
        logging.error(f"Erro ao preparar dados: {str(e)}")
        raise

def gerar_tabela_png(dados_consolidados, nome_arquivo='tabela_resumo.png'):
    try:
        tabela_data = []
        for genero, dados in dados_consolidados.items():
            for tipo in ['positivas', 'negativas']:
                tabela_data.append({
                    'Gênero': genero,
                    'Tipo': tipo,
                    'Sentimento': f"{dados[tipo]['sentimento_medio']:.3f}",
                    'Coerência (c_v)': f"{dados[tipo]['coerencia']['c_v']:.3f}",
                    'Releases': dados[tipo]['quantidade']
                })
        
        df = pd.DataFrame(tabela_data)
        plt.figure(figsize=(12, 8))
        ax = plt.subplot(111, frame_on=False)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)
        
        tabela = plt.table(
            cellText=df.values,
            colLabels=df.columns,
            loc='center',
            cellLoc='center',
            colColours=['#f3f3f3']*len(df.columns)
        )
        
        tabela.auto_set_font_size(False)
        tabela.set_fontsize(10)
        tabela.scale(1.2, 1.2)
        
        for k, cell in tabela._cells.items():
            if k[0] == 0:
                cell.set_facecolor('#4daf4a')
                cell.set_text_props(color='white', weight='bold')
            else:
                if k[0] % 2 == 0:
                    cell.set_facecolor('#f9f9f9')
        
        plt.savefig(
            os.path.join(GRAFICOS_DIR, nome_arquivo),
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.5
        )
        plt.close()

        df.to_csv(os.path.join(GRAFICOS_DIR, 'tabela_resumo.csv'), index=False)
        
        logging.info(f"Tabela gerada como PNG: {nome_arquivo}")
        
    except Exception as e:
        logging.error(f"Erro ao gerar tabela PNG: {str(e)}")
        raise

def gerar_tabela_recomendacoes(dados_consolidados):
    try:
        recomendacoes = []
        
        for genero, dados in dados_consolidados.items():
            topicos_positivos = []
            for topico in dados['positivas']['topicos']:
                score = (topico.get('sentimento_medio', 0) * 0.7 + 
                        dados['positivas']['coerencia']['c_v'] * 0.3)
                topicos_positivos.append({
                    'titulo': topico['titulo'],
                    'score': score,
                    'sentimento': topico.get('sentimento_medio', 0),
                    'coerencia': dados['positivas']['coerencia']['c_v']
                })
            
            topicos_negativos = []
            for topico in dados['negativas']['topicos']:
                score = (topico.get('sentimento_medio', 0) * 0.7 + 
                        dados['negativas']['coerencia']['c_v'] * 0.3)
                topicos_negativos.append({
                    'titulo': topico['titulo'],
                    'score': score,
                    'sentimento': topico.get('sentimento_medio', 0),
                    'coerencia': dados['negativas']['coerencia']['c_v']
                })
            
            top_seguir = sorted(topicos_positivos, key=lambda x: x['score'], reverse=True)[:3]
            top_evitar = sorted(topicos_negativos, key=lambda x: x['score'])[:3]
            
            recomendacoes.append({
                'Gênero': genero,
                'Tópicos a seguir': "\n".join([f"{t['titulo']} (S:{t['sentimento']:.2f}, C:{t['coerencia']:.2f})" 
                                              for t in top_seguir]),
                'Tópicos a evitar': "\n".join([f"{t['titulo']} (S:{t['sentimento']:.2f}, C:{t['coerencia']:.2f})" 
                                             for t in top_evitar])
            })
        
        df = pd.DataFrame(recomendacoes)
        df.to_csv(os.path.join(GRAFICOS_DIR, 'recomendacoes_topicos.csv'), index=False)
        
        return df
        
    except Exception as e:
        logging.error(f"Erro ao gerar recomendações: {str(e)}")
        raise

def gerar_grafico_sentimentos(dados_consolidados):
    try:
        dados_plot = []
        for genero, dados in dados_consolidados.items():
            dados_plot.append({
                'Gênero': genero,
                'Positivas': dados['positivas']['sentimento_medio'],
                'Negativas': dados['negativas']['sentimento_medio']
            })
        
        df = pd.DataFrame(dados_plot).set_index('Gênero')
        
        plt.figure(figsize=(12, 6))
        ax = df.plot(kind='bar', color=['#4CAF50', '#F44336'], width=0.7)
        
        plt.title('Média de Sentimento por Gênero e Tipo de Release', pad=20, fontsize=14)
        plt.xlabel('Gênero', labelpad=10)
        plt.ylabel('Sentimento Médio', labelpad=10)
        plt.axhline(0, color='black', linewidth=0.5)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Tipo de Release', bbox_to_anchor=(1.05, 1))
        plt.grid(axis='y', alpha=0.3)
        
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.2f}", 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 5), 
                       textcoords='offset points')
        
        plt.tight_layout()
        plt.savefig(os.path.join(GRAFICOS_DIR, 'sentimento_por_genero.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info("Gráfico de sentimentos gerado com sucesso")
        
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico de sentimentos: {str(e)}")
        raise

def gerar_grafico_coerencia(dados_consolidados):
    try:
        dados_plot = []
        for genero, dados in dados_consolidados.items():
            dados_plot.append({
                'Gênero': genero,
                'Positivas': dados['positivas']['coerencia']['c_v'],
                'Negativas': dados['negativas']['coerencia']['c_v']
            })
        
        df = pd.DataFrame(dados_plot).set_index('Gênero')
        
        plt.figure(figsize=(12, 6))
        ax = df.plot(kind='bar', color=['#2196F3', '#FF9800'], width=0.7)
        
        plt.title('Coerência (c_v) por Gênero e Tipo de Release', pad=20, fontsize=14)
        plt.xlabel('Gênero', labelpad=10)
        plt.ylabel('Coerência (c_v)', labelpad=10)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Tipo de Release', bbox_to_anchor=(1.05, 1))
        plt.grid(axis='y', alpha=0.3)
        
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.2f}", 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha='center', va='center', 
                       xytext=(0, 5), 
                       textcoords='offset points')
        
        plt.tight_layout()
        plt.savefig(os.path.join(GRAFICOS_DIR, 'coerencia_por_genero.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info("Gráfico de coerência gerado com sucesso")
        
    except Exception as e:
        logging.error(f"Erro ao gerar gráfico de coerência: {str(e)}")
        raise

def main():
    dados_consolidados = preparar_dados_para_tabela_resumo()
    gerar_tabela_png(dados_consolidados)
    gerar_grafico_sentimentos(dados_consolidados)
    gerar_grafico_coerencia(dados_consolidados)
    dados_consolidados = preparar_dados_para_tabela_recomendacoes()
    gerar_tabela_recomendacoes(dados_consolidados)

if __name__ == "__main__":
    main()