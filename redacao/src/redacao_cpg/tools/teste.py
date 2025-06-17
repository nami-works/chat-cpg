from serpapi import GoogleSearch

params = {
    "engine": "google",
    "q": "hidratação capilar",
    "api_key": "SUA_CHAVE_REAL_AQUI"
}

search = GoogleSearch(params)
results = search.get_dict()
print(results)
