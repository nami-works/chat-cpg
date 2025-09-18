import requests
import openai
from typing import List, Tuple

def get_google_suggestions(tema: str) -> List[str]:
    """
    Retorna sugestões de busca do Google relacionadas ao tema fornecido.
    
    Parâmetros:
    tema (str): O tema para buscar sugestões.

    Retorno:
    List[str]: Lista de sugestões de busca.

    Exemplo:
    >>> get_google_suggestions("python")
    ['python tutorial', 'python api', 'python examples']
    """
    try:
        url = f"https://www.google.com/complete/search?q={tema}&client=firefox"
        response = requests.get(url)
        suggestions = response.json()[1]  # Pega a lista de sugestões
        return suggestions
    except Exception as e:
        print(f"❌ Erro em get_google_suggestions: {e}")
        return []

def classificar_intencao(termos: List[str]) -> str:
    """
    Classifica a intenção de busca com base em palavras-chave.
    
    Parâmetros:
    termos (List[str]): Lista de termos para analisar.

    Retorno:
    str: Classificação da intenção ("informacional", "comercial", ou "indefinido").

    Exemplo:
    >>> classificar_intencao(["comprar carros", "como dirigir"])
    'comercial'
    """
    informacionais = ["como", "o que", "onde"]
    comerciais = ["comprar", "preço", "onde encontrar"]

    for termo in termos:
        if any(suffix in termo for suffix in informacionais):
            return "informacional"
        elif any(suffix in termo for suffix in comerciais):
            return "comercial"
    return "indefinido"

def gerar_headers(titulo_base: str) -> Tuple[str, List[str]]:
    """
    Gera um título H1 e uma lista de subtítulos H2 a partir do título base fornecido.
    
    Parâmetros:
    titulo_base (str): O título base para gerar headers.

    Retorno:
    Tuple[str, List[str]]: O título H1 e lista de subtítulos H2.

    Exemplo:
    >>> gerar_headers("python")
    ('Tudo sobre python', ['Para que serve python?', 'Como usar python?', 'Vantagens e Cuidados com python'])
    """
    h1 = f"Tudo sobre {titulo_base}"
    h2 = [f"Para que serve {titulo_base}?", f"Como usar {titulo_base}?", f"Vantagens e Cuidados com {titulo_base}"]
    return h1, h2

def gerar_titulos_otimizados(tema: str, api_key: str) -> List[str]:
    """
    Retorna títulos otimizados para blogs utilizando uma API de modelos de linguagem.
    
    Parâmetros:
    tema (str): O tema para gerar títulos.
    api_key (str): A chave da API do OpenAI.

    Retorno:
    List[str]: Lista de títulos otimizados.

    Exemplo:
    >>> gerar_titulos_otimizados("Python para iniciantes", "sua_chave_api")
    ['Aprenda Python do Zero', 'Python: Guia Completo para Iniciantes']
    """
    openai.api_key = api_key
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Crie títulos criativos sobre: {tema}",
            max_tokens=50
        )
        return response.choices[0].text.strip().split('\n')
    except Exception as e:
        print(f"❌ Erro em gerar_titulos_otimizados: {e}")
        return []

def main():
    try:
        tema = "python"
        suggestions = get_google_suggestions(tema)
        print(suggestions)
    except Exception as e:
        print(f"❌ Erro ao obter sugestões do Google: {e}")

    try:
        termos = ["comprar carros", "como dirigir"]
        intent = classificar_intencao(termos)
        print(intent)
    except Exception as e:
        print(f"❌ Erro na classificação da intenção: {e}")

    try:
        h1, h2 = gerar_headers("python")
        print(h1)
        print(h2)
    except Exception as e:
        print(f"❌ Erro ao gerar headers: {e}")

    try:
        api_key = "sua_chave_api"
        otimizados = gerar_titulos_otimizados("Python para iniciantes", api_key)
        print(otimizados)
    except Exception as e:
        print(f"❌ Erro ao gerar títulos otimizados: {e}")

if __name__ == "__main__":
    main()