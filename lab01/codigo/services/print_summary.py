import os
from typing import Dict, List
from collections import defaultdict

import os
import matplotlib.pyplot as plt

# Import das classes de gráficos
from plots.rq01_age_charts import RQ01AgeCharts
from plots.rq02_prs_charts import RQ02PRsCharts
from plots.rq03_releases_charts import RQ03ReleasesCharts
from plots.rq04_updates_charts import RQ04UpdatesCharts
from plots.rq05_languages_charts import RQ05LanguagesCharts
from plots.rq06_issues_charts import RQ06IssuesCharts

from plots.rq01_compare_idade import RQ01CompareAgeCharts

class CalculateMetrics:
    @staticmethod
    def print_summary(repositories: List[Dict], output_md_filename: str = None):
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
        
        # Dados básicos para todos os repositórios
        ages = [repo['age_days'] for repo in repositories]
        merged_prs = [repo['merged_pull_requests'] for repo in repositories]
        releases = [repo['total_releases'] for repo in repositories]
        days_since_updates = [repo['days_since_update'] for repo in repositories]
        closed_ratios = [repo['closed_issues_ratio'] for repo in repositories if repo['total_issues'] > 0]

        # Dados básicos para os 10 primeiros repositórios
        top_10_repos = repositories[:10]  # Pega os 10 primeiros repositórios
        top_10_ages = [repo['age_days'] for repo in top_10_repos]
        top_10_merged_prs = [repo['merged_pull_requests'] for repo in top_10_repos]
        top_10_releases = [repo['total_releases'] for repo in top_10_repos]
        top_10_days_since_updates = [repo['days_since_update'] for repo in top_10_repos]
        top_10_closed_ratios = [repo['closed_issues_ratio'] for repo in top_10_repos if repo['total_issues'] > 0]

        languages = {}
        for repo in repositories:
            lang = repo['primary_language']
            languages[lang] = languages.get(lang, 0) + 1
        sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        top_languages = sorted_languages[:10]
        
        # Diretório de saída dos gráficos
        base_dir = './lab01/relatorios/graficos'
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # Geração dos gráficos para todos os repos
        rq01_hist_path, rq01_box_path = RQ01AgeCharts.generate(ages, base_dir, 'AllRepos')
        rq02_hist_path, rq02_box_path = RQ02PRsCharts.generate(merged_prs, base_dir, 'AllRepos')
        rq03_hist_path, rq03_box_path = RQ03ReleasesCharts.generate(releases, base_dir, 'AllRepos')
        rq04_hist_path, rq04_box_path = RQ04UpdatesCharts.generate(days_since_updates, base_dir, 'AllRepos')
        rq05_bar_path, rq05_pie_path = RQ05LanguagesCharts.generate(top_languages, base_dir, 'AllRepos')
        
        # Geração dos gráficos para top10 os repos
        rq01_hist_top10, rq01_box_top10 = RQ01AgeCharts.generate(top_10_ages, base_dir, 'Top10Repos')
        rq02_hist_top10, rq02_box_top10 = RQ02PRsCharts.generate(top_10_merged_prs, base_dir, 'Top10Repos')
        rq03_hist_top10, rq03_box_top10 = RQ03ReleasesCharts.generate(top_10_releases, base_dir, 'Top10Repos')
        rq04_hist_top10, rq04_box_top10 = RQ04UpdatesCharts.generate(top_10_days_since_updates, base_dir, 'Top10Repos')

        rq06_hist_path, rq06_box_path = RQ06IssuesCharts.generate(closed_ratios, base_dir, 'AllRepos')
        rq06_hist_top10, rq06_box_top10 = RQ06IssuesCharts.generate(top_10_closed_ratios, base_dir, 'Top10Repos')
            
        rq07_analysis = CalculateMetrics.analyze_rq07(repositories)


        rq01_compare_idade = RQ01CompareAgeCharts.generate(ages, top_10_ages, base_dir)

        # Início da impressão do resumo
        add_line("\n" + "=" * 50)
        add_line("# RESUMO DOS DADOS COLETADOS")
        add_line("=" * 50)
        
    #####################################################################################
        # RQ01: Idade dos repositórios
        add_line(f"\n## RQ 01. Sistemas populares são maduros/antigos?")
        add_line(f"\n### Métrica: idade do repositório")
        
        add_line(f"\n**Para todos os repositórios:**")
        median_age = sorted(ages)[len(ages) // 2]
        add_line(f"  Mediana: {median_age} dias")
        add_line(f"  Mín: {min(ages)} dias, Máx: {max(ages)} dias")
        add_line(f"![RQ01 Hist]({rq01_hist_path})\n")
        add_line(f"![RQ01 Box]({rq01_box_path})\n")
        
        add_line(f"\n**Para top10 repositórios:**")
        top10_median_age = sorted(top_10_ages)[len(top_10_ages) // 2]
        add_line(f"  Mediana: {top10_median_age} dias")
        add_line(f"  Mín: {min(top_10_ages)} dias, Máx: {max(top_10_ages)} dias")
        add_line(f"![RQ01 Hist]({rq01_hist_top10})\n")
        add_line(f"![RQ01 Box]({rq01_box_top10})\n")
        
                
        add_line(f"\n**Comparativo:**")
        add_line(f"![RQ01 Compare]({rq01_compare_idade})\n")

    #####################################################################################      
        # RQ02: Pull Requests Aceitas
        add_line(f"\n## RQ 02. Sistemas populares recebem muita contribuição externa?")
        add_line(f"\n### Métrica: Pull Requests Aceitas")

        add_line(f"\n**Para todos os repositórios:**")
        median_prs = sorted(merged_prs)[len(merged_prs) // 2]
        add_line(f"  Mediana: {median_prs}")
        add_line(f"  Mín: {min(merged_prs)}, Máx: {max(merged_prs)}")
        add_line(f"![RQ02 Hist]({rq02_hist_path})\n")
        add_line(f"![RQ02 Box]({rq02_box_path})\n")
        
        add_line(f"\n**Para top10 repositórios:**")
        top10_median_prs = sorted(top_10_merged_prs)[len(top_10_merged_prs) // 2]
        add_line(f"  Mediana: {top10_median_prs}")
        add_line(f"  Mín: {min(top_10_merged_prs)}, Máx: {max(top_10_merged_prs)}")
        add_line(f"![RQ02 Hist]({rq02_hist_top10})\n")
        add_line(f"![RQ02 Box]({rq02_box_top10})\n")
        
    #####################################################################################
        # RQ03: Releases
        add_line(f"\n## RQ 03. Sistemas populares lançam releases com frequência? ")
        add_line(f"\n### Métrica: Releases")

        add_line(f"\n**Para todos os repositórios:**")
        median_releases = sorted(releases)[len(releases) // 2]
        add_line(f"  Mediana: {median_releases}")
        add_line(f"  Mín: {min(releases)}, Máx: {max(releases)}")
        add_line(f"![RQ03 Hist]({rq03_hist_path})\n")
        add_line(f"![RQ03 Box]({rq03_box_path})\n")
        
        add_line(f"\n**Para top10 repositórios:**")
        top10_median_releases = sorted(top_10_releases)[len(top_10_releases) // 2]
        add_line(f"  Mediana: {top10_median_releases}")
        add_line(f"  Mín: {min(top_10_releases)}, Máx: {max(top_10_releases)}")
        add_line(f"![RQ03 Hist]({rq03_hist_top10})\n")
        add_line(f"![RQ03 Box]({rq03_box_top10})\n")

    #####################################################################################
        # RQ04: Dias desde a última atualização
        add_line(f"\n## RQ 04. Sistemas populares são atualizados com frequência")
        add_line(f"\n### Métrica: Dias desde a última atualização")
        
        add_line(f"\n**Para todos os repositórios:**")
        median_days_since_updates = sorted(days_since_updates)[len(days_since_updates) // 2]
        add_line(f"  Mediana: {median_days_since_updates} dias")
        add_line(f"  Mín: {min(days_since_updates)} dias, Máx: {max(days_since_updates)} dias")
        add_line(f"![RQ04 Hist]({rq04_hist_path})\n")
        add_line(f"![RQ04 Box]({rq04_box_path})\n")
        
        add_line(f"\n**Para top10 repositórios:**")
        top10_median_days_since_updates = sorted(top_10_days_since_updates)[len(top_10_days_since_updates) // 2]
        add_line(f"  Mediana: {top10_median_days_since_updates} dias")
        add_line(f"  Mín: {min(top_10_days_since_updates)} dias, Máx: {max(top_10_days_since_updates)} dias")
        add_line(f"![RQ04 Hist]({rq04_hist_top10})\n")
        add_line(f"![RQ04 Box]({rq04_box_top10})\n")

    #####################################################################################
        # RQ05: Linguagens mais populares
        add_line(f"\n## RQ 05. Sistemas populares são escritos nas linguagens mais populares?")
        add_line(f"\n### Linguagem primária de cada um desses repositórios")
        
        top_languages = sorted_languages[:10]
        for lang, count in top_languages:
            add_line(f"  {lang}: {count} repositórios")   
        add_line(f"![RQ05 Barras]({rq05_bar_path})\n")
        add_line(f"![RQ05 Pizza]({rq05_pie_path})\n")  
            
    #####################################################################################
        # RQ06: Percentual de issues fechadas       
        add_line(f"\n## RQ 06. Sistemas populares possuem um alto percentual de issues fechadas? ")
        add_line(f"\n### Razão entre número de issues fechadas pelo total de issues")
        median_closed_ratios = sorted(closed_ratios)[len(closed_ratios) // 2]

        add_line(f"\n**Para todos os repositórios:**")
        add_line(f"  Mediana: {median_closed_ratios:.2f}%")
        add_line(f"  Mín: {min(closed_ratios):.2f}%, Máx: {max(closed_ratios):.2f}%")
        add_line(f"![RQ06 Hist]({rq06_hist_path})\n")
        add_line(f"![RQ06 Box]({rq06_box_path})\n")

        add_line(f"\n**Para top10 repositórios:**")
        top10_median_closed_ratios = sorted(top_10_closed_ratios)[len(top_10_closed_ratios) // 2]
        add_line(f"  Mediana: {top10_median_closed_ratios:.2f}%")
        add_line(f"  Mín: {min(top_10_closed_ratios):.2f}%, Máx: {max(top_10_closed_ratios):.2f}%")
        add_line(f"![RQ06 Hist]({rq06_hist_top10})\n")
        add_line(f"![RQ06 Box]({rq06_box_top10})\n")


    #####################################################################################
        add_line(f"\n## RQ07 - ANÁLISE POR LINGUAGEM")
        add_line(f"\n### Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência? ")

        add_line(f"\nLinguagens mais populares:")
        for lang in rq07_analysis['popular_languages']:
            add_line(f"  - {lang}")

        popular_stats = rq07_analysis['popular_stats']
        other_stats = rq07_analysis['other_stats']

        add_line(f"\nComparação: Linguagens Populares vs Outras")
        add_line(f"| Métrica                    | Populares   | Outras      |")
        add_line(f"| -------------------------- | ----------- | ----------- |")
        add_line(f"| Repositórios               | {popular_stats['count']:11d} | {other_stats['count']:11d} |")
        add_line(f"| Mediana PRs Aceitas (RQ02) | {popular_stats['median_prs']:11d} | {other_stats['median_prs']:11d} |")
        add_line(f"| Mediana Releases (RQ03)    | {popular_stats['median_releases']:11d} | {other_stats['median_releases']:11d} |")
        add_line(f"| Mediana Dias Update (RQ04) | {popular_stats['median_days_update']:11d} | {other_stats['median_days_update']:11d} |")

        by_language = rq07_analysis['by_language']
        sorted_langs = sorted(by_language.items(), key=lambda x: x[1]['count'], reverse=True)

        add_line("\nDetalhamento por linguagem (Top 10):")
        add_line("| Linguagem   | Qty | Med PRs | Med Rels | Med Days Upd |")
        add_line("| ----------- | --- | ------- | -------- | ------------ |")



        for lang, stats in sorted_langs[:10]:
            lang_short = lang[:11] if len(lang) <= 11 else lang[:8] + "..."
            add_line(
                f"| {lang_short:<11} | {stats['count']:3d} | {stats['median_merged_prs']:7d} | {stats['median_releases']:8d} | {stats['median_days_since_update']:12d} |")

        add_line(f"\nConclusão")
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
            
    @staticmethod
    def analyze_by_language(repositories: List[Dict]) -> Dict:
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
        
    @staticmethod
    def get_popular_languages(repositories: List[Dict], top_n: int = 5) -> List[str]:
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

    @staticmethod
    def analyze_rq07(repositories: List[Dict]) -> Dict:
            """
            Análise específica para RQ07 (BÔNUS)
            Compara linguagens populares vs outras linguagens

            Args:
                repositories: Lista de repositórios

            Returns:
                Dicionário com análise comparativa
            """
            popular_languages = CalculateMetrics.get_popular_languages(repositories, 5)

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
                'by_language': CalculateMetrics.analyze_by_language(repositories)
            }