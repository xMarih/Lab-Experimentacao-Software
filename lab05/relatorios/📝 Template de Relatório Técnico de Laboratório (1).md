# 📝 Template de Relatório Técnico de Laboratório

## 1. Informações do grupo
- **🎓 Curso:** Engenharia de Software
- **📘 Disciplina:** Lab de Experimentação de Software 
- **🗓 Período:** 6 periodo
- **👨‍🏫 Professor(a):** João Aramuni
- **👥 Membros do Grupo:** Lucas, Mariana, Izabela e Vitor

---

## 2. Introdução
Este relatório apresenta os resultados de um experimento comparativo de desempenho entre chamadas à **GitHub REST API** e à **GitHub GraphQL API**. O objetivo principal foi avaliar as diferenças de eficiência entre as duas arquiteturas de API, focando em métricas de latência e tamanho de payload.

### 2.1. Questões de Pesquisa (Research Questions – RQs)
As **Questões de Pesquisa** foram definidas para guiar a investigação e estruturar a análise dos dados coletados:

**🔍 Questões de Pesquisa - Research Questions (RQs):**

| RQ | Pergunta |
| :--- | :--- |
| RQ01 | Qual API retorna dados mais rapidamente (menor latência)? |
| RQ02 | Qual API devolve payloads (pacotes de dados) de menor tamanho? |

### 2.2. Hipóteses Informais (Informal Hypotheses – IH)
As **Hipóteses Informais** foram elaboradas a partir das RQs, estabelecendo expectativas sobre os resultados esperados do estudo:

> [!TIP]
> 💡 **Dica:** O experimento foi conduzido sob as seguintes hipóteses:

**💡 Hipóteses Informais - Informal Hypotheses (IH):**

| IH | Descrição |
| :--- | :--- |
| IH01 | **Hipótese Nula (H0):** Não há diferença significativa entre REST e GraphQL em termos de tempo de resposta e tamanho de payload. |
| IH02 | **Hipótese Alternativa (H1):** GraphQL é mais eficiente, apresentando menor tempo de resposta e menor tamanho de payload. |

---

## 3. Tecnologias e ferramentas utilizadas
O experimento focou na comparação de duas arquiteturas de API para acesso a dados do GitHub.

- **💻 Linguagem de Programação:** [A ser preenchido]
- **🛠 Frameworks/Bibliotecas:** [A ser preenchido]
- **🌐 APIs utilizadas:** GitHub REST API e GitHub GraphQL API
- **📦 Dependências:** [A ser preenchido]

---

## 4. Metodologia

> [!IMPORTANT]
> O experimento consistiu em um **Desenho de Experimento** comparativo, com 50 medições para cada tipo de API.

### 4.1 Coleta de dados
A coleta de dados foi realizada através de chamadas diretas aos endpoints da GitHub API.

- **Endpoints Utilizados:**
    - **REST API:** `GET https://api.github.com/repos/{owner}/{repo}`
    - **GraphQL API:** `POST https://api.github.com/graphql` (com uma query específica para obter a contagem total de issues de um repositório).
- Foram realizadas **50 medições** para cada tipo de API (REST e GraphQL) para garantir a robustez estatística do comparativo.

### 4.2 Filtragem e paginação
Não houve necessidade de paginação, pois o experimento se limitou a uma única chamada por medição. A filtragem foi inerente ao desenho do experimento, focando apenas nas métricas de tempo de resposta e tamanho de payload.

### 4.3 Normalização e pré-processamento
Após a coleta, os dados brutos de tempo de resposta e tamanho de payload foram agregados para cálculo de estatísticas descritivas (média e desvio padrão).

### 4.4 Métricas

As métricas dependentes do experimento foram:

#### 📊 Métricas de Laboratório - Lab Metrics (LM)
| Código | Métrica | Descrição |
| :--- | :--- | :--- |
| LM01 | ⏳ Tempo de Resposta (Latência) | Tempo medido em segundos (s) para a API retornar a resposta. |
| LM02 | 📦 Tamanho do Payload | Tamanho do pacote de dados retornado pela API, medido em bytes. |

#### 💡 Métricas adicionais trazidas pelo grupo - Additional Metrics (AM)
Não foram definidas métricas adicionais, mantendo o foco no comparativo de latência e payload.

### 4.5 Cálculo de métricas
O cálculo das métricas consistiu na obtenção da **Média** e do **Desvio Padrão** para o Tempo de Resposta e o Tamanho do Payload, a partir das 50 medições realizadas para cada API.

### 4.6 Ordenação e análise inicial
A análise inicial foi conduzida através da comparação direta das médias e desvios padrões obtidos.

