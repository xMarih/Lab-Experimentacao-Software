import os
import json
import time
import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO ---
# Se você setou a variável de ambiente: $env:GITHUB_TOKEN="seu_token"
# Caso contrário, substitua o valor do TOKEN abaixo.
TOKEN = os.environ.get("GITHUB_TOKEN", "SEU_GITHUB_TOKEN_AQUI") 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_CSV = os.path.join(DATA_DIR, "cloned_repos.csv")
TARGET_REPOS = 200
MIN_PRS_WITH_REVIEW = 100
MIN_PR_LIFESPAN_HOURS = 1 # PR deve ter levado pelo menos 1 hora para ser fechado/mesclado

# --- FUNÇÕES AUXILIARES ---

def handle_rate_limit(response, fallback_wait=600):
    """Lida com erros de limite de taxa (Rate Limit) da API do GitHub."""
    if response.status_code == 403 and int(response.headers.get("X-RateLimit-Remaining", 1)) == 0:
        reset_timestamp = int(response.headers.get("X-RateLimit-Reset", time.time() + fallback_wait))
        now = int(time.time())
        wait_seconds = max(reset_timestamp - now + 10, 10) # Espera até o reset + 10s de buffer
        
        tqdm.write(f"\n🚦 Limite de requisições da API atingido (403).")
        tqdm.write(f"⏳ Esperando {wait_seconds} segundos até a liberação.")
        time.sleep(wait_seconds)
        return True
    
    if response.status_code != 200:
        tqdm.write(f"\n⚠️ Erro na requisição: {response.status_code} - {response.reason}")
        # Tenta esperar um pouco por outros erros temporários
        time.sleep(10) 
        return True
        
    return False

def filter_repos_with_min_prs(token, needed=TARGET_REPOS, min_prs=MIN_PRS_WITH_REVIEW):
    """
    Usa a API REST para buscar repos e a API GraphQL para verificar PRs revisados.
    Inclui a filtragem de PRs com tempo de vida mínimo.
    """
    headers_rest = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    headers_graphql = {
        "Authorization": f"bearer {token}"
    }

    all_filtered = []
    page = 1
    max_pr_fetch = 100 # Número de PRs por requisição GraphQL
    
    print(f"🔍 Iniciando coleta de repositórios: +1000 estrelas e pelo menos {min_prs} PRs válidos...")

    while len(all_filtered) < needed:
        # 1. API REST: Busca repositórios por popularidade
        params = {
            "q": "stars:>1000",
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
            "page": page
        }

        response = requests.get("https://api.github.com/search/repositories", headers=headers_rest, params=params)
        
        if handle_rate_limit(response):
            continue

        repos = response.json().get("items", [])
        if not repos:
            print("\n🏁 Não há mais repositórios para buscar na API REST.")
            break

        tqdm.write(f"\n🔄 Processando página {page} da API REST ({len(repos)} repositórios)...")
        
        # 2. API GraphQL: Filtra PRs por review e tempo de vida
        repos_nesta_pagina = []
        
        for repo in tqdm(repos, desc=f"  ⚙️ Filtrando PRs revisados e com tempo > {MIN_PR_LIFESPAN_HOURS}h", ncols=120):
            owner, name = repo["full_name"].split("/")
            valid_prs_count = 0
            cursor = None
            
            # Limita a busca para evitar requisições infinitas e muito longas
            max_prs_to_check = 1000 # Verifica até 1000 PRs mais recentes do repositório
            checked_count = 0
            
            while checked_count < max_prs_to_check:
                after_clause = f', after: "{cursor}"' if cursor else ""
                
                # Consulta para buscar PRs fechados/mesclados, reviews e datas
                query = {
                    "query": f"""
                    {{
                        repository(owner: \"{owner}\", name: \"{name}\") {{
                            pullRequests(states: [MERGED, CLOSED], first: {max_pr_fetch}{after_clause}, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
                                nodes {{
                                    reviews {{ totalCount }}
                                    createdAt
                                    closedAt
                                }}
                                pageInfo {{ hasNextPage endCursor }}
                            }}
                        }}
                    }}
                    """
                }

                try:
                    r = requests.post("https://api.github.com/graphql", headers=headers_graphql, json=query)
                    
                    if handle_rate_limit(r):
                        # Se o rate limit for atingido, a pausa já ocorreu, tenta o loop novamente.
                        continue 
                        
                    response_json = r.json()

                    # Lida com erros do GraphQL, como repositório não encontrado
                    if "errors" in response_json or not response_json.get("data", {}).get("repository", {}).get("pullRequests"):
                         break

                    pr_data = response_json["data"]["repository"]["pullRequests"]
                    
                    for pr in pr_data["nodes"]:
                        # 1. Checa se o PR tem review
                        has_review = pr["reviews"]["totalCount"] > 0

                        # 2. Checa o critério de tempo de vida (Closed - Created > 1 hora)
                        pr_closed_at = pr.get("closedAt")
                        pr_created_at = pr.get("createdAt")
                        
                        time_valid = False
                        if pr_closed_at and pr_created_at:
                            try:
                                t_closed = datetime.fromisoformat(pr_closed_at.replace('Z', '+00:00'))
                                t_created = datetime.fromisoformat(pr_created_at.replace('Z', '+00:00'))
                                
                                # Verifica se a diferença de tempo é maior que 1 hora
                                time_diff = t_closed - t_created
                                if time_diff > timedelta(hours=MIN_PR_LIFESPAN_HOURS):
                                    time_valid = True
                            except:
                                # Ignora se as datas estiverem inválidas
                                pass

                        if has_review and time_valid:
                            valid_prs_count += 1

                    checked_count += len(pr_data["nodes"])
                    
                    if not pr_data["pageInfo"]["hasNextPage"] or valid_prs_count >= min_prs:
                        break # Para se não houver mais páginas ou se já atingiu o mínimo
                    
                    cursor = pr_data["pageInfo"]["endCursor"]

                except Exception as e:
                    tqdm.write(f"  ❌ Erro ao buscar PRs do repo {repo['full_name']}: {type(e).__name__} - {e}")
                    break
            
            # 3. Verifica se o repositório é válido
            if valid_prs_count >= min_prs:
                repo["pr_count"] = valid_prs_count
                repos_nesta_pagina.append(repo)
        
        all_filtered.extend(repos_nesta_pagina)
        
        print(f"\n✅ Página {page} finalizada. Total acumulado: {len(all_filtered)} repositórios válidos.")
        print("-" * 50)
        
        # 4. Salva o progresso
        if all_filtered:
            save_repos_to_files(all_filtered, OUTPUT_CSV)

        if len(all_filtered) >= needed:
            break
            
        page += 1

    return all_filtered[:needed]

