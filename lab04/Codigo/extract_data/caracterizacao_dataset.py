"""
Gera caracterização do dataset para o dashboard BI.
Análise descritiva dos dados coletados do Steam, incluindo:
- Distribuição de jogos por gênero
- Estatísticas de reviews (quantidade, sentimento)
- Análise temporal das reviews
- Tópicos mais comuns
- Comparações entre subgrupos
"""
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient
import numpy as np
from datetime import datetime

# Configurar estilo dos gráficos
sns.set_style("whitegrid")  # Define o estilo do seaborn
sns.set_palette("husl")     # Define a paleta de cores
plt.style.use('default')    # Usa o estilo padrão do matplotlib

def connect_mongo():
    """Conecta ao MongoDB e retorna client"""
    MONGO_URI = "mongodb://admin:password@localhost:27018/games?authSource=admin"
    return MongoClient(MONGO_URI)

def load_collections(client):
    """Carrega as coleções principais em DataFrames"""
    db = client.games
    
    # Carregar dados
    sellers_df = pd.DataFrame(list(db.top_sellers_info.find()))
    reviews_df = pd.DataFrame(list(db.steam_reviews.find()))
    topics_df = pd.DataFrame(list(db.topic_reviews.find()))
    
    return sellers_df, reviews_df, topics_df

def criar_diretorio_output():
    """Cria diretório para salvar análises se não existir"""
    output_dir = "caracterizacao_output"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def analise_generos(sellers_df, output_dir):
    """Análise da distribuição de jogos por gênero"""
    if 'genero' in sellers_df.columns:
        # Contagem de jogos por gênero
        generos_count = sellers_df['genero'].value_counts()
        
        plt.figure(figsize=(12, 6))
        generos_count.plot(kind='bar')
        plt.title('Distribuição de Jogos por Gênero')
        plt.xlabel('Gênero')
        plt.ylabel('Número de Jogos')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/distribuicao_generos.png")
        plt.close()
        
        # Salvar dados
        generos_count.to_csv(f"{output_dir}/distribuicao_generos.csv")
        
        return generos_count

def analise_reviews(reviews_df, output_dir):
    """Análise das reviews: quantidade, distribuição temporal, sentimentos"""
    if len(reviews_df) == 0:
        return None
        
    # Estatísticas gerais
    stats = {
        'total_reviews': len(reviews_df),
        'reviews_por_jogo': reviews_df.groupby('appid').size().describe(),
    }
    
    # Se tiver campo de sentimento
    if 'sentiment' in reviews_df.columns:
        sentiment_dist = reviews_df['sentiment'].value_counts()
        
        plt.figure(figsize=(10, 6))
        sentiment_dist.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Distribuição de Sentimentos nas Reviews')
        plt.savefig(f"{output_dir}/distribuicao_sentimentos.png")
        plt.close()
        
        stats['sentiment_distribution'] = sentiment_dist
    
    # Análise temporal se tiver data
    if 'created_at' in reviews_df.columns:
        reviews_df['created_at'] = pd.to_datetime(reviews_df['created_at'])
        reviews_por_mes = reviews_df.set_index('created_at').resample('M').size()
        
        plt.figure(figsize=(15, 6))
        reviews_por_mes.plot()
        plt.title('Evolução do Número de Reviews ao Longo do Tempo')
        plt.xlabel('Data')
        plt.ylabel('Número de Reviews')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/evolucao_temporal_reviews.png")
        plt.close()
        
        stats['reviews_temporais'] = reviews_por_mes
    
    # Salvar estatísticas
    with open(f"{output_dir}/estatisticas_reviews.txt", 'w') as f:
        f.write("Estatísticas das Reviews\n")
        f.write("=======================\n\n")
        f.write(f"Total de reviews: {stats['total_reviews']}\n\n")
        f.write("Estatísticas de reviews por jogo:\n")
        f.write(str(stats['reviews_por_jogo']))
    
    return stats

def analise_topicos(topics_df, output_dir):
    """Análise dos tópicos identificados nas reviews"""
    if 'topics' in topics_df.columns:
        # Frequência dos tópicos
        topic_counts = topics_df['topics'].value_counts()
        
        plt.figure(figsize=(12, 6))
        topic_counts.head(10).plot(kind='bar')
        plt.title('Top 10 Tópicos mais Frequentes')
        plt.xlabel('Tópico')
        plt.ylabel('Frequência')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/top_topicos.png")
        plt.close()
        
        # Salvar dados
        topic_counts.to_csv(f"{output_dir}/frequencia_topicos.csv")
        
        return topic_counts

def gerar_relatorio_caracterizacao(stats, output_dir):
    """Gera relatório markdown com a caracterização do dataset"""
    report = f"""# Caracterização do Dataset - Steam Games Reviews

## Visão Geral
- **Total de Reviews Analisadas**: {stats.get('total_reviews', 'N/A')}
- **Período da Análise**: {stats.get('periodo_analise', 'N/A')}

## Distribuição por Gênero
Ver arquivo: distribuicao_generos.csv e gráfico distribuicao_generos.png

## Análise das Reviews
- Ver estatísticas detalhadas em: estatisticas_reviews.txt
- Distribuição de sentimentos: distribuicao_sentimentos.png
- Evolução temporal: evolucao_temporal_reviews.png

## Tópicos Identificados
Ver arquivo: frequencia_topicos.csv e gráfico top_topicos.png

## Notas Metodológicas
- Dados coletados via Steam API
- Processamento de tópicos utilizando LDA
- Análise de sentimentos realizada com VADER

## Arquivos Gerados
- CSV com dados processados em ../exports/
- Visualizações em formato PNG
- Estatísticas descritivas em TXT/CSV
"""
    
    with open(f"{output_dir}/relatorio_caracterizacao.md", 'w', encoding='utf-8') as f:
        f.write(report)

def main():
    # Criar diretório para outputs
    output_dir = criar_diretorio_output()
    
    # Conectar ao MongoDB e carregar dados
    client = connect_mongo()
    try:
        sellers_df, reviews_df, topics_df = load_collections(client)
        
        # Realizar análises
        generos_stats = analise_generos(sellers_df, output_dir)
        reviews_stats = analise_reviews(reviews_df, output_dir)
        topics_stats = analise_topicos(topics_df, output_dir)
        
        # Compilar estatísticas
        stats = {
            'total_reviews': len(reviews_df) if reviews_df is not None else 0,
            'periodo_analise': 'TODO: extrair período dos dados',
            'generos_stats': generos_stats,
            'reviews_stats': reviews_stats,
            'topics_stats': topics_stats
        }
        
        # Gerar relatório
        gerar_relatorio_caracterizacao(stats, output_dir)
        
        print(f"\nCaracterização concluída! Verifique a pasta '{output_dir}' para ver os resultados.")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()