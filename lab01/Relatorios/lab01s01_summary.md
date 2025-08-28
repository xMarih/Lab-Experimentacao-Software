
==================================================
RESUMO DOS DADOS COLETADOS
==================================================

Idade (RQ01):
  Mediana: 3056 dias
  Mín: 63 dias, Máx: 6344 dias
### RQ01 - Idade dos Repositórios (Histograma)

![RQ01 Hist](./lab01/relatorios/graficos\rq01_idade_hist.png)

### RQ01 - Idade dos Repositórios (Box Plot)

![RQ01 Box](./lab01/relatorios/graficos\rq01_idade_box.png)


Pull Requests Aceitas (RQ02):
  Mediana: 710
  Mín: 0, Máx: 86225
### RQ02 - Pull Requests Aceitas (Histograma)

![RQ02 Hist](./lab01/relatorios/graficos\rq02_prs_hist.png)

### RQ02 - Pull Requests Aceitas (Box Plot)

![RQ02 Box](./lab01/relatorios/graficos\rq02_prs_box.png)


Releases (RQ03):
  Mediana: 36
  Mín: 0, Máx: 1000
### RQ03 - Releases (Histograma)

![RQ03 Hist](./lab01/relatorios/graficos\rq03_releases_hist.png)

### RQ03 - Releases (Box Plot)

![RQ03 Box](./lab01/relatorios/graficos\rq03_releases_box.png)


Dias desde última atualização (RQ04):
  Mediana: 0 dias
  Mín: 0 dias, Máx: 4 dias
### RQ04 - Dias Desde a Última Atualização (Histograma)

![RQ04 Hist](./lab01/relatorios/graficos\rq04_dias_hist.png)

### RQ04 - Dias Desde a Última Atualização (Box Plot)

![RQ04 Box](./lab01/relatorios/graficos\rq04_dias_box.png)


Linguagens mais populares (RQ05):
  Python: 189 repositórios
  TypeScript: 156 repositórios
  JavaScript: 130 repositórios
  Unknown: 103 repositórios
  Go: 73 repositórios
  Java: 50 repositórios
  C++: 48 repositórios
  Rust: 44 repositórios
  C: 25 repositórios
  Jupyter Notebook: 22 repositórios
### RQ05 - Linguagens Mais Populares (Barras)

![RQ05 Barras](./lab01/relatorios/graficos\rq05_linguagens_bar.png)

### RQ05 - Linguagens Mais Populares (Pizza)

![RQ05 Pizza](./lab01/relatorios/graficos\rq05_linguagens_pie.png)


Percentual de issues fechadas (RQ06):
  Mediana: 86.57%

==================================================
RQ07 - ANÁLISE POR LINGUAGEM (BÔNUS)
==================================================
### RQ06 - Percentual de Issues Fechadas (Histograma)

![RQ06 Hist](./lab01/relatorios/graficos\rq06_issues_hist.png)

### RQ06 - Percentual de Issues Fechadas (Box Plot)

![RQ06 Box](./lab01/relatorios/graficos\rq06_issues_box.png)


Linguagens mais populares:
  - Python
  - TypeScript
  - JavaScript
  - Unknown
  - Go

Comparação: Linguagens Populares vs Outras
┌─────────────────────────────┬─────────────┬─────────────┐
│ Métrica                     │ Populares   │ Outras      │
├─────────────────────────────┼─────────────┼─────────────┤
│ Repositórios                │         651 │         349 │
│ Mediana PRs Aceitas (RQ02)  │         715 │         681 │
│ Mediana Releases (RQ03)     │          42 │          31 │
│ Mediana Dias Update (RQ04)  │           0 │           0 │
└─────────────────────────────┴─────────────┴─────────────┘

Detalhamento por linguagem (Top 10):
┌─────────────┬─────┬─────────┬──────────┬──────────────┐
│ Linguagem   │ Qty │ Med PRs │ Med Rels │ Med Days Upd │
├─────────────┼─────┼─────────┼──────────┼──────────────┤
│ Python      │ 189 │     548 │       23 │            0 │
│ TypeScript  │ 156 │    2143 │      147 │            0 │
│ JavaScript  │ 130 │     551 │       34 │            0 │
│ Unknown     │ 103 │     129 │        0 │            0 │
│ Go          │  73 │    1690 │      124 │            0 │
│ Java        │  50 │     713 │       44 │            0 │
│ C++         │  48 │     934 │       60 │            0 │
│ Rust        │  44 │    2174 │       87 │            0 │
│ C           │  25 │     113 │       32 │            0 │
│ Jupyter ... │  22 │     147 │        0 │            0 │
└─────────────┴─────┴─────────┴──────────┴──────────────┘

Conclusão RQ07:
✓ Linguagens populares recebem MAIS contribuições externas
✓ Linguagens populares lançam MAIS releases
✗ Linguagens populares são atualizadas com MENOS frequência
