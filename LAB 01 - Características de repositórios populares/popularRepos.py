import requests
import csv
import time
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

class GitHubAnalyzer:
    def __init__(self, token: str):
        """
        Inicializa o analisador do GitHub

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

        page_size = 10

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
                time.sleep(5)
                continue

        print(f"Coleta finalizada! {len(repositories)} repositórios coletados.")
        return repositories

    def analyze_by_language(self, repositories: List[Dict]) -> Dict:
        """
        Analisa dados agrupados por linguagem para RQ07 (BÔNUS)

        Args:
            repositories: Lista de repositórios

        Returns:
            Dicionário com análise por linguagem
        """
        by_language = defaultdict(list)

        for repo in repositories:
            lang = repo['primary_language']
            by_language[lang].append(repo)

        language_stats = {}

        for lang, repos in by_language.items():
            if len(repos) < 3:
                continue

            merged_prs = [repo['merged_pull_requests'] for repo in repos]

            releases = [repo['total_releases'] for repo in repos]

            days_since_update = [repo['days_since_update'] for repo in repos]

            language_stats[lang] = {
                'count': len(repos),
                'median_merged_prs': sorted(merged_prs)[len(merged_prs) // 2],
                'median_releases': sorted(releases)[len(releases) // 2],
                'median_days_since_update': sorted(days_since_update)[len(days_since_update) // 2],
                'avg_merged_prs': sum(merged_prs) / len(merged_prs),
                'avg_releases': sum(releases) / len(releases),
                'avg_days_since_update': sum(days_since_update) / len(days_since_update)
            }

        return language_stats

    def get_popular_languages(self, repositories: List[Dict], top_n: int = 5) -> List[str]:
        """
        Identifica as linguagens mais populares

        Args:
            repositories: Lista de repositórios
            top_n: Número de linguagens mais populares para retornar

        Returns:
            Lista das linguagens mais populares
        """
        language_count = defaultdict(int)

        for repo in repositories:
            language_count[repo['primary_language']] += 1

        sorted_languages = sorted(language_count.items(), key=lambda x: x[1], reverse=True)
        return [lang for lang, count in sorted_languages[:top_n]]

    def analyze_rq07(self, repositories: List[Dict]) -> Dict:
        """
        Análise específica para RQ07 (BÔNUS)
        Compara linguagens populares vs outras linguagens

        Args:
            repositories: Lista de repositórios

        Returns:
            Dicionário com análise comparativa
        """
        popular_languages = self.get_popular_languages(repositories, 5)

        popular_repos = []
        other_repos = []

        for repo in repositories:
            if repo['primary_language'] in popular_languages:
                popular_repos.append(repo)
            else:
                other_repos.append(repo)

        def calc_medians(repos_list):
            if not repos_list:
                return {'median_prs': 0, 'median_releases': 0, 'median_days_update': 0}

            prs = sorted([r['merged_pull_requests'] for r in repos_list])
            releases = sorted([r['total_releases'] for r in repos_list])
            days = sorted([r['days_since_update'] for r in repos_list])

            return {
                'median_prs': prs[len(prs) // 2],
                'median_releases': releases[len(releases) // 2],
                'median_days_update': days[len(days) // 2],
                'count': len(repos_list)
            }

        popular_stats = calc_medians(popular_repos)
        other_stats = calc_medians(other_repos)

        return {
            'popular_languages': popular_languages,
            'popular_stats': popular_stats,
            'other_stats': other_stats,
            'by_language': self.analyze_by_language(repositories)
        }

    def save_to_csv(self, repositories: List[Dict], filename: str = 'github_repositories.csv'):
        """
        Salva os dados dos repositórios em arquivo CSV

        Args:
            repositories: Lista de repositórios
            filename: Nome do arquivo CSV
        """
        if not repositories:
            print("Nenhum dado para salvar.")
            return

        fieldnames = repositories[0].keys()

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(repositories)

        print(f"Dados salvos em {filename}")

    def print_summary(self, repositories: List[Dict]):
        """
        Imprime um resumo dos dados coletados

        Args:
            repositories: Lista de repositórios
        """
        if not repositories:
            print("Nenhum dado para resumir.")
            return

        print("\n" + "=" * 50)
        print("RESUMO DOS DADOS COLETADOS")
        print("=" * 50)

        total_repos = len(repositories)
        print(f"Total de repositórios: {total_repos}")

        ages = [repo['age_days'] for repo in repositories]
        merged_prs = [repo['merged_pull_requests'] for repo in repositories]
        releases = [repo['total_releases'] for repo in repositories]
        days_since_updates = [repo['days_since_update'] for repo in repositories]

        print(f"\nIdade (RQ01):")
        print(f"  Mediana: {sorted(ages)[len(ages) // 2]} dias")
        print(f"  Mín: {min(ages)} dias, Máx: {max(ages)} dias")

        print(f"\nPull Requests Aceitas (RQ02):")
        print(f"  Mediana: {sorted(merged_prs)[len(merged_prs) // 2]}")
        print(f"  Mín: {min(merged_prs)}, Máx: {max(merged_prs)}")

        print(f"\nReleases (RQ03):")
        print(f"  Mediana: {sorted(releases)[len(releases) // 2]}")
        print(f"  Mín: {min(releases)}, Máx: {max(releases)}")

        print(f"\nDias desde última atualização (RQ04):")
        print(f"  Mediana: {sorted(days_since_updates)[len(days_since_updates) // 2]} dias")
        print(f"  Mín: {min(days_since_updates)} dias, Máx: {max(days_since_updates)} dias")

        languages = {}
        for repo in repositories:
            lang = repo['primary_language']
            languages[lang] = languages.get(lang, 0) + 1

        print(f"\nLinguagens mais populares (RQ05):")
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        for lang, count in sorted_languages[:10]:
            print(f"  {lang}: {count} repositórios")

        closed_ratios = [repo['closed_issues_ratio'] for repo in repositories if repo['total_issues'] > 0]
        if closed_ratios:
            print(f"\nPercentual de issues fechadas (RQ06):")
            print(f"  Mediana: {sorted(closed_ratios)[len(closed_ratios) // 2]:.2f}%")

        print(f"\n" + "=" * 50)
        print("RQ07 - ANÁLISE POR LINGUAGEM (BÔNUS)")
        print("=" * 50)

        rq07_analysis = self.analyze_rq07(repositories)

        print(f"\nLinguagens mais populares:")
        for lang in rq07_analysis['popular_languages']:
            print(f"  - {lang}")

        popular_stats = rq07_analysis['popular_stats']
        other_stats = rq07_analysis['other_stats']

        print(f"\nComparação: Linguagens Populares vs Outras")
        print(f"┌─────────────────────────────┬─────────────┬─────────────┐")
        print(f"│ Métrica                     │ Populares   │ Outras      │")
        print(f"├─────────────────────────────┼─────────────┼─────────────┤")
        print(f"│ Repositórios                │ {popular_stats['count']:11d} │ {other_stats['count']:11d} │")
        print(f"│ Mediana PRs Aceitas (RQ02)  │ {popular_stats['median_prs']:11d} │ {other_stats['median_prs']:11d} │")
        print(
            f"│ Mediana Releases (RQ03)     │ {popular_stats['median_releases']:11d} │ {other_stats['median_releases']:11d} │")
        print(
            f"│ Mediana Dias Update (RQ04)  │ {popular_stats['median_days_update']:11d} │ {other_stats['median_days_update']:11d} │")
        print(f"└─────────────────────────────┴─────────────┴─────────────┘")

        print(f"\nDetalhamento por linguagem (Top 10):")
        by_language = rq07_analysis['by_language']

        sorted_langs = sorted(by_language.items(), key=lambda x: x[1]['count'], reverse=True)

        print(f"┌─────────────┬─────┬─────────┬──────────┬──────────────┐")
        print(f"│ Linguagem   │ Qty │ Med PRs │ Med Rels │ Med Days Upd │")
        print(f"├─────────────┼─────┼─────────┼──────────┼──────────────┤")

        for lang, stats in sorted_langs[:10]:
            lang_short = lang[:11] if len(lang) <= 11 else lang[:8] + "..."
            print(
                f"│ {lang_short:<11} │ {stats['count']:3d} │ {stats['median_merged_prs']:7d} │ {stats['median_releases']:8d} │ {stats['median_days_since_update']:12d} │")

        print(f"└─────────────┴─────┴─────────┴──────────┴──────────────┘")

        print(f"\nConclusão RQ07:")
        if popular_stats['median_prs'] > other_stats['median_prs']:
            print("✓ Linguagens populares recebem MAIS contribuições externas")
        else:
            print("✗ Linguagens populares recebem MENOS contribuições externas")

        if popular_stats['median_releases'] > other_stats['median_releases']:
            print("✓ Linguagens populares lançam MAIS releases")
        else:
            print("✗ Linguagens populares lançam MENOS releases")

        if popular_stats['median_days_update'] < other_stats['median_days_update']:
            print("✓ Linguagens populares são atualizadas com MAIS frequência")
        else:
            print("✗ Linguagens populares são atualizadas com MENOS frequência")


def main():
    """
    Função principal - Lab01S01
    """
    """
    Criar o token com scopo de:
        - Repo
        - User
        - Project
    """
    with open("token.txt") as f:
        TOKEN = f.read().strip()


    analyzer = GitHubAnalyzer(TOKEN)

    repositories = analyzer.collect_repositories(100)

    analyzer.save_to_csv(repositories, 'lab01s01_repositories.csv')

    analyzer.print_summary(repositories)


if __name__ == "__main__":
    main()