def save_repos_to_files(repos, file_path):
    """Salva a lista de repositórios em um arquivo CSV."""
    if not repos:
        print("🔴 Nenhum repositório válido coletado. Arquivos não foram salvos.")
        return

    # Colunas requeridas no output
    selected = [
        "id", "full_name", "description", "language",
        "stargazers_count", "forks_count", "open_issues_count", "pr_count"
    ]
    
    rows = [{k: r.get(k) for k in selected} for r in repos]
    df = pd.DataFrame(rows)

    # Limita o tamanho da descrição para evitar problemas de visualização
    df["description"] = df["description"].apply(
        lambda x: (x[:300] + "...") if isinstance(x, str) and len(x) > 300 else x
    )

    try:
        # Salva CSV com separador padrão (vírgula)
        df.to_csv(file_path, index=False, encoding="utf-8")
        tqdm.write(f"  💾 {len(repos)} repositórios salvos em {file_path}")
    except Exception as e:
        tqdm.write(f"🔴 Erro ao salvar o arquivo CSV: {e}")

# --- EXECUÇÃO PRINCIPAL ---
def main():
    if TOKEN == "SEU_GITHUB_TOKEN_AQUI":
        print("🔴 ERRO: Por favor, substitua 'SEU_GITHUB_TOKEN_AQUI' ou configure a variável de ambiente GITHUB_TOKEN.")
        return
        
    start_time = time.time()
    
    # Inicia a coleta
    filtered_repos = filter_repos_with_min_prs(TOKEN)

    # 5. Filtragem e salvamento final
    final_repos = filtered_repos[:TARGET_REPOS]
    save_repos_to_files(final_repos, OUTPUT_CSV)
    
    print("\n" + "=" * 50)
    print(f"🎉 Processo Finalizado.")
    print(f"Total de repositórios válidos salvos: {len(final_repos)}")
    print(f"Arquivo de saída: {OUTPUT_CSV}")
    print(f"Tempo total de execução: {time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}")
    print("=" * 50)

if __name__ == "__main__":
    main()