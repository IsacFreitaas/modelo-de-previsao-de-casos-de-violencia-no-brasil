# Previsão de Casos de Violência no Brasil

## 🎯 Objetivo

Este projeto tem como objetivo desenvolver um modelo de machine learning para prever a quantidade de casos de violência (doméstica, sexual, autoprovocada, etc.) no Brasil. A análise é estratificada por estado e faixa etária, utilizando dados históricos de violência e indicadores socioeconômicos para identificar tendências e padrões.

O problema social da violência é complexo e multifacetado. Ao utilizar dados, buscamos fornecer uma ferramenta que possa auxiliar na compreensão de suas dinâmicas e, potencialmente, no planejamento de políticas públicas mais eficazes.

## 📊 Fontes de Dados

O modelo é construído a partir de dados públicos de fontes oficiais brasileiras, garantindo transparência e replicabilidade:

- **DataSUS**: O Sistema de Informação de Agravos de Notificação (SINAN) fornece dados detalhados sobre notificações de violência interpessoal e autoprovocada.
- **IBGE (Instituto Brasileiro de Geografia e Estatística)**: Fornece indicadores socioeconômicos essenciais, como dados populacionais, renda per capita, taxas de desemprego, escolaridade e o Índice de Desenvolvimento Humano (IDH) por município e estado.
- **Dados.gov.br**: Portal de dados abertos do governo federal, que pode ser utilizado para encontrar datasets complementares.

## ⚙️ Metodologia

O projeto foi estruturado em quatro etapas principais, seguindo um fluxo de trabalho padrão em projetos de Ciência de Dados:

1.  **Coleta e Tratamento**: Os dados brutos são coletados das fontes mencionadas. Scripts em Python (`notebooks/01_Coleta_e_Tratamento.ipynb`) são utilizados para limpar, transformar, unificar os datasets e tratar valores ausentes, resultando em uma base de dados consolidada e pronta para análise.

2.  **Análise Exploratória de Dados (EDA)**: Com os dados tratados, realizamos uma investigação (`notebooks/02_EDA_e_Modelagem.ipynb`) para descobrir tendências, padrões e correlações. Gráficos de séries temporais e mapas de calor são gerados para visualizar a evolução da violência por estado, tipo e sua relação com fatores socioeconômicos.

3.  **Modelagem Preditiva**: Nesta fase, treinamos e avaliamos diferentes modelos de machine learning (como XGBoost e Random Forest) para prever o número de casos futuros. O processo inclui a seleção de variáveis (features), o ajuste de hiperparâmetros e a validação do modelo com métricas como MAE, RMSE e R². O melhor modelo é salvo no arquivo `model.pkl`.

4.  **Interface Interativa**: Uma aplicação web desenvolvida com **Flet** (`app/main.py`) permite que o usuário interaja com o modelo. É possível filtrar os dados, visualizar o histórico e as previsões em um gráfico dinâmico, e simular cenários alterando variáveis socioeconômicas para observar o impacto previsto nos casos de violência.

## 🖥️ Interface da Aplicação

A interface permite uma análise intuitiva e personalizada.

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e rodar a aplicação em sua máquina.

### Pré-requisitos

- Python 3.8 ou superior
- Git

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/IsacFreitaas/modelo-de-previsao-de-casos-de-violencia-no-brasil.git
    cd modelo-de-previsao-de-casos-de-violencia-no-brasil/
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **(Opcional) Execute os notebooks de análise e treinamento:**
    Para gerar os dados tratados e o modelo `model.pkl` a partir dos dados brutos, execute os notebooks localizados na pasta `/notebooks` usando Jupyter Notebook ou JupyterLab.
    ```bash
    jupyter notebook
    ```

5.  **Inicie a aplicação Flet:**
    ```bash
    flet run app/main.py
    ```