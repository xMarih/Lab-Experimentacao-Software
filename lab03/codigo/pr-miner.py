import os
import time
import requests
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
from github import Github
from github import RateLimitExceededException, UnknownObjectException
import concurrent.futures
import random
import sys
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

INPUT_REPOS_CSV = os.path.join(DATA_DIR, "cloned_repos.csv")
OUTPUT_PRS_CSV = os.path.join(DATA_DIR, "collected_prs_details.csv")
MAX_THREADS = 4
MAX_PRS_PER_REPO = 101

class GitHubTokenManager:
    """Gerencia a rotação de múltiplos tokens do GitHub para resiliência."""
    def __init__(self):
        self.tokens = [
            os.environ.get("GITHUB_TOKEN"),
            os.environ.get("GITHUB_TOKEN2"),
            os.environ.get("GITHUB_TOKEN3"),
        ]
        self.tokens = [t for t in self.tokens if t is not None]
        
        if not self.tokens:
            sys.exit("ERRO: Nenhuma variável de ambiente GITHUB_TOKEN, GITHUB_TOKEN2 ou GITHUB_TOKEN3 foi configurada.")

        self.current_token_index = 0
        self.max_tokens = len(self.tokens)
        self.active_token = self.tokens[0]
        self.g = self._init_github_instance(self.active_token)
        self.lock = threading.Lock()

        tqdm.write(f"\n🔑 Gerenciador de Tokens iniciado com {self.max_tokens} token(s).")
    
    def _init_github_instance(self, token):
        """Inicializa a instância do PyGithub."""
        return Github(token, timeout=30)

    def rotate_token(self):
        """Troca para o próximo token disponível."""
        with self.lock: 
            self.current_token_index = (self.current_token_index + 1) % self.max_tokens
            self.active_token = self.tokens[self.current_token_index]
            self.g = self._init_github_instance(self.active_token)
            tqdm.write(f"\n Rotação de Token: Novo token em uso (Index {self.current_token_index + 1}).")
      

    def handle_rate_limit(self, error):
            """
            Lida com o erro de limite de requisições, rotacionando o token ou pausando.
            Usa o limite GraphQL (graphql) como fallback se o limite REST (core) falhar.
            Retorna True se houve pausa/rotação, False caso contrário.
            """
            if not isinstance(error, RateLimitExceededException):
                return False
                
            tqdm.write(f"\n Limite de requisições atingido para o token atual (Index {self.current_token_index + 1}).")
            
            if self.max_tokens > 1 and self.current_token_index < self.max_tokens - 1:
                self.rotate_token()
                return True
            
            try:
                rate_limit_info = self.g.get_rate_limit()
                
                if hasattr(rate_limit_info, 'core'):
                    limit_info = rate_limit_info.core
                elif hasattr(rate_limit_info, 'graphql'):
                    limit_info = rate_limit_info.graphql
                else:
                    raise AttributeError("Não foi possível determinar o rate limit (core ou graphql).")
                
                reset_timestamp = limit_info.reset.timestamp()
                now = time.time()
                wait_seconds = max(int(reset_timestamp - now + 10), 600) 
                
                tqdm.write(f" Todos os {self.max_tokens} tokens atingiram o limite.")
                tqdm.write(f" Estimativa de espera: {time.strftime('%H:%M:%S', time.gmtime(wait_seconds))} (Reset: {time.ctime(reset_timestamp)})...")
                time.sleep(wait_seconds)
                
                if self.max_tokens > 1:
                    self.rotate_token()
                return True
                
            except Exception as e:
                tqdm.write(f" Erro ao checar rate limit: {e}. Pausando por 10 minutos.")
                time.sleep(600)
                
                if self.max_tokens > 1:
                    self.rotate_token()
                return True
            
            return False



def load_repos(file_path):
    """Carrega a lista de repositórios a serem minerados."""
    if not os.path.exists(file_path):
        tqdm.write(f" ERRO: Arquivo de repositórios '{file_path}' não encontrado. Execute o script de mineração de repos primeiro.")
        return pd.DataFrame()
    
    return pd.read_csv(file_path)

def load_collected_prs(file_path):
    """Carrega PRs já coletados para garantir continuidade."""
    required_cols = [
        "repo_full_name", "pr_number", "created_at", "closed_at", 
        "review_count", "time_to_close_hours" 
    ]
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if all(col in df.columns for col in required_cols):
                 return df
            else:
                tqdm.write(f" Arquivo '{file_path}' tem colunas incorretas. Iniciando novo arquivo.")
        except Exception as e:
            tqdm.write(f" Erro ao ler '{file_path}': {e}. Iniciando novo arquivo.")
    
    cols = required_cols + [
        "title", "body", "merged", "merged_at", "files_changed", 
        "additions", "deletions", "comments", "review_comments", "participant_count"
    ]
    return pd.DataFrame(columns=cols)