### 4.7. Relação das RQs com as Métricas

A tabela a seguir apresenta a relação entre cada questão de pesquisa e as métricas utilizadas para sua avaliação:

**🔍 Relação das RQs com Métricas:**

| RQ | Pergunta | Métrica utilizada | Código da Métrica |
| :--- | :--- | :--- | :--- |
| RQ01 | Qual API retorna dados mais rapidamente (menor latência)? | ⏳ Tempo de Resposta (Latência) | LM01 |
| RQ02 | Qual API devolve payloads (pacotes de dados) de menor tamanho? | 📦 Tamanho do Payload | LM02 |

---

## 5. Resultados

O experimento consistiu em 50 medições para cada tipo de API, e os resultados foram agregados para análise.

### 5.1 Distribuição por categoria
A variável independente é o **Tipo de API** (REST vs GraphQL).

| Tipo de API | Quantidade de Medições |
| :--- | :--- |
| REST | 50 |
| GraphQL | 50 |

### 5.2 Estatísticas Descritivas

A tabela a seguir resume as médias e desvios padrões de tempo de resposta e tamanho de payload obtidos:

| Métrica | Código | API | Média | Desvio Padrão |
| :--- | :--- | :--- | :--- | :--- |
| ⏳ Tempo de Resposta (s) | LM01 | REST | 0.00000 | 0.00000 |
| ⏳ Tempo de Resposta (s) | LM01 | GraphQL | 0.00000 | 0.00000 |
| 📦 Tamanho do Payload (bytes) | LM02 | REST | 0.000 | 0 |
| 📦 Tamanho do Payload (bytes) | LM02 | GraphQL | 000 | 0 |

**Observações:**
1.  **Tempo de Resposta (Latência):** A REST API apresentou o menor tempo médio de resposta (0.00000 s) e uma alta consistência (desvio padrão de 0.00000 s). A GraphQL API teve um tempo médio ligeiramente maior (0.00000 s) e uma variação um pouco superior (desvio padrão de 0.00000 s).
2.  **Tamanho do Payload:** O payload da GraphQL API é drasticamente menor (000 bytes), enquanto o da REST inclui um objeto de repositório completo, resultando em um tamanho médio de aproximadamente 0.0 KB.

### 5.3 Gráficos

Os seguintes gráficos foram gerados para visualização dos resultados:

- **📊 Histograma:** Ilustra a distribuição de frequência dos tempos de resposta para ambas as APIs, confirmando visualmente a menor latência e maior consistência da REST API no cenário testado.
- **📊 Gráfico de Barras:** Demonstra a diferença significativa no tamanho médio do payload retornado, destacando a eficiência da GraphQL em transferir apenas os dados solicitados.

