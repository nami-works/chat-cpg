import pandas as pd
import os
import json
import time
import random
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import Dict, Tuple

# Diretório base para salvar o cache junto ao script
base_dir = os.path.dirname(os.path.abspath(__file__))
cache_path = os.path.join(base_dir, 'coordenadas_cache.json')

# Coordenadas conhecidas dos shoppings
shoppings_coords = {
    'Iguatz': (-3.777757, -38.481135),
    'RioMar': (-8.087457, -34.891664),
    'RioSul': (-22.956909, -43.176186),
    'Shopping Recife': (-8.117044, -34.901358),
    'Shops Jardins': (-23.564738, -46.668939),
}

# -------------------- Funcoes utilitarias --------------------

def carregar_cache() -> Dict[str, Tuple[float, float]]:
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_cache(cache: Dict[str, Tuple[float, float]]):
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def obter_coordenadas(cep: str, cache: Dict[str, Tuple[float, float]]) -> Tuple[float, float]:
    if cep in cache:
        return cache[cep]

    geolocator = Nominatim(user_agent='distanciador_kigen')
    try:
        location = geolocator.geocode({'postalcode': cep, 'country': 'Brazil'}, timeout=10)
        coords = (location.latitude, location.longitude) if location else (None, None)
    except Exception:
        coords = (None, None)

    if coords != (None, None):
        cache[cep] = coords
        salvar_cache(cache)
    time.sleep(3 + random.random())
    return coords

def calcular_distancia(coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
    return round(geodesic(coords1, coords2).km, 2)

# -------------------- Processo principal --------------------

def processar_planilha(csv_path: str, max_iteracoes: int = 50):
    cache = carregar_cache()

    for iteracao in range(max_iteracoes):
        df = pd.read_csv(csv_path, dtype=str)
        df['cep'] = df['cep'].astype(str).str.strip().str.zfill(8)


        for shopping in shoppings_coords:
            if shopping not in df.columns:
                df[shopping] = ''

        if 'Shopping Mais Proximo' not in df.columns:
            df['Shopping Mais Proximo'] = ''

        if 'Estimado Por Proximidade' not in df.columns:
            df['Estimado Por Proximidade'] = ''

        colunas_dist = list(shoppings_coords.keys())
        colunas_todas = colunas_dist + ['Shopping Mais Proximo', 'Estimado Por Proximidade']
        pendentes = df[df[colunas_todas].isna().any(axis=1) | df[colunas_todas].eq('').any(axis=1)]

        if pendentes.empty:
            print("✅ Nenhum CEP pendente restante.")
            break

        inicio_iteracao = time.time()
        for idx, row in pendentes.iterrows():
            cep = row['cep']
            coords = obter_coordenadas(cep, cache)

            #Busca coordenadas do CEP mais próximo
            if None not in coords and df.at[idx, 'Estimado Por Proximidade'] == 'sim':
                for col in colunas_todas:
                    df.at[idx, col] = ''
                df.at[idx, 'Estimado Por Proximidade'] = ''       
            if None in coords:
                prefixo = cep[:7]
                similares = df[
                    (df['cep'].str.startswith(prefixo)) &
                    (df[colunas_todas].notna().all(axis=1)) &
                    (df[colunas_todas].ne('').all(axis=1))
                ]

                if not similares.empty:
                    for shopping in shoppings_coords:
                        df.at[idx, shopping] = similares.iloc[0][shopping]
                    df.at[idx, 'Shopping Mais Proximo'] = similares.iloc[0]['Shopping Mais Proximo']
                    df.at[idx, 'Estimado Por Proximidade'] = 'sim'  # <- AQUI indicamos que foi uma estimativa
                    continue

            distancias = {}
            for shopping, coords_shop in shoppings_coords.items():
                distancia = calcular_distancia(coords, coords_shop)
                df.at[idx, shopping] = distancia
                distancias[shopping] = distancia
            shopping_proximo = min(distancias, key=distancias.get)
            df.at[idx, 'Shopping Mais Proximo'] = shopping_proximo

        df.to_csv(csv_path, index=False)

        pendentes_restantes = df[df[colunas_todas].isna().any(axis=1) | df[colunas_todas].eq('').any(axis=1)]
        duracao = time.time() - inicio_iteracao
        ceps_processados = len(pendentes) - len(pendentes_restantes)
        if ceps_processados > 0:
            tempo_medio = duracao / ceps_processados
            estimado_restante = tempo_medio * len(pendentes_restantes)
            minutos, segundos = divmod(int(estimado_restante), 60)
            print(f'⏳ Estimativa de tempo restante: {minutos} min {segundos} s')
        else:
            print('⚠️ Nenhum CEP processado nesta rodada. Não é possível estimar o tempo.')

        print(f"🔁 Iteracao {iteracao + 1} concluida. CEPs ainda pendentes apos esta rodada: {len(pendentes_restantes)}")

if __name__ == "__main__":
    base_path = os.path.join(base_dir, 'base_ceps.csv')
    processar_planilha(base_path)
