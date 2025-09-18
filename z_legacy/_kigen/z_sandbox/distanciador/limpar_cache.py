import json
import os

# Caminho do cache
cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'coordenadas_cache.json')

with open(cache_path, 'r', encoding='utf-8') as f:
    cache = json.load(f)

# Filtra apenas os válidos
cache_limpo = {
    cep: coords for cep, coords in cache.items()
    if coords and coords != [None, None]
}

# Sobrescreve o arquivo com os válidos
with open(cache_path, 'w', encoding='utf-8') as f:
    json.dump(cache_limpo, f, ensure_ascii=False, indent=2)

print(f"Cache limpo: {len(cache)} → {len(cache_limpo)} entradas válidas.")