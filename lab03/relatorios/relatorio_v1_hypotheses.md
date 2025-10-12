# Lab03 — Hipóteses Iniciais e Plano de Análise

**Disciplina:** Laboratório de Experimentação de Software

**Lab:** Lab03 — Caracterizando a atividade de code review no GitHub

**Objetivo deste documento:** apresentar as hipóteses iniciais para as questões de pesquisa RQ01–RQ08, descrever as métricas que serão usadas, e indicar os testes estatísticos e visualizações a serem aplicados na primeira versão do relatório final (Lab03S02).

---

## 1. Metodologia (resumo)
- Dataset: PRs submetidos aos 200 repositórios mais populares do GitHub (cada repositório com pelo menos 100 PRs). 
- Seleção de PRs: somente PRs com estado `MERGED` ou `CLOSED`, com `reviews.totalCount >= 1`, e com duração (closedAt - createdAt) > 1 hora.
- Métricas principais (por PR):
  - Tamanho: `files_changed`, `additions`, `deletions`, `diff_size = additions + deletions`.
  - Tempo de análise: `time_to_close_hours`.
  - Descrição: `body_length_chars` (comprimento do corpo da descrição em caracteres).
  - Interações: `participant_count`, `comments_total` (número total de comentários), `review_count`.

---

## 2. Orientação estatística
- Para as análises de associação entre variáveis contínuas/ordinais e as respostas, usaremos correlações (Spearman) quando não assumirmos normalidade. Spearman é robusto para relações monotônicas não lineares e para variáveis com distribuição assimétrica (comum em PR sizes).
- Para a variável binária `merged` (feedback final: MERGED vs CLOSED), usaremos modelos de regressão logística multivariada. Incluir covariáveis: `log(diff_size + 1)`, `files_changed`, `log(time_to_close_hours + 1)`, `body_length_chars`, `review_count`, `participant_count`, além de informação do repositório (p.ex. stars) como controle.
- Para o número de revisões (`review_count`) usaremos modelos de contagem (Poisson ou Negative Binomial se houver overdispersion).
- Para comparações de medianas usar tabelas descritivas e boxplots/violin plots.

---

## 3. Hipóteses iniciais (RQ01–RQ08)

### A) Feedback Final das Revisões (Status do PR)

RQ01 — Tamanho dos PRs vs feedback final
- H0: O tamanho do PR (`diff_size`, `files_changed`) não está associado à probabilidade de um PR ser `MERGED`.
- H1: PRs menores (menor `diff_size` e `files_changed`) têm maior probabilidade de serem `MERGED`.
- Motivação: PRs maiores tendem a ser mais complexos e exigir mudanças significativas; isso pode aumentar a chance de revisão longa e rejeição.
- Teste/Análise: regressão logística (outcome = merged), coeficiente para `log(diff_size)` e `files_changed`; gráfico: boxplot de `diff_size` por `merged`.

RQ02 — Tempo de análise vs feedback final
- H0: `time_to_close_hours` não está associado à probabilidade de `MERGED`.
- H1: PRs com menor `time_to_close_hours` têm maior probabilidade de serem `MERGED` (ou seja, decisões rápidas tendem a resultar em merge), embora a direção também possa ser inversa em alguns contextos.
- Motivação: PRs simples/claros tendem a ser revisados e mesclados mais rápido.
- Teste/Análise: regressão logística com `log(time_to_close_hours + 1)`; survival curves separadas por status (KM) para explorar distribuição de tempos.

RQ03 — Descrição dos PRs vs feedback final
- H0: `body_length_chars` não está associado ao feedback final.
- H1: PRs com descrições mais longas/detalhadas têm maior probabilidade de serem `MERGED`.
- Motivação: descrições detalhadas facilitam a revisão e podem reduzir solicitações de mudanças.
- Teste/Análise: regressão logística; comparar medianas de `body_length_chars` entre `MERGED` e `CLOSED`.