def save_prs_to_file(df, file_path):
    """Salva o DataFrame de PRs no arquivo CSV de forma incremental."""
    df.to_csv(file_path, index=False, encoding='utf-8')
    tqdm.write(f"Progresso salvo: {df.shape[0]} PRs em {file_path}")

def filter_remaining_repos(repos_df, collected_df):
    """
    Filtra os repositórios que já tiveram todos os seus PRs coletados.
    Se um repositório estiver no CSV de PRs, ele é considerado 'iniciado'.
    Para o propósito de continuidade simples, vamos considerar que, se o repositório
    estiver no arquivo de PRs, ele foi processado. Você pode refinar isso depois.
    """
    if collected_df.empty:
        return repos_df['full_name'].tolist()
        
    collected_repos = set(collected_df['repo_full_name'].unique())
    all_repos = repos_df['full_name'].tolist()
    remaining = [repo for repo in all_repos if repo not in collected_repos]
    
    
    return remaining



def fetch_pr_details_graphql(manager, owner, repo_name, pr_number):
    """
    Busca todos os detalhes de um único PR (reviews, comments, files, etc.)
    em uma única requisição GraphQL.
    """
    query = {
        "query": f"""
        {{
            repository(owner: "{owner}", name: "{repo_name}") {{
                pullRequest(number: {pr_number}) {{
                    id
                    title
                    body
                    state
                    merged
                    createdAt
                    closedAt
                    mergedAt
                    additions
                    deletions
                    changedFiles
                    reviews {{ totalCount }}
                    comments {{ totalCount }}
                    reviewThreads {{ totalCount }}
                    participants {{ totalCount }}
                }}
            }}
        }}
        """
    }
    
    headers = {"Authorization": f"bearer {manager.active_token}"}
    
    try:
        r = requests.post("https://api.github.com/graphql", headers=headers, json=query)
        
        if r.status_code == 403:
            
            return None 
            
        r.raise_for_status() 
        
        response_json = r.json()

        if "errors" in response_json or not response_json.get("data", {}).get("repository", {}).get("pullRequest"):
            tqdm.write(f"   GraphQL Error para PR #{pr_number}: {response_json.get('errors', ['Desconhecido'])}")
            return None

        return response_json["data"]["repository"]["pullRequest"]
    
    except requests.exceptions.RequestException as e:
        tqdm.write(f"    Erro de requisição GraphQL para PR #{pr_number}: {type(e).__name__}")
        return None

def process_single_repo(manager, repo_name, collected_prs_df):
    """
    Coleta os detalhes dos PRs para um único repositório, limitado por MAX_PRS_PER_REPO.
    Retorna o DataFrame de PRs coletados OU None em caso de falha/rate limit que exija espera.
    """
    tqdm.write(f"\n--- Iniciando coleta em: {repo_name} (Máx: {MAX_PRS_PER_REPO} PRs válidos) ---")
    owner, name = repo_name.split("/")
    repo_prs_data = []
    
    processed_pr_numbers = set(collected_prs_df[collected_prs_df['repo_full_name'] == repo_name]['pr_number'])
    
    valid_pr_count = len(processed_pr_numbers)
    
    if valid_pr_count >= MAX_PRS_PER_REPO:
         tqdm.write(f"   Limite de PRs ({MAX_PRS_PER_REPO}) já atingido em '{repo_name}'. Pulando.")
         return pd.DataFrame() 
    
    try:
        repo = manager.g.get_repo(repo_name)
        prs_list = repo.get_pulls(state='closed', sort='created', direction='desc')
        
        pr_bar = tqdm(prs_list, desc=f"   {repo_name}", total=prs_list.totalCount)
        
        for pr in pr_bar:
            
            if valid_pr_count >= MAX_PRS_PER_REPO:
                tqdm.write(f"   Limite de {MAX_PRS_PER_REPO} PRs válidos atingido para '{repo_name}'. Parando.")
                break 

            if pr.number in processed_pr_numbers:
                pr_bar.set_description(f"   {repo_name} (Pulando {len(processed_pr_numbers)} já coletados)")
                continue

            pr_data_raw = fetch_pr_details_graphql(manager, owner, name, pr.number)
            
            if pr_data_raw is None:
                if manager.handle_rate_limit(RateLimitExceededException("GraphQL Limit")):
                    return None 
                continue 

            pr_closed_at_str = pr_data_raw.get("closedAt")
            pr_created_at_str = pr_data_raw.get("createdAt")
            
            if not pr_closed_at_str or not pr_created_at_str:
                continue

            t_closed = datetime.fromisoformat(pr_closed_at_str.replace('Z', '+00:00'))
            t_created = datetime.fromisoformat(pr_created_at_str.replace('Z', '+00:00'))

            time_diff = t_closed - t_created
            if time_diff.total_seconds() < 3600:
                continue
            
            review_count = pr_data_raw.get("reviews", {}).get("totalCount", 0)
            if review_count == 0: 
                continue

            valid_pr_count += 1 

            pr_data = {
                "repo_full_name": repo_name,
                "pr_number": pr.number,
                "title": pr_data_raw.get("title") or "",
                "body": pr_data_raw.get("body") or "",
                "state": pr_data_raw.get("state"),
                "merged": pr_data_raw.get("merged"),
                "created_at": pr_created_at_str,
                "closed_at": pr_closed_at_str,
                "merged_at": pr_data_raw.get("mergedAt"),
                "files_changed": pr_data_raw.get("changedFiles"),
                "additions": pr_data_raw.get("additions"),
                "deletions": pr_data_raw.get("deletions"),
                "review_count": review_count, 
                "comments": pr_data_raw.get("comments", {}).get("totalCount", 0),
                "review_comments": pr_data_raw.get("reviewThreads", {}).get("totalCount", 0),
                "participant_count": pr_data_raw.get("participants", {}).get("totalCount", 0),
                "time_to_close_hours": time_diff.total_seconds() / 3600,
            }
            repo_prs_data.append(pr_data)

        tqdm.write(f"   Repositório '{repo_name}' concluído com {len(repo_prs_data)} PRs coletados nesta sessão.")
        return pd.DataFrame(repo_prs_data)
    
    except RateLimitExceededException as e:
        manager.handle_rate_limit(e)
        return None 
    
    except UnknownObjectException:
        tqdm.write(f"   Repositório '{repo_name}' não encontrado no GitHub. Pulando.")
        return pd.DataFrame() 
        
    except Exception as e:
        tqdm.write(f"   Erro geral durante a coleta de PRs de '{repo_name}': {type(e).__name__} - {e}")
        time.sleep(random.randint(30, 90))
        return None

