# Relatório final - Características de repositórios populares

GRUPO: Izabela Cecilia Silva Barbosa, Lucas Machado de Oliveira Andrade, Mariana Eliza Alves Costa e Vitor Fernandes de Souza

## Introdução

O cenário atual de desenvolvimento de software demanda evidências empíricas para apoiar a tomada de decisões. Neste contexto, realizamos uma investigação sistemática sobre práticas de desenvolvimento, utilizando métodos científicos para coletar e analisar dados relevantes para a comunidade de engenharia de software.

## HIPÓTESES INFORMAIS
### RQ 01. Sistemas populares são maduros/antigos?
Métrica: idade do repositório (calculado a partir da data de sua criação)
Hipótese Informal: A maturidade é um fator crucial para a popularidade. Acredita-se que repositórios populares são, em média, mais antigos. Eles tiveram tempo para evoluir, construir uma comunidade, e acumular estrelas ao longo dos anos. Portanto, a idade mediana dos repositórios na amostra será significativamente alta (por exemplo, mais de 3 anos).

### RQ 02. Sistemas populares recebem muita contribuição externa?
Métrica: total de pull requests aceitas
Hipótese Informal: Repositórios populares com uma comunidade ativa e que recebem muitas pull requests aceitas (contribuições externas) possuem mais estrelas. A alta visibilidade e o grande número de estrelas atraem novos contribuidores, resultando em um alto número de pull requests aceitas por repositório.

### RQ 03. Sistemas populares lançam releases com frequência?
Métrica: total de releases
Hipótese Informal: A frequência de releases é um indicativo de um ciclo de desenvolvimento ativo e de um produto em constante evolução. Repositórios populares tendem a ter um processo de entrega contínua mais robusto, com um número acima da média de releases, o que mantém os usuários engajados e os projetos atualizados.

### RQ 04. Sistemas populares são atualizados com frequência?
Métrica: tempo até a última atualização (calculado a partir da data de última atualização)
Hipótese Informal: Projetos populares são ativamente mantidos. Espera-se que o tempo desde a última atualização seja baixo da média, indicando que a base de código está em constante desenvolvimento. Repositórios com longos períodos sem atualizações, mesmo que sejam populares, podem estar em fase de hibernação ou abandonados.

### RQ 05. Sistemas populares são escritos nas linguagens mais populares?
Métrica: linguagem primária de cada um desses repositórios
Hipótese Informal: A escolha da linguagem de programação influencia diretamente a visibilidade e a popularidade. As linguagens mais populares (como JavaScript, Python, Java, etc.) têm grandes comunidades de desenvolvedores, o que facilita o aumento de estrelas e contribuições. Portanto, a maioria dos repositórios populares na amostra será escrita em uma das linguagens mais usadas no mercado.

### RQ 06. Sistemas populares possuem um alto percentual de issues fechadas?
Métrica: razão entre número de issues fechadas pelo total de issues 
Hipótese Informal: Uma taxa acima da média da amostra de issues fechadas indica que o projeto é bem gerenciado, com problemas e bugs sendo resolvidos de forma eficiente. Isso demonstra confiabilidade para a comunidade. Espera-se que a maioria dos repositórios populares tenha um percentual elevado de issues fechadas, mostrando que são reativos às demandas dos usuários.

### RQ 07: Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência? 
Hipótese Informal: Projetos desenvolvidos em linguagens de programação mais populares (como Python, JavaScript, Java, etc.) tendem a ter uma comunidade de desenvolvedores maior. Essa base de usuários mais ampla e ativa leva a um ciclo de desenvolvimento mais dinâmico.

## Resultados

### RQ 01. Sistemas populares são maduros/antigos?

Métrica: idade do repositório (calculado a partir da data de sua criação)
Idade (RQ01):
  Mediana: 3320 dias
  Mín: 211 dias, Máx: 5835 dias
  ![RQ01 - Idade dos Repositórios](./graficos/rq01_idade_hist.png)

### RQ 02. Sistemas populares recebem muita contribuição externa?

Métrica: total de pull requests aceitas
Pull Requests Aceitas (RQ02):
  Mediana: 1872
  Mín: 0, Máx: 65576
  ![RQ02 - Pull Request Aceitas](./graficos/rq02_prs_box.png)
  

### RQ 03. Sistemas populares lançam releases com frequência?

Métrica: total de releases
Releases (RQ03):
  Mediana: 17
  Mín: 0, Máx: 1000
  ![RQ02 - Pull Request Aceitas](./graficos/rq02_prs_box.png)

### RQ 04. Sistemas populares são atualizados com frequência?

Métrica: tempo até a última atualização 
Dias desde última atualização (RQ04):
  Mediana: 0 dias
  Mín: 0 dias, Máx: 0 dias
  ![RQ02 - Pull Request Aceitas](./graficos/rq02_prs_box.png)

### RQ 05. Sistemas populares são escritos nas linguagens mais populares?

Métrica: linguagem primária de cada um desses repositórios
Linguagens mais populares (RQ05):
  TypeScript: 18 repositórios
  Python: 16 repositórios
  Unknown: 14 repositórios
  JavaScript: 14 repositórios
  C++: 5 repositórios
  Go: 5 repositórios
  Java: 4 repositórios
  Rust: 4 repositórios
  Shell: 3 repositórios
  Jupyter Notebook: 3 repositórios
  ![RQ02 - Pull Request Aceitas](./graficos/rq02_prs_box.png)

### RQ 06. Sistemas populares possuem um alto percentual de issues fechadas?

Métrica: razão entre número de issues fechadas pelo total de issues Relatório Final:
Percentual de issues fechadas (RQ06):
  Mediana: 91.98%
  ![RQ02 - Pull Request Aceitas](./graficos/rq02_prs_box.png)

### RQ 07: Sistemas escritos em linguagens mais populares recebem mais contribuição externa, lançam mais releases e são atualizados com mais frequência?
Linguagens mais populares:
  - TypeScript
  - Python
  - Unknown
  - JavaScript
  - C++

Comparação: Linguagens Populares vs Outras

| Métrica                     | Populares   | Outras      |
| --------------------------- | ----------- | ----------- |
| Repositórios                |          67 |          33 |
| Mediana PRs Aceitas (RQ02)  |        1949 |         945 |
| Mediana Releases (RQ03)     |          22 |           7 |
| Mediana Dias Update (RQ04)  |           0 |           0 |

Detalhamento por linguagem (Top 10):

| Linguagem   | Qty | Med PRs | Med Rels | Med Days Upd |
| ----------- | --- | ------- | -------- | ------------ |
| TypeScript  |  18 |    7019 |      212 |            0 |
| Python      |  16 |    2737 |       57 |            0 |
| Unknown     |  14 |     368 |        0 |            0 |
| JavaScript  |  14 |    1000 |       83 |            0 |
| C++         |   5 |   23240 |      219 |            0 |
| Go          |   5 |    2465 |      106 |            0 |
| Java        |   4 |    1179 |        0 |            0 |
| Rust        |   4 |   13325 |      341 |            0 |
| Shell       |   3 |     493 |        0 |            0 |
| Jupyter     |   3 |     376 |        0 |            0 |


Conclusão RQ07:
✓ Linguagens populares recebem MAIS contribuições externas
✓ Linguagens populares lançam MAIS releases
✗ Linguagens populares são atualizadas com MENOS frequência
