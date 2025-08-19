# 🧪 Laboratório 01 — Análise de Repositórios Populares no GitHub

## 🎯 Objetivo

Investigar características de sistemas populares open-source, com base nos 1.000 repositórios mais estrelados no GitHub. As análises envolvem:

* Idade (maturidade)
* Contribuição externa (pull requests aceitas)
* Frequência de lançamentos (releases)
* Frequência de atualização (último push)
* Linguagem de programação mais comum
* Percentual de issues fechadas

---

## 🗂️ Etapas do Projeto

1. **Coleta de Repositórios com GraphQL API**

   * Paginação para capturar 1000 repositórios
   * Dados exportados para `.csv`

2. **Análise dos Dados Coletados**

   * Cálculo de medianas por métrica
   * Contagens por categoria (ex: linguagens)
   * Visualização de dados com gráficos

3. **Relatório Final**

   * Resposta às RQs
   * Hipóteses e discussão dos resultados
   * Geração de documentos e gráficos

---

## 🛠️ Como Executar

### 🔐 Configuração do Token



---

### ▶️ Etapas de Execução



---
## ❓ Questões de Pesquisa (RQs)

| RQ  | Pergunta                                                                  | Métrica                                    |
| --- | ------------------------------------------------------------------------- | ------------------------------------------ |
| RQ1 | Sistemas populares são maduros/antigos?                                   | Idade do repositório                       |
| RQ2 | Sistemas populares recebem muita contribuição externa?                    | Total de pull requests aceitas             |
| RQ3 | Sistemas populares lançam releases com frequência?                        | Total de releases                          |
| RQ4 | Sistemas populares são atualizados com frequência?                        | Tempo desde a última atualização (em dias) |
| RQ5 | Sistemas populares são escritos nas linguagens mais populares?            | Linguagem principal do repositório         |
| RQ6 | Sistemas populares possuem um alto percentual de issues fechadas?         | Ratio: issues fechadas / total de issues   |
| RQ7 | Linguagens populares afetam contribuição, releases e atualização? (bônus) | Análise por linguagem das RQs 2, 3 e 4     |

---

## 📈 Métricas Utilizadas

| Categoria            | Métricas                                          |
| -------------------- | ------------------------------------------------- |
| Maturidade           | Idade do repositório                              |
| Colaboração Externa  | Total de pull requests aceitas                    |
| Atividade            | Total de releases, tempo desde última atualização |
| Popularidade         | Número de estrelas (filtro inicial)               |
| Linguagem            | Linguagem primária                                |
| Qualidade Processual | Percentual de issues fechadas                     |

---

## 👥 Equipe

* **Izabela Cecilia Silva Barbosa**
* **Lucas Machado de Oliveira Andrade**
* **Mariana Eliza Alves Costa**
* **Vitor Fernandes de Souza**

---

## 📁 Estrutura do Projeto