def main():
    start_time = time.time()
    
    manager = GitHubTokenManager()
    
    repos_df = load_repos(INPUT_REPOS_CSV)
    if repos_df.empty:
        return
    collected_prs_df = load_collected_prs(OUTPUT_PRS_CSV)

    remaining_repos = filter_remaining_repos(repos_df, collected_prs_df)
    
    if not remaining_repos:
        tqdm.write("\n Todos os repositórios foram processados. Fim da coleta.")
        return

    total_repos = len(remaining_repos)
    tqdm.write(f"\n Iniciando coleta detalhada de {total_repos} repositórios restantes com {MAX_THREADS} threads...")

    all_prs_data = collected_prs_df.to_dict(orient="records")
    
    repo_queue = list(remaining_repos)
    repos_processed_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        
        future_to_repo = {}
        
        while repo_queue or future_to_repo:
            
            while repo_queue and len(future_to_repo) < MAX_THREADS:
                repo_name = repo_queue.pop(0)
                
                future = executor.submit(process_single_repo, manager, repo_name, collected_prs_df)
                future_to_repo[future] = repo_name
                tqdm.write(f"Thread iniciada para: {repo_name}. (Fila: {len(repo_queue)}, Ativas: {len(future_to_repo)})")

            if not future_to_repo:
                break 

            done, _ = concurrent.futures.wait(
                future_to_repo, 
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done:
                repo_name = future_to_repo.pop(future)
                
                try:
                    result_df = future.result() 

                    if result_df is None:
                        tqdm.write(f" Rate Limit/Erro na thread de '{repo_name}'. Repositório será re-enviado.")
                        repo_queue.insert(0, repo_name) 
                        
                    elif result_df.empty:
                        tqdm.write(f"Repositório '{repo_name}' não retornou PRs válidos. Marcando como concluído.")
                        repos_processed_count += 1
                        
                    else:
                        all_prs_data.extend(result_df.to_dict(orient="records"))
                        current_df = pd.DataFrame(all_prs_data)
                        current_df.drop_duplicates(subset=["repo_full_name", "pr_number"], inplace=True)
                        save_prs_to_file(current_df, OUTPUT_PRS_CSV) 
                        
                        tqdm.write(f"   Repositório '{repo_name}' CONCLUÍDO. Total: {len(current_df)} PRs salvos.")
                        repos_processed_count += 1

                except Exception as exc:
                    tqdm.write(f" Erro fatal na thread de '{repo_name}': {exc}. Repositório re-enviado.")
                    repo_queue.insert(0, repo_name) 
            
    print("\n" + "=" * 50)
    print(f" Processo Finalizado.")
    print(f"Total de Repositórios Processados: {repos_processed_count}")
    print(f"Tempo total de execução: {time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))}")
    print(f"Dados salvos em: {OUTPUT_PRS_CSV}")
    print("=" * 50)


if __name__ == '__main__':
    main()
