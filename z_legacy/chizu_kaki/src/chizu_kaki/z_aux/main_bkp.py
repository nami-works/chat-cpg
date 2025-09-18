# ```python
import requests
import pandas as pd
from geopy.distance import great_circle
from typing import Any, Dict, List, Tuple

# Ferramenta para validação de CEPs.
class CepValidationTool:
    def run(self, ceps: List[str]) -> bool:
        """ Valida se todos os CEPs estão no formato adequado (string de 8 dígitos numéricos). """
        return all(isinstance(cep, str) and len(cep) == 8 and cep.isdigit() for cep in ceps)

# Ferramenta para conversão de CEP para coordenadas geográficas.
class GeoCodingTool:
    def run(self, cep: str) -> Tuple[str, float, float]:
        """ Consulta a API ViaCEP para obter coordenadas a partir do CEP. """
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        if response.status_code != 200 or 'erro' in response.json():
            return None
        data = response.json()
        return (data['cep'], float(data['latitude']), float(data['longitude']))

# Ferramenta para calcular a distância geodésica entre duas coordenadas.
class DistanceCalculatorTool:
    def run(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """ Calcula a distância geodésica entre duas coordenadas. """
        return round(great_circle(coord1, coord2).km, 2)

# Ferramenta para gerar um relatório CSV com os resultados finais.
class ReportGeneratorTool:
    def run(self, data: List[Tuple[str, str, float]]) -> str:
        """ Gera um CSV com os resultados das distâncias calculadas. """
        df = pd.DataFrame(data, columns=['cep', 'shopping_mais_proximo', 'distancia_km'])
        caminho_csv = 'data/ceps_distancias.csv'
        df.to_csv(caminho_csv, index=False)
        return caminho_csv

# Função principal para executar o processo da Crew ChizuKaki.
def main():
    ceps_shoppings = {
        "Iguatemi Fortaleza": "60811341",
        "Shopping Recife": "51020900",
        "Shopping RioMar Recife": "51110160",
        "Shops Jardins": "01414002",
        "Shopping RioSul": "22290070"
    }

    # Carrega os dados dos CEPs do arquivo CSV.
    base_ceps_df = pd.read_csv('data/base_ceps.csv')

    # Validação dos CEPs na base de dados.
    validacao_tool = CepValidationTool()
    if not validacao_tool.run(base_ceps_df['cep'].tolist()):
        print("Erro: CEPs inválidos detectados.")
        return

    resultados = []

    # Processa os CEPs, calculando distâncias e gerando resultados.
    for cep in base_ceps_df['cep']:
        coordenadas_cliente = GeoCodingTool().run(cep)
        if not coordenadas_cliente:
            resultados.append((cep, "N/A", "N/A"))
            continue

        distancias = {}
        for shopping, shopping_cep in ceps_shoppings.items():
            coordenadas_shopping = GeoCodingTool().run(shopping_cep)
            if coordenadas_shopping:
                distancias[shopping] = DistanceCalculatorTool().run(
                    (coordenadas_cliente[1], coordenadas_cliente[2]),
                    (coordenadas_shopping[1], coordenadas_shopping[2])
                )

        shopping_proximo = min(distancias, key=distancias.get) if distancias else "N/A"
        distancia_proxima = distancias.get(shopping_proximo, "N/A")
        resultados.append((cep, shopping_proximo, distancia_proxima))

    # Gera o relatório em CSV com os resultados.
    caminho_csv = ReportGeneratorTool().run(resultados)
    print(f"Relatório gerado com sucesso em {caminho_csv}.")

if __name__ == "__main__":
    main()
# ```

# ### Estrutura do Projeto
# ```plaintext
# chizukaki/
# │
# ├── agents.py                # Implementação das ferramentas da Crew
# ├── main.py                  # Script principal que orquestra a execução
# ├── requirements.txt         # Dependências do projeto
# ├── data/                    # Pasta para armazenar dados
# │   ├── base_ceps.csv        # Arquivo CSV de entrada com CEPs
# │   └── ceps_distancias.csv   # Resultado da análise em CSV
# └── README.md                # Documentação do projeto
# ```

### Instruções para Uso:
1. **Instalar Dependências**:
   Execute:
   ```bash
   pip install -r requirements.txt
   ```

2. **Criação do CSV de Entrada**:
   Para a pasta `data/`, crie o arquivo `base_ceps.csv` contendo os CEPs:
   ```csv
   cep
   12345678
   87654321
   11223344
   ```

3. **Executar o Projeto**:
   Execute o código em `main.py` utilizando:
   ```bash
   python main.py
   ```

### Resultados Esperados:
A execução do script irá gerar um arquivo `ceps_distancias.csv`, que conterá as informações sobre a proximidade entre os CEPs e os shoppings, incluindo as distâncias calculadas.

### Conclusão:
A Crew ChizuKaki está agora totalmente implementada e pode processar dados de clientes em relação a shoppings de forma eficiente. As ferramentas e a estrutura de código foram otimizadas para facilitar manutenções futuras e ampliações.