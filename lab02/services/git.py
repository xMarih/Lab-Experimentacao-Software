import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import os

class GitHubService:
    def __init__(self, token: str):
        """
        Inicializa o serviço do GitHub

        Args:
            token: Token de acesso pessoal do GitHub
        """
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.url = 'https://api.github.com/graphql'

    def create_query(self, first: int = 100, after: Optional[str] = None) -> str:
        """
        Cria a query GraphQL para buscar repositórios populares

        Args:
            first: Número de repositórios para buscar
            after: Cursor para paginação

        Returns:
            String da query GraphQL
        """
        after_clause = f', after: "{after}"' if after else ''

        query = f"""
        {{
          search(query: "stars:>1", type: REPOSITORY, first: {first}{after_clause}) {{
            pageInfo {{
              hasNextPage
              endCursor
            }}
            repositoryCount
            edges {{
              node {{
                ... on Repository {{
                  name
                  owner {{
                    login
                  }}
                  stargazerCount
                  createdAt
                  updatedAt
                  primaryLanguage {{
                    name
                  }}
                  pullRequests(states: MERGED) {{
                    totalCount
                  }}
                  releases {{
                    totalCount
                  }}
                  issues {{
                    totalCount
                  }}
                  closedIssues: issues(states: CLOSED) {{
                    totalCount
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        return query

    def make_request(self, query: str) -> Dict:
        """
        Faz a requisição para a API GraphQL do GitHub

        Args:
            query: Query GraphQL

        Returns:
            Resposta da API em formato dict
        """
        response = requests.post(
            self.url,
            headers=self.headers,
            json={'query': query}
        )

        if response.status_code != 200:
            raise Exception(f"Erro na requisição: {response.status_code}")

        data = response.json()

        if 'errors' in data:
            raise Exception(f"Erro na query GraphQL: {data['errors']}")

        return data

    def extract_repository_data(self, repo_node: Dict) -> Dict:
        """
        Extrai e processa os dados de um repositório

        Args:
            repo_node: Nó do repositório da resposta GraphQL

        Returns:
            Dicionário com dados processados do repositório
        """
        created_at = datetime.fromisoformat(repo_node['createdAt'].replace('Z', '+00:00'))
        age_days = (datetime.now().astimezone() - created_at).days

        updated_at = datetime.fromisoformat(repo_node['updatedAt'].replace('Z', '+00:00'))
        days_since_update = (datetime.now().astimezone() - updated_at).days

        total_issues = repo_node['issues']['totalCount']
        closed_issues = repo_node['closedIssues']['totalCount']
        closed_issues_ratio = (closed_issues / total_issues * 100) if total_issues > 0 else 0

        primary_language = repo_node['primaryLanguage']['name'] if repo_node['primaryLanguage'] else 'Unknown'

        return {
            'name': repo_node['name'],
            'owner': repo_node['owner']['login'],
            'stars': repo_node['stargazerCount'],
            'created_at': repo_node['createdAt'],
            'updated_at': repo_node['updatedAt'],
            'age_days': age_days,
            'days_since_update': days_since_update,
            'merged_pull_requests': repo_node['pullRequests']['totalCount'],
            'total_releases': repo_node['releases']['totalCount'],
            'primary_language': primary_language,
            'total_issues': total_issues,
            'closed_issues': closed_issues,
            'closed_issues_ratio': round(closed_issues_ratio, 2)
        }

    def collect_repositories(self, total_repos: int = 100) -> List[Dict]:
        """
        Coleta dados dos repositórios mais populares com páginas menores
        """
        repositories = []
        after_cursor = None
        collected = 0

        page_size = 40  # Tamanho da página menor para evitar timeouts

        print(f"Iniciando coleta de {total_repos} repositórios (páginas de {page_size})...")

        while collected < total_repos:
            remaining = total_repos - collected
            fetch_count = min(page_size, remaining)

            query = self.create_query(fetch_count, after_cursor)

            try:
                response = self.make_request(query)

                search_result = response['data']['search']
                edges = search_result['edges']

                for edge in edges:
                    repo_data = self.extract_repository_data(edge['node'])
                    repositories.append(repo_data)
                    collected += 1

                    if collected % 10 == 0:
                        print(f"Coletados {collected}/{total_repos} repositórios...")

                time.sleep(1)  

                page_info = search_result['pageInfo']
                if page_info['hasNextPage'] and collected < total_repos:
                    after_cursor = page_info['endCursor']
                else:
                    break

            except Exception as e:
                print(f"Erro na página {collected // page_size + 1}: {e}")
                time.sleep(1) 
                continue

        print(f"Coleta finalizada! {len(repositories)} repositórios coletados.")
        return repositories