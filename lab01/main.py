import csv
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
from services.git import GitHubService

class MetricsAnalyzer:
    def __init__(self):
        pass

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
    with open("token.txt") as f:
        TOKEN = f.read().strip()

    # Inicializar serviços
    github_service = GitHubService(TOKEN)
    metrics_analyzer = MetricsAnalyzer()

    # Coletar repositórios
    repositories = github_service.collect_repositories(100)

    # Salvar dados
    metrics_analyzer.save_to_csv(repositories, './files/lab01s01_repositories.csv')

    # Exibir análise
    metrics_analyzer.print_summary(repositories)

if __name__ == "__main__":
    main()