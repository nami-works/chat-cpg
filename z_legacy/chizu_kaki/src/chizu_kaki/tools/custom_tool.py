import requests
import pandas as pd
from geopy.distance import great_circle
from typing import Any, Dict, List, Tuple

# class CepValidationTool:
#     def run(self, ceps: List[str]) -> bool:
#         return all(
#             isinstance(cep, str) and
#             len(cep.replace('-', '').strip()) == 8 and
#             cep.replace('-', '').strip().isdigit()
#             for cep in ceps
#         )

class GeoCodingTool:
#     def run(self, cep: str) -> Tuple[str, float, float]:
#         response = requests.get(f'https://viacep.com.br/ws/{cep}/json/')
#         if response.status_code != 200 or 'erro' in response.json():
#             return None
#         data = response.json()
#         return (data['cep'], float(data['latitude']), float(data['longitude']))

    def run(self, cep: str) -> Tuple[str, float, float]:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': cep,
            'country': 'Brazil',
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'chizu-kaki/1.0'
        }

    # def run(self, cep: str) -> Tuple[str, float, float]:
    #     url = "https://nominatim.openstreetmap.org/search"
    #     params = {
    #         'q': f'{cep}, 'Brazil',
    #         'format': 'json',
    #         'limit': 1
    #     }
    #     headers = {
    #         'User-Agent': 'chizu-kaki/1.0'
    #     }

        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            return None

        data = response.json()
        if not data:
            return None

        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return (cep, lat, lon)

class DistanceCalculatorTool:
    def run(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        return round(great_circle(coord1, coord2).km, 2)

class ReportGeneratorTool:
    def run(self, data: List[Tuple[str, str, float]]) -> str:
        df = pd.DataFrame(data, columns=['cep', 'shopping_mais_proximo', 'distancia_km'])
        caminho_csv = 'ceps_distancias.csv'
        df.to_csv(caminho_csv, index=False)
        return caminho_csv