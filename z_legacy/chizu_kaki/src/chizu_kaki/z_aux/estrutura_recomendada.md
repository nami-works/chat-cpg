```markdown
# Estrutura de Diretórios e Arquivos da Crew ChizuKaki

## 🎯 Objetivo
A Crew ChizuKaki foi desenvolvida para avaliar a proximidade entre uma base de CEPs e uma lista fixa de shoppings, convertendo CEPs em coordenadas geográficas, calculando distâncias e gerando relatórios eficazes.

---

## 🗂 Estrutura de Diretórios

```
chizukaki/
│
├── agents.py                # Implementações das ferramentas da Crew
├── main.py                  # Script principal que orquestra a execução
├── requirements.txt         # Dependências do projeto
├── data/                    # Pasta para armazenar dados
│   ├── base_ceps.csv        # Arquivo CSV de entrada com CEPs
│   └── ceps_distancias.csv   # Resultado da análise em CSV
└── README.md                # Documentação do projeto
```

---

## 🛠️ Implementação do Código

### 1. agents.py

Aqui estão as implementações das ferramentas que serão utilizadas pela Crew ChizuKaki:

```python
import requests
import pandas as pd
from geopy.distance import great_circle
from typing import Any, Dict, List, Tuple

class CepValidationTool:
    def run(self, ceps: List[str]) -> bool:
        """ Valida os CEPs fornecidos. """
        return all(isinstance(cep, str) and len(cep) == 8 and cep.isdigit() for cep in ceps)

class GeoCodingTool:
    def run(self, cep: str) -> Tuple[str, float, float]:
        """ Consulta a API ViaCEP para obter coordenadas do CEP. """
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
        if response.status_code != 200 or 'erro' in response.json():
            return None
        data = response.json()
        return (data['cep'], float(data['latitude']), float(data['longitude']))

class DistanceCalculatorTool:
    def run(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """ Calcula a distância geodésica entre duas coordenadas. """
        return round(great_circle(coord1, coord2).km, 2)

class ReportGeneratorTool:
    def run(self, data: List[Tuple[str, str, float]]) -> str:
        """ Gera um CSV com os resultados das distâncias calculadas. """
        df = pd.DataFrame(data, columns=['cep', 'shopping_mais_proximo', 'distancia_km'])
        caminho_csv = 'data/ceps_distancias.csv'
        df.to_csv(caminho_csv, index=False)
        return caminho_csv
```

### 2. main.py

Este arquivo controla a execução geral da aplicação:

```python
def main():
    ceps_shoppings = {
        "Shopping A": "12345678",
        "Shopping B": "87654321",
        "Shopping C": "11223344",
    }

    # Carrega os dados dos CEPs
    base_ceps_df = pd.read_csv('data/base_ceps.csv')

    # Valida CEPs da base
    validacao_tool = CepValidationTool()
    if not validacao_tool.run(base_ceps_df['cep'].tolist()):
        print("Erro: CEPs inválidos detectados.")
        return

    resultados = []
    # Pixando coordenadas e distâncias
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

    # Gera o relatório
    caminho_csv = ReportGeneratorTool().run(resultados)
    print(f"Relatório gerado com sucesso em {caminho_csv}.")

if __name__ == "__main__":
    main()
```

### 3. requirements.txt

As dependências necessárias para executar o projeto:

```
requests
pandas
geopy
```

---

## 📊 Aplicações da Crew ChizuKaki
- **Logística e Roteirização**: Identificação do shopping mais próximo para otimizar entregas.
- **Marketing Geográfico**: Direcionamento de campanhas com base na localização dos clientes.
- **Planejamento de Expansão**: Decisões sobre novos shoppings baseadas na proximidade com os clientes.
- **Recomendação Personalizada**: Ofertas específicas para clientes com base na proximidade a shoppings.

---

## 🔧 Instruções de Uso

1. **Instalar Dependências**:
   Execute o comando:
   ```bash
   pip install -r requirements.txt
   ```

2. **Criação do CSV de Entrada**:
   Crie e coloque seu arquivo `base_ceps.csv` na pasta `data`.

3. **Executar o Projeto**:
   Execute o script principal:
   ```bash
   python main.py
   ```

---

## 📜 Documentação
Para mais informações sobre o projeto, consulte o arquivo `README.md`, onde detalhes adicionais e instruções podem ser encontrados.

---

Com essa organização, a Crew ChizuKaki estará encapsulada de forma modular e eficiente, pronta para execução e manutenção em projetos que envolvem a análise de proximidade geográfica.