import requests
import csv
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

env_path = Path('../..') / '.env'
load_dotenv(env_path)

GITHUB_TOKEN = os.getenv('TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("Token não encontrado no arquivo .env")

HEADERS = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Content-Type': 'application/json',
}

QUERY = """
query TopJavaMavenRepos($cursor: String) {
    search(
        query: "language:Java maven in:description,readme \\"pom\\" in:path sort:stars-desc"
        type: REPOSITORY
        first: 100
        after: $cursor
    ) {
        repositoryCount
        edges {
            node {
                ... on Repository {
                    nameWithOwner
                    url
                    stargazerCount
                    primaryLanguage {
                        name
                    }
                    createdAt
                    pushedAt
                    diskUsage
                    name
                }
            }
        }
        pageInfo {
            hasNextPage
            endCursor
        }
    }
}
"""

def calculate_time_diff(from_date):
    if not from_date:
        return "N/A"
    
    created_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    if created_date.tzinfo is None:
        created_date = created_date.replace(tzinfo=timezone.utc)
    
    diff = now - created_date    
    years = diff.days // 365
    months = (diff.days % 365) // 30
    days = (diff.days % 365) % 30
    
    if years > 0:
        return f"{years} anos, {months} meses"
    elif months > 0:
        return f"{months} meses, {days} dias"
    else:
        return f"{days} dias"

def format_disk_size(kb_size):
    if not kb_size:
        return "N/A"
    
    if kb_size >= 1024 * 1024:  # GB
        return f"{kb_size / (1024 * 1024):.1f} GB"
    elif kb_size >= 1024:  # MB
        return f"{kb_size / 1024:.1f} MB"
    else:
        return f"{kb_size} KB"

def fetch_github_repos():
    all_repos = []
    has_next_page = True
    end_cursor = None
    request_count = 0
    
    while has_next_page and len(all_repos) < 1000:
        variables = {"cursor": end_cursor}
        
        payload = {
            "query": QUERY,
            "variables": variables
        }
        
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json=payload,
                headers=HEADERS
            )
            
            request_count += 1
            
            if response.status_code != 200:
                print(f"Erro na requisição: {response.status_code}")
                print(response.text)
                break
            
            data = response.json()
            
            if 'errors' in data:
                print(f"Erros na resposta: {data['errors']}")
                break
            
            search_data = data['data']['search']
            
            for edge in search_data['edges']:
                repo = edge['node']
                all_repos.append({
                    'name_with_owner': repo['nameWithOwner'],
                    'url': repo['url'],
                    'stargazer_count': repo['stargazerCount'],
                    'primary_language': repo['primaryLanguage']['name'] if repo['primaryLanguage'] else 'N/A',
                    'created_at': repo['createdAt'],
                    'age': calculate_time_diff(repo['createdAt']),
                    'last_push': repo['pushedAt'],
                    'time_since_last_push': calculate_time_diff(repo['pushedAt']),
                    'disk_usage_kb': repo['diskUsage'],
                    'size_formatted': format_disk_size(repo['diskUsage']),
                    'name': repo['name']
                })
            
            page_info = search_data['pageInfo']
            has_next_page = page_info['hasNextPage']
            end_cursor = page_info['endCursor']
            
            print(f"Página {request_count}: {len(all_repos)} repositórios coletados")
            
            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if rate_limit_remaining < 10:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - time.time(), 0) + 10
                print(f"Rate limit baixo. Esperando {wait_time:.0f} segundos...")
                time.sleep(wait_time)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro durante a requisição: {e}")
            break
    
    return all_repos[:1000]

def save_to_csv(repos):
    if not repos:
        print("Nenhum repositório para salvar.")
        return
    
    csv_dir = Path('..') / 'csvFiles'
    csv_dir.mkdir(exist_ok=True)
    
    filename = csv_dir / 'java_maven_repos_detailed.csv'

    if filename.exists():
        os.remove(filename)
        print(f"Arquivo existente '{filename}' removido.")
    
    fieldnames = [
        'name_with_owner', 
        'url', 
        'stargazer_count', 
        'primary_language',
        'created_at',
        'age',
        'last_push',
        'time_since_last_push',
        'disk_usage_kb',
        'size_formatted',
        'name'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for repo in repos:
            writer.writerow(repo)
    
    print(f"Arquivo '{filename}' salvo com {len(repos)} repositórios.")

def main():
    print("Iniciando busca por repositórios Java Maven...")
    
    repos = fetch_github_repos()
    
    if repos:
        save_to_csv(repos)
        print(f"\nBusca concluída! Total de {len(repos)} repositórios encontrados.")
    else:
        print("Nenhum repositório foi encontrado.")

if __name__ == "__main__":
    main()