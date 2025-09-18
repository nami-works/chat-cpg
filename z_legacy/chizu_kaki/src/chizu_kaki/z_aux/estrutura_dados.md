### Estrutura de Dados para a Crew ChizuKaki

A Crew ChizuKaki é encarregada de realizar avaliações de proximidade entre endereços definidos por CEPs e uma lista de shoppings. Para isso, propomos uma estrutura de dados sólida e bem definida, conforme as diretrizes da CrewAI e as melhores práticas de manipulação de dados.

---

## 1. Estrutura de Entrada

**a. Dicionário de Shoppings (`ceps_shoppings`)**:
O dicionário será fixo no código e conterá os nomes dos shoppings como chaves e os respectivos CEPs como valores.

```python
ceps_shoppings = {
    "Shopping A": "12345678",
    "Shopping B": "87654321",
    "Shopping C": "11223344",
}
```

**b. Arquivo CSV da Base de CEPs (`base_ceps.csv`)**:
O arquivo CSV deve ter uma estrutura simples, contendo uma única coluna chamada `cep`. A primeira linha é um cabeçalho.

```
cep
12345678
87654321
11223344
```

## 2. Estrutura de Saída

**a. Arquivo CSV de Resultados (`ceps_distancias.csv`)**:
O arquivo gerado após o cálculo das distâncias deve seguir a seguinte estrutura:

```
cep,shopping_mais_proximo,distancia_km
12345678,Shopping A,5.50
87654321,Shopping B,3.25
11223344,N/A,N/A
```

### 3. Implementação das Funções

Abaixo, apresentamos a implementação das funções que atenderão às necessidades da Crew ChizuKaki.

```python
import pandas as pd
import requests
from geopy.distance import great_circle

def carregar_arquivo_csv(caminho_arquivo):
    """
    Função para carregar e validar arquivo CSV.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"O arquivo {caminho_arquivo} não foi encontrado.")
    
    df = pd.read_csv(caminho_arquivo)
    if 'cep' not in df.columns:
        raise ValueError("O arquivo CSV deve conter uma coluna chamada `cep`.")

    return df

def validar_ceps(ceps):
    """ Função para validar o formato dos CEPs. """
    return all(isinstance(cep, str) and cep.isdigit() and len(cep) == 8 for cep in ceps)

def obter_coordenadas(cep):
    """ Função para obter latitude e longitude a partir do CEP. """
    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
    if response.status_code != 200 or 'erro' in response.json():
        return None
    data = response.json()
    return (data['cep'], float(data['latitude']), float(data['longitude']))

def calcular_distancias(ceps_df, ceps_shoppings):
    """ Função para calcular a distância dos CEPs para os shoppings. """
    resultados = []
    for index, row in ceps_df.iterrows():
        cep = row['cep']
        coordenadas_cliente = obter_coordenadas(cep)
        if not coordenadas_cliente:
            resultados.append((cep, "N/A", "N/A"))
            continue
        
        distancias = {}
        for shopping, cep_shopping in ceps_shoppings.items():
            coordenadas_shopping = obter_coordenadas(cep_shopping)
            if coordenadas_shopping:
                distancia = great_circle(coordenadas_cliente[1:], coordenadas_shopping[1:]).km
                distancias[shopping] = distancia
        
        if distancias:
            shopping_proximo = min(distancias, key=distancias.get)
            distancia_proxima = round(distancias[shopping_proximo], 2)
            resultados.append((cep, shopping_proximo, distancia_proxima))
        else:
            resultados.append((cep, "N/A", "N/A"))

    return pd.DataFrame(resultados, columns=['cep', 'shopping_mais_proximo', 'distancia_km'])

def gerar_relatorio(distancias_df):
    """ Função para gerar o arquivo CSV de resultados. """
    distancias_df.to_csv('ceps_distancias.csv', index=False)
```

### 4. Executando a Crew

O ponto de entrada para a execução do fluxo da Crew ChizuKaki pode ser estruturado da seguinte forma:

```python
def main():
    # Carregar o arquivo base de CEPs
    base_ceps_df = carregar_arquivo_csv('base_ceps.csv')
    
    # Validar CEPs dos shoppings
    if not validar_ceps(ceps_shoppings.values()):
        print("Erro: Um ou mais CEPs dos shoppings estão inválidos.")
        return

    # Calcular distâncias
    distancias_df = calcular_distancias(base_ceps_df, ceps_shoppings)
    
    # Gerar relatório
    gerar_relatorio(distancias_df)
    print("Relatório de distâncias gerado com sucesso como 'ceps_distancias.csv'.")

if __name__ == "__main__":
    main()
```

### Observações Finais
- A estruturação dos dados de entrada e saída segue padrões comuns a projetos de dados e serviços web, garantindo legibilidade e facilidade de manutenção.
- As funções para validar, converter e calcular distâncias foram construídas com robustez para lidar com potenciais falhas.
- Exemplos e bibliotecas utilizadas, como `pandas` e `geopy`, foram escolhidos por sua popularidade e eficiência conforme demosntrado em práticas de projetos em [GitHub](https://github.com), [PyPI](https://pypi.org), e [StackOverflow](https://stackoverflow.com).

Dessa forma, a Crew ChizuKaki está pronta para seus objetivos de análise de proximidade com shoppings de maneira clara e eficiente, respeitando as diretrizes de documentação e implementação definidas anteriormente.