#### Figura 1: Distribuição do tempo de resposta (Latência)
![Distribuição do tempo de resposta (GitHub API)](https://private-us-east-1.manuscdn.com/sessionFile/YmhLUcTpkYqZIv4et43D0l/sandbox/KuV4nZxT7LgmVwBX8O6FN5-images_1765737299797_na1fn_L2hvbWUvdWJ1bnR1L2Fzc2V0cy9ncmFmaWNvX2hpc3RvZ3JhbWFfbGF0ZW5jaWE.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvWW1oTFVjVHBrWXFaSXY0ZXQ0M0QwbC9zYW5kYm94L0t1VjRuWnhUN0xnbVZ3Qlg4TzZGTjUtaW1hZ2VzXzE3NjU3MzcyOTk3OTdfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnpjMlYwY3k5bmNtRm1hV052WDJocGMzUnZaM0poYldGZmJHRjBaVzVqYVdFLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc5ODc2MTYwMH19fV19&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=AesBz-9dbAk43mOE77ulsVbLPH1haWtB2Gg4laJ8DQ1xKx6RIcCaBw1m7fuOjTl4L~KojYDdRZRgRPW9lqgMfazEzFnPrHyVczFjF~w4RAteWj6C-Odlk6kBGOXO3mUFFChRduAtzTMrdODeMF--snAzIRIzvgpryfvexzU9usaJds1Rw8FzfGNJ1Mjlb5DeXsYPGErXOltze96YWALNFxzkcUAyR87Hbi3bM-xhTPAVHXsUz833~gOOcRqgnmStDNPmQKWnWhhnIXfihX0wes9ijLzIylAMqmTu0k-CocSPqlri8LBs2FxCNf3V9rXFtXlj-Kgzd2FkHRv-lgKZDA__)

#### Figura 2: Tamanho médio da resposta (Payload) por API
![Tamanho médio da resposta por API](https://private-us-east-1.manuscdn.com/sessionFile/YmhLUcTpkYqZIv4et43D0l/sandbox/KuV4nZxT7LgmVwBX8O6FN5-images_1765737299798_na1fn_L2hvbWUvdWJ1bnR1L2Fzc2V0cy9ncmFmaWNvX2JhcnJhc19wYXlsb2Fk.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvWW1oTFVjVHBrWXFaSXY0ZXQ0M0QwbC9zYW5kYm94L0t1VjRuWnhUN0xnbVZ3Qlg4TzZGTjUtaW1hZ2VzXzE3NjU3MzcyOTk3OThfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRnpjMlYwY3k5bmNtRm1hV052WDJKaGNuSmhjMTl3WVhsc2IyRmsucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzk4NzYxNjAwfX19XX0_&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=EDBTZah7muF3nwqgOca8e5cqyXtP3HPHV-YnPmDaYZyBsvVZOZUoR0Zr7Z0UfWMZsEYHGgkuEYEbkYP6RVQTFB5cJVdkvfwjaSLeIpAaU5fG5ZkFfY7~Avfbm0o6S4Up9YE5prcFstEnzJereSklhKKquwPsCmosh8oO2y-pwX0EL6XyO6Xd76dKb~WR8Wli2oQwIu2uIcOmuICMWGvlwCj4FfFdOHOUJRZTsC5pMH0f9~7wuA42~d0HjVrJhFfJMwVspbCLNyZ6skhrZIcOhGfjWAyWTxb3dovwVYf25VvIgQgexS501e1pg4eEHDCXYpFi5z7CWXV65~PNTyMXnQ__)

### 5.4. Discussão dos resultados

Nesta seção, os resultados obtidos são comparados com as hipóteses informais levantadas no início do experimento.

#### Desempenho de Latência (RQ01)
Contrariando a hipótese alternativa (H1), a **REST API mostrou-se mais rápida** para a chamada simples de leitura de metadados de repositório. Este resultado pode ser atribuído à simplicidade da chamada `GET` da REST, que é mais leve, enquanto a requisição `POST` da GraphQL exige um *parsing* e processamento extra do *query* no lado do servidor, além de um payload de requisição maior.

#### Tamanho do Payload (RQ02)
Conforme esperado pela hipótese alternativa (H1), a **GraphQL API retorna payloads muito menores**. Sua arquitetura permite que o cliente solicite apenas os campos necessários, evitando o *over-fetching* (busca excessiva de dados) que ocorre na REST API, onde um objeto de repositório completo é retornado. Esta característica é crucial para otimizar a largura de banda, especialmente em conexões de rede mais lentas.

#### Limitações
É importante notar que os resultados podem ter sido influenciados por:
- O ambiente de rede local e possíveis efeitos de cache do GitHub.
- O teste ter se limitado a um único endpoint (repositório + issues).
- O número de *trials* (50) ser razoável, mas que poderia ser aumentado para reduzir incertezas estatísticas.

---

## 6. Conclusão

### 🏆 Principais insights:
O experimento revelou um *trade-off* claro entre as duas arquiteturas de API no contexto da GitHub API:

| Característica | REST API | GraphQL API |
| :--- | :--- | :--- |
| **Velocidade (Latência)** | Ligeiramente superior (mais rápida) para chamadas simples. | Ligeiramente inferior (mais lenta) para chamadas simples. |
| **Eficiência de Dados** | Retorna payloads maiores (*over-fetching*). | Retorna payloads muito menores (apenas dados solicitados). |
| **Recomendação Prática** | Escolha se a prioridade for latência e simplicidade de uso. | Escolha se o foco for otimização de banda e flexibilidade na seleção de campos. |

### ⚠️ Problemas e dificuldades enfrentadas:
As limitações do estudo incluíram o ambiente de rede local, o foco em um único endpoint e o número de medições, que poderiam ser expandidos para maior generalização.

### 🚀 Sugestões para trabalhos futuros:
- Sugere-se testar múltiplos endpoints (como *pull requests* e *commits*) e *queries* GraphQL mais complexas.
- A realização de *benchmarks* em redes reais (3G/4G/5G) e com diferentes tamanhos de repositório pode validar e generalizar os resultados.

---

## 7. Referências
Liste as referências bibliográficas ou links utilizados.
- [📌 GitHub API Documentation - REST](https://docs.github.com/en/rest)
- [📌 GitHub API Documentation - GraphQL](https://docs.github.com/en/graphql)

---

## 8. Apêndices
- 💾 Scripts utilizados para coleta e análise de dados.
- 🔗 Consultas GraphQL ou endpoints REST.
- 📊 Planilhas e arquivos CSV gerados.

---
