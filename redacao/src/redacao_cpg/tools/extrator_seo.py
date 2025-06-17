import os
import requests
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI
from typing import Literal, List, Tuple
from pathlib import Path

load_dotenv()

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

def classificar_intencao(tema: str, api_key: str) -> str:
    """
    Classifica a intenção de busca utilizando uma API de modelos de linguagem.

    Parâmetros:
    tema (str): O tema para analisar.
    api_key (str): A chave da API do OpenAI.

    Retorno:
    str: Classificação da intenção ("informacional", "comercial", ou "indefinido").

    Exemplo:
    >>> classificar_intencao("Como escolher shampoo sem sulfato", "sua_chave_api")
    'informacional'
    """
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=api_key
        )
        
        response = llm.invoke(
            f"Classifique a seguinte intenção de busca como 'informacional', 'comercial' ou 'indefinido':\n\n"
            f"Tema: {tema}\n\n"
            "Responda apenas com a palavra correspondente."
        )
        return response.content.strip().lower()
    except Exception as e:
        print(f"❌ Erro em classificar_intencao: {e}")
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
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key
        )
        
        response = llm.invoke(
            f"Crie 2 títulos criativos e otimizados para blog sobre o tema: {tema}"
        )
        texto = response.content
        return [linha.strip('-• ') for linha in texto.split('\n') if linha.strip()]
    except Exception as e:
        print(f"❌ Erro em gerar_titulos_otimizados: {e}")
        return []

def gerar_campos_semanticos(tema: str) -> dict:
    return {
        'palavra_chave_base': tema,
        'relacionadas_google': get_google_suggestions(tema),
        'long_tail_keywords': get_google_suggestions(tema),
        'intencao_busca': classificar_intencao(get_google_suggestions(tema)),
        'titulos_sugeridos': gerar_titulos_otimizados(tema, os.getenv('OPENAI_API_KEY')),
        'h1': gerar_headers(tema)[0],
        'h2': gerar_headers(tema)[1]
    }

def extrair_seo(tema: str) -> dict:
    try:
        suggestions = get_google_suggestions(tema)
    except Exception as e:
        print(f"❌ Erro ao obter sugestões do Google: {e}")
        suggestions = []

    try:
        api_key = os.getenv('OPENAI_API_KEY')
        intent = classificar_intencao(tema, api_key)
    except Exception as e:
        print(f"❌ Erro na classificação da intenção: {e}")
        intent = "indefinido"

    try:
        h1, h2 = gerar_headers(tema)
    except Exception as e:
        print(f"❌ Erro ao gerar headers: {e}")
        h1, h2 = "", []

    try:
        api_key = os.getenv('OPENAI_API_KEY')
        otimizados = gerar_titulos_otimizados(tema, api_key)
    except Exception as e:
        print(f"❌ Erro ao gerar títulos otimizados: {e}")
        otimizados = []

    return {
        'palavra_chave_base': tema,
        'relacionadas_google': suggestions,
        'intencao_busca': intent,
        'long_tail_keywords': suggestions,
        'titulos_sugeridos': otimizados,
        'h1': h1,
        'h2': h2
    }

if __name__ == "__main__":
    extrair_seo()