RQ04 — Interações nos PRs vs feedback final
- H0: Métricas de interação (`participant_count`, `comments_total`, `review_count`) não estão associadas ao feedback final.
- H1: Interações mais elevadas (até certo ponto) estão associadas a maior probabilidade de `CLOSED` (rejeição) ou menor probabilidade de `MERGED` — hipótese alternativa: efeito não-linear (muitas interações podem indicar problemas que reduzem a chance de merge).
- Motivação: maior número de interações pode indicar que o PR exigiu revisões significativas.
- Teste/Análise: regressão logística com termos quadráticos ou splines para captar não-linearidade; boxplots e scatterplots com smoothing.

### B) Número de Revisões (counts)

RQ05 — Tamanho dos PRs vs número de revisões realizadas
- H0: `diff_size` não está associado ao `review_count`.
- H1: PRs maiores recebem mais revisões (maior `review_count`).
- Teste/Análise: regressão de contagem (Negative Binomial se overdispersion), plot de média de `review_count` por quartil de `diff_size`.

RQ06 — Tempo de análise vs número de revisões realizadas
- H0: `time_to_close_hours` não está associado ao `review_count`.
- H1: PRs que sofreram mais revisões tendem a ter maior `time_to_close_hours` (correlação positiva).
- Teste/Análise: correlação de Spearman + modelo de contagem com `log(time_to_close_hours + 1)` como covariável.

RQ07 — Descrição dos PRs vs número de revisões realizadas
- H0: `body_length_chars` não está associado ao `review_count`.
- H1: PRs com descrições mais detalhadas (maior `body_length_chars`) tendem a ter menor `review_count` (porque ficam mais claros desde o início).
- Teste/Análise: regressão de contagem; boxplots por faixas de `body_length_chars`.

RQ08 — Interações nos PRs vs número de revisões realizadas
- H0: Métricas de interação não predizem `review_count`.
- H1: PRs com mais participantes e comentários tendem a apresentar maior `review_count`.
- Teste/Análise: regressão de contagem; verificar multicolinearidade entre `comments_total`, `participant_count` e `review_count`.

---

## 4. Medidas sumarizadas para o relatório (o que apresentar em Lab03S02)
- Tabelas com medianas globais para cada métrica (`diff_size`, `time_to_close_hours`, `body_length_chars`, `participant_count`, `comments_total`, `review_count`).
- Boxplots por `merged` vs `closed` e histogramas das distribuições.
- Resultados dos testes de correlação (Spearman) e coeficientes das regressões (odds ratios para logistic regression; incident rate ratios para modelos de contagem).
- Exemplos (até 5) de PRs extremos (ex.: maior `diff_size`, maior `review_count`) e interpretação qualitativa breve.

---

## 5. Critérios de validade e escolhas metodológicas
- Usaremos Spearman quando as distribuições forem não-normais (em geral, `diff_size` e `review_count` são fortemente assimétricas).
- Testes multivariados (regressões) serão preferidos para controlar covariáveis (e.g., tamanho do repositório, linguagem, estrelas) e reduzir viés de confusão.
- Se identificarmos overdispersion no `review_count`, vamos usar Negative Binomial em vez de Poisson.

---

## 6. Próximos passos imediatos
1. Instalar dependências (`pandas`, `PyGithub`, `tqdm`).
2. Executar `pr-miner.py` em modo de teste (3–5 repositórios) para validar coleta e formatos.
3. Ajustar `pr-miner.py` para coletar `reviews` nodes e `comments` nodes (se já não coletados) e gerar métricas derivadas.
4. Rodar coleta completa e gerar `collected_prs_details.csv`.
5. Executar notebooks de EDA e preencher `relatorio_v1_hypotheses.md` com resultados reais.

---

*Documento gerado automaticamente para Lab03S02 — hipóteses iniciais e plano de análise.*
