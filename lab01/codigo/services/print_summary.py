import os
from typing import Dict, List
from collections import defaultdict

import os
import matplotlib.pyplot as plt

# Import das classes de gráficos
from charts.rq01_age_charts import RQ01AgeCharts
from charts.rq02_prs_charts import RQ02PRsCharts
from charts.rq03_releases_charts import RQ03ReleasesCharts
from charts.rq04_updates_charts import RQ04UpdatesCharts
from charts.rq05_languages_charts import RQ05LanguagesCharts
from charts.rq06_issues_charts import RQ06IssuesCharts

class CalculateMetrics:
    @staticmethod
    def print_summary(self, repositories: List[Dict], output_md_filename: str = None):
        """
        Imprime um resumo dos dados coletados e salva em um arquivo .md

        Args:
            repositories: Lista de repositórios
            output_md_filename: Nome do arquivo .md para salvar o resumo (opcional)
        """
        if not repositories:
            print("Nenhum dado para resumir.")
            return

        output_lines = []
        def add_line(line: str):
            print(line)
            output_lines.append(line + "\n")

        # Dados básicos
        ages = [repo['age_days'] for repo in repositories]
        merged_prs = [repo['merged_pull_requests'] for repo in repositories]
        releases = [repo['total_releases'] for repo in repositories]
        days_since_updates = [repo['days_since_update'] for repo in repositories]
        closed_ratios = [repo['closed_issues_ratio'] for repo in repositories if repo['total_issues'] > 0]

        # Diretório de saída dos gráficos
        base_dir = './relatorios/graficos'
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Geração dos gráficos com as classes
        rq01_hist_path, rq01_box_path = RQ01AgeCharts.generate(ages, base_dir)
        rq02_hist_path, rq02_box_path = RQ02PRsCharts.generate(merged_prs, base_dir)
        rq03_hist_path, rq03_box_path = RQ03ReleasesCharts.generate(releases, base_dir)
        rq04_hist_path, rq04_box_path = RQ04UpdatesCharts.generate(days_since_updates, base_dir)

        languages = {}
        for repo in repositories:
            lang = repo['primary_language']
            languages[lang] = languages.get(lang, 0) + 1
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        top_languages = sorted_languages[:10]
        rq05_bar_path, rq05_pie_path = RQ05LanguagesCharts.generate(top_languages, base_dir)

        if closed_ratios:
            rq06_hist_path, rq06_box_path = RQ06IssuesCharts.generate(closed_ratios, base_dir)
        else:
            rq06_hist_path = rq06_box_path = None
        
        # Início da impressão do resumo
        add_line("\n" + "=" * 50)
        add_line("RESUMO DOS DADOS COLETADOS")
        add_line("=" * 50)

        # RQ01: Idade dos repositórios
        add_line(f"\nIdade (RQ01):")
        median_age = sorted(ages)[len(ages) // 2]
        add_line(f"  Mediana: {median_age} dias")
        add_line(f"  Mín: {min(ages)} dias, Máx: {max(ages)} dias")
        add_line("### RQ01 - Idade dos Repositórios (Histograma)\n")
        add_line(f"![RQ01 Hist]({rq01_hist_path})\n")
        add_line("### RQ01 - Idade dos Repositórios (Box Plot)\n")
        add_line(f"![RQ01 Box]({rq01_box_path})\n")
                
        # RQ02: Pull Requests Aceitas
        add_line(f"\nPull Requests Aceitas (RQ02):")
        median_prs = sorted(merged_prs)[len(merged_prs) // 2]
        add_line(f"  Mediana: {median_prs}")
        add_line(f"  Mín: {min(merged_prs)}, Máx: {max(merged_prs)}")
        add_line("### RQ02 - Pull Requests Aceitas (Histograma)\n")
        add_line(f"![RQ02 Hist]({rq02_hist_path})\n")
        add_line("### RQ02 - Pull Requests Aceitas (Box Plot)\n")
        add_line(f"![RQ02 Box]({rq02_box_path})\n")
        
        # RQ03: Releases
        add_line(f"\nReleases (RQ03):")
        median_releases = sorted(releases)[len(releases) // 2]
        add_line(f"  Mediana: {median_releases}")
        add_line(f"  Mín: {min(releases)}, Máx: {max(releases)}")
        add_line("### RQ03 - Releases (Histograma)\n")
        add_line(f"![RQ03 Hist]({rq03_hist_path})\n")
        add_line("### RQ03 - Releases (Box Plot)\n")
        add_line(f"![RQ03 Box]({rq03_box_path})\n")
        
        # RQ04: Dias desde a última atualização
        add_line(f"\nDias desde última atualização (RQ04):")
        median_days_since_updates = sorted(days_since_updates)[len(days_since_updates) // 2]
        add_line(f"  Mediana: {median_days_since_updates} dias")
        add_line(f"  Mín: {min(days_since_updates)} dias, Máx: {max(days_since_updates)} dias")
        add_line("### RQ04 - Dias Desde a Última Atualização (Histograma)\n")
        add_line(f"![RQ04 Hist]({rq04_hist_path})\n")
        add_line("### RQ04 - Dias Desde a Última Atualização (Box Plot)\n")
        add_line(f"![RQ04 Box]({rq04_box_path})\n")
            
        # RQ05: Linguagens mais populares
        add_line(f"\nLinguagens mais populares (RQ05):")
        top_languages = sorted_languages[:10]
        for lang, count in top_languages:
            add_line(f"  {lang}: {count} repositórios")   
        add_line("### RQ05 - Linguagens Mais Populares (Barras)\n")
        add_line(f"![RQ05 Barras]({rq05_bar_path})\n")
        add_line("### RQ05 - Linguagens Mais Populares (Pizza)\n")
        add_line(f"![RQ05 Pizza]({rq05_pie_path})\n")  
            
        if closed_ratios:
            # RQ06: Percentual de issues fechadas
            add_line(f"\nPercentual de issues fechadas (RQ06):")
            median_closed_ratios = sorted(closed_ratios)[len(closed_ratios) // 2]
            add_line(f"  Mediana: {median_closed_ratios:.2f}%")

        add_line("\n" + "=" * 50)
        add_line("RQ07 - ANÁLISE POR LINGUAGEM (BÔNUS)")
        add_line("=" * 50)
        add_line("### RQ06 - Percentual de Issues Fechadas (Histograma)\n")
        add_line(f"![RQ06 Hist]({rq06_hist_path})\n")
        add_line("### RQ06 - Percentual de Issues Fechadas (Box Plot)\n")
        add_line(f"![RQ06 Box]({rq06_box_path})\n")

        rq07_analysis = self.analyze_rq07(repositories)

        add_line(f"\nLinguagens mais populares:")
        for lang in rq07_analysis['popular_languages']:
            add_line(f"  - {lang}")

        popular_stats = rq07_analysis['popular_stats']
        other_stats = rq07_analysis['other_stats']

        add_line(f"\nComparação: Linguagens Populares vs Outras")
        add_line(f"┌─────────────────────────────┬─────────────┬─────────────┐")
        add_line(f"│ Métrica                     │ Populares   │ Outras      │")
        add_line(f"├─────────────────────────────┼─────────────┼─────────────┤")
        add_line(f"│ Repositórios                │ {popular_stats['count']:11d} │ {other_stats['count']:11d} │")
        add_line(f"│ Mediana PRs Aceitas (RQ02)  │ {popular_stats['median_prs']:11d} │ {other_stats['median_prs']:11d} │")
        add_line(
            f"│ Mediana Releases (RQ03)     │ {popular_stats['median_releases']:11d} │ {other_stats['median_releases']:11d} │")
        add_line(
            f"│ Mediana Dias Update (RQ04)  │ {popular_stats['median_days_update']:11d} │ {other_stats['median_days_update']:11d} │")
        add_line(f"└─────────────────────────────┴─────────────┴─────────────┘")

        add_line(f"\nDetalhamento por linguagem (Top 10):")
        by_language = rq07_analysis['by_language']

        sorted_langs = sorted(by_language.items(), key=lambda x: x[1]['count'], reverse=True)

        add_line(f"┌─────────────┬─────┬─────────┬──────────┬──────────────┐")
        add_line(f"│ Linguagem   │ Qty │ Med PRs │ Med Rels │ Med Days Upd │")
        add_line(f"├─────────────┼─────┼─────────┼──────────┼──────────────┤")

        for lang, stats in sorted_langs[:10]:
            lang_short = lang[:11] if len(lang) <= 11 else lang[:8] + "..."
            add_line(
                f"│ {lang_short:<11} │ {stats['count']:3d} │ {stats['median_merged_prs']:7d} │ {stats['median_releases']:8d} │ {stats['median_days_since_update']:12d} │")

        add_line(f"└─────────────┴─────┴─────────┴──────────┴──────────────┘")

        add_line(f"\nConclusão RQ07:")
        if popular_stats['median_prs'] > other_stats['median_prs']:
            add_line("✓ Linguagens populares recebem MAIS contribuições externas")
        else:
            add_line("✗ Linguagens populares recebem MENOS contribuições externas")

        if popular_stats['median_releases'] > other_stats['median_releases']:
            add_line("✓ Linguagens populares lançam MAIS releases")
        else:
            add_line("✗ Linguagens populares lançam MENOS releases")

        if popular_stats['median_days_update'] < other_stats['median_days_update']:
            add_line("✓ Linguagens populares são atualizadas com MAIS frequência")
        else:
            add_line("✗ Linguagens populares são atualizadas com MENOS frequência")    
            
        if output_md_filename:
            # Salvar o conteúdo em um arquivo .md
            with open(output_md_filename, "w", encoding="utf-8") as md_file:
                md_file.writelines(output_lines)
            print(f"\nResumo salvo em {output_md_filename}")

                
               

                

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
                    return {'median_prs': 0, 'median_releases': 0, 'median_days_update': 0, 'count': 0}

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
        
        
        