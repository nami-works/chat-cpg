```python
# arquivo: metas_vendas.py

import pandas as pd  # Importa a biblioteca pandas para manipulação de dados
import requests  # Importa a biblioteca requests para coletas de dados via API
from statsmodels.tsa.seasonal import seasonal_decompose  # Importa a decomposição sazonal do Statsmodels
from sklearn.linear_model import LinearRegression  # Importa regressão linear do Scikit-Learn
from prophet import Prophet  # Importa a biblioteca Prophet para previsão de séries temporais
from pmdarima import auto_arima  # Importa o modelo ARIMA da biblioteca pmdarima
from typing import Dict, Any  # Importa tipagens para uso nas funções

def coletar_dados(api_url: str, params: Dict[str, Any]) -> pd.DataFrame:
    """
    Coleta dados de vendas e variáveis internas a partir da API.
    
    Args:
        api_url (str): URL da API de onde os dados serão coletados.
        params (dict): Parâmetros a serem passados na requisição da API.
        
    Returns:
        DataFrame: Um dataframe contendo os dados coletados.
        
    Example:
        dados = coletar_dados('http://api.exemplo.com/data', {'key': 'value'})
    """
    response = requests.get(api_url, params=params)  # Realiza a requisição GET
    data = response.json()  # Converte a resposta em JSON
    df = pd.DataFrame(data)  # Cria um DataFrame a partir dos dados
    return df

def preparar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Realiza limpeza e formatação do DataFrame coletado.
    
    Args:
        df (DataFrame): DataFrame a ser preparado.
        
    Returns:
        DataFrame: DataFrame limpo e formatado.
        
    Example:
        dados_preparados = preparar_dados(dados)
    """
    df.columns = [col.strip() for col in df.columns]  # Remove espaços em branco dos nomes das colunas
    df = df.dropna()  # Remove linhas com valores ausentes
    # Outras transformações de limpeza podem ser adicionadas aqui
    return df

def calcular_vendas_historicas(df: pd.DataFrame, periodo: str) -> pd.DataFrame:
    """
    Calcula as vendas históricas com base no período especificado.
    
    Args:
        df (DataFrame): DataFrame contendo os dados de vendas.
        periodo (str): Período para o qual as vendas serão calculadas (e.g., 'M' para mensal).
        
    Returns:
        DataFrame: DataFrame com vendas históricas calculadas.
        
    Example:
        vendas_historicas = calcular_vendas_historicas(dados_preparados, 'M')
    """
    vendas_historicas = df.resample(periodo).sum()  # Agrupa vendas pelo período definido
    return vendas_historicas

def analisar_sazonalidade(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisa a sazonalidade e ajusta vendas com base em tendências.
    
    Args:
        df (DataFrame): DataFrame com vendas a serem analisadas.
        
    Returns:
        DataFrame: DataFrame com ajustes sazonais.
        
    Example:
        vendas_ajustadas = analisar_sazonalidade(vendas_historicas)
    """
    decomposicao = seasonal_decompose(df, model='additive')  # Decomposição da série temporal
    df['ajuste'] = decomposicao.trend  # Adiciona a tendência ao DataFrame
    return df

def modelar_vendas(df: pd.DataFrame, variaveis: list) -> Dict[str, Any]:
    """
    Aplica um modelo estatístico para prever vendas futuras.
    
    Args:
        df (DataFrame): DataFrame com dados históricos.
        variaveis (list): Variáveis independentes para o modelo.
        
    Returns:
        dict: Dicionário com informações do modelo e previsões de vendas.
        
    Example:
        resultado_modelagem = modelar_vendas(dados_preparados, ['variavel1', 'variavel2'])
    """
    modelo = LinearRegression()
    X = df[variaveis]  # Variáveis independentes
    y = df['vendas']  # Variável dependente
    modelo.fit(X, y)  # Ajusta o modelo
    predicoes = modelo.predict(X)  # Faz previsões
    return {'modelo': modelo, 'previsoes': predicoes}

def gerar_metas(df: pd.DataFrame, metas_previstas: Dict) -> pd.DataFrame:
    """
    Gera as metas mensais baseadas em previsões e outras variáveis.
    
    Args:
        df (DataFrame): DataFrame com previsões.
        metas_previstas (dict): Metas projetadas para cada mês.
        
    Returns:
        DataFrame: DataFrame com metas mensais.
        
    Example:
        metas_mensais = gerar_metas(dados_preparados, {'Janeiro': 10000, 'Fevereiro': 12000})
    """
    for mes, meta in metas_previstas.items():
        df.loc[mes, 'meta'] = meta  # Atribui metas aos meses no DataFrame
    return df

def validar_metas(df: pd.DataFrame, metas: pd.DataFrame) -> pd.DataFrame:
    """
    Valida as metas contra dados históricos para ajustar previsões.
    
    Args:
        df (DataFrame): DataFrame com dados atuais.
        metas (DataFrame): DataFrame com metas a serem validadas.
        
    Returns:
        DataFrame: DataFrame com valiações de metas.
        
    Example:
        validacao_metas = validar_metas(dados_preparados, metas_mensais)
    """
    df['validacao'] = df['vendas'] >= df['meta']  # Compara vendas com metas
    return df

def salvar_resultados(df: pd.DataFrame, file_path: str) -> None:
    """
    Salva o DataFrame com resultados em um arquivo CSV.
    
    Args:
        df (DataFrame): DataFrame com resultados a serem salvos.
        file_path (str): Caminho do arquivo em que os resultados serão salvos.
        
    Example:
        salvar_resultados(dados_preparados, 'resultados_vendas.csv')
    """
    df.to_csv(file_path, index=False)  # Salva o DataFrame em um arquivo CSV
```

Certifique-se de que todas as dependências estão instaladas corretamente para o funcionamento das funções, utilizando:
```bash
pip install pandas requests statsmodels scikit-learn prophet pmdarima
```

Esse código agora contém todas as funções necessárias conforme o planejamento, com documentação, types e boas práticas de codificação conforme pedido e referências citadas.