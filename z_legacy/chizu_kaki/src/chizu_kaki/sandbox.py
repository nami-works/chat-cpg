import requests
import pandas as pd
import sys
import warnings
from pathlib import Path

# from dotenv import load_dotenv
# from crew import ChizuKaki

from tools.custom_tool import CepValidationTool, GeoCodingTool, DistanceCalculatorTool, ReportGeneratorTool

# from geopy.distance import great_circle
# from typing import Any, Dict, List, Tuple

# warnings.filterwarnings("ignore", category=SyntaxWarning)

base_dir = Path(__file__).resolve().parent
base_ceps = base_dir / 'base_ceps_sample.csv'

# def run():
# ceps_shoppings = {
#     "Iguatemi Fortaleza": "60811341",
#     "Shopping Recife": "51020900",
#     "Shopping RioMar Recife": "51110160",
#     "Shops Jardins": "01414002",
#     "Shopping RioSul": "22290070"
# }

    # Carrega os dados dos CEPs do arquivo CSV.
base_ceps_df = pd.read_csv(base_ceps)

    # Validação dos CEPs na base de dados.
validacao_tool = CepValidationTool()
if not validacao_tool.run(base_ceps_df['cep'].tolist()):
    print("Erro: CEPs inválidos detectados.")

resultados = []


    # # Processa os CEPs, calculando distâncias e gerando resultados.
    # for cep in base_ceps_df['cep']:
    #     coordenadas_cliente = GeoCodingTool().run(cep)
    #     if not coordenadas_cliente:
    #         resultados.append((cep, "N/A", "N/A"))
    #         continue

    #     distancias = {}
    #     for shopping, shopping_cep in ceps_shoppings.items():
    #         coordenadas_shopping = GeoCodingTool().run(shopping_cep)
    #         if coordenadas_shopping:
    #             distancias[shopping] = DistanceCalculatorTool().run(
    #                 (coordenadas_cliente[1], coordenadas_cliente[2]),
    #                 (coordenadas_shopping[1], coordenadas_shopping[2])
    #             )

    #     shopping_proximo = min(distancias, key=distancias.get) if distancias else "N/A"
    #     distancia_proxima = distancias.get(shopping_proximo, "N/A")
    #     resultados.append((cep, shopping_proximo, distancia_proxima))

    # # Gera o relatório em CSV com os resultados.
    # caminho_csv = ReportGeneratorTool().run(resultados)
    # print(f"Relatório gerado com sucesso em {caminho_csv}.")

print (resultados)