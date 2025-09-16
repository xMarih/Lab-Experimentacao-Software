# Lab02 - Estudo das Características de Qualidade de Sistemas Java

## Descrição

Este repositório contém o código e os resultados do Laboratório 02 da disciplina de Laboratório de Experimentação de Software. O objetivo deste laboratório é analisar aspectos da qualidade de repositórios Java, correlacionando-os com características do seu processo de desenvolvimento, sob a perspectiva de métricas de produto calculadas através da ferramenta CK.

## Estrutura do Repositório

## Metodologia

1.  **Seleção de Repositórios:** Coleta dos top-1.000 repositórios Java mais populares do GitHub.
2.  **Coleta de Dados:** Utilização das APIs REST ou GraphQL do GitHub para coletar informações dos repositórios.
3.  **Análise Estática de Código:** Utilização da ferramenta CK para medir os valores de qualidade (CBO, DIT, LCOM).
4.  **Análise de Dados:** Sumarização dos dados obtidos através de valores de medida central (mediana, média e desvio padrão).
5.  **Visualização de Dados:** Geração de gráficos de correlação para visualizar o comportamento dos dados obtidos.
6.  **Testes Estatísticos:** Utilização de testes estatísticos (por exemplo, teste de correlação de Spearman ou de Pearson) para fornecer confiança nas análises apresentadas.

## Questões de Pesquisa

*   RQ 01. Qual a relação entre a popularidade dos repositórios e as suas características de qualidade?
*   RQ 02. Qual a relação entre a maturidade do repositórios e as suas características de qualidade ?
*   RQ 03. Qual a relação entre a atividade dos repositórios e as suas características de qualidade?
*   RQ 04. Qual a relação entre o tamanho dos repositórios e as suas características de qualidade?

## Sprints e Entregas

*   **Lab02S01:** Lista dos 1.000 repositórios Java + Script de Automação de clone e Coleta de Métricas + Arquivo .csv com o resultado das medições de 1 repositório (5 pontos)
*   **Lab02S02:** Arquivo .csv com o resultado de todas as medições dos 1.000 repositórios + hipóteses (5 pontos) Análise e visualização de dados + elaboração do relatório final (10 pontos)

## Instruções de Uso

1.  **Configuração do Ambiente:**
    *   Certifique-se de ter o Python 3.7 ou superior instalado.
    *   Crie um ambiente virtual: `python -m venv venv`
    *   Ative o ambiente virtual:
        *   No Windows: `.\venv\Scripts\activate`
        *   No Linux/macOS: `source venv/bin/activate`
    *   Instale as dependências: `pip install -r requirements.txt` (assumindo que você tenha um arquivo `requirements.txt`)

2.  **Clone dos Repositórios:**
    *   Execute o script `github_clone.py` para clonar os repositórios do GitHub.

3.  **Extração de Métricas CK:**
    *   Execute o script `ck_metrics_extractor.py` para extrair as métricas de qualidade usando a ferramenta CK.

4.  **Análise e Visualização de Dados:**
    *   Utilize os scripts em `services/` para analisar os dados e gerar os gráficos.

5.  **Elaboração do Relatório Final:**
    *   Preencha o arquivo `relatorios/relatorio_final.md` com os resultados da sua análise.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests para melhorar este projeto.

## Autores

*   Izabela Cecilia Silva Barbosa
*   Lucas Machado de Oliveira Andrade
*   Mariana Eliza Alves Costa
*   Vitor Fernandes de Souza
