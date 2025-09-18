import openai
import os
import requests

from dotenv import load_dotenv 
from typing import List, Tuple


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

def classificar_intencao(termos: List[str]) -> str:
    """
    Classifica a intenção de busca com base em palavras-chave.
    
    Parâmetros:
    termos (List[str]): Lista de termos para analisar.

    Retorno:
    str: Classificação da intenção ("informacional", "comercial", ou "indefinido").

    Exemplo:
    >>> classificar_intencao(["onde comprar", "como usar"])
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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um redator especialista em SEO."},
                {"role": "user", "content": f"Crie 5 títulos criativos e otimizados para blog sobre o tema: {tema}"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        texto = response['choices'][0]['message']['content']
        return [linha.strip('-• ') for linha in texto.split('\n') if linha.strip()]
    except Exception as e:
        print(f"❌ Erro em gerar_titulos_otimizados: {e}")
        return []

def salvar_como_markdown(dados: dict, caminho: str):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"# Campos Semânticos: {dados['palavra_chave_base']}\n\n")

        f.write("## 🔍 Palavras-chave relacionadas no Google\n")
        for item in dados['relacionadas_google']:
            f.write(f"- {item}\n")

        f.write("\n## 🎯 Intenção de Busca\n")
        f.write(f"- {dados['intencao_busca']}\n")

        f.write("\n## 🐍 Long-tail Keywords\n")
        for item in dados['long_tail_keywords']:
            f.write(f"- {item}\n")

        f.write("\n## 🧠 Títulos Sugeridos\n")
        for item in dados['titulos_sugeridos']:
            f.write(f"- {item}\n")

        f.write("\n## 🏷️ Headers (H1 e H2)\n")
        f.write(f"**H1:** {dados['h1']}\n")
        for h2 in dados['h2']:
            f.write(f"- H2: {h2}\n")

    print(f"✅ Arquivo salvo em: {caminho}")

def main():
    try:
        tema = "shampoo sem sulfato"
        suggestions = get_google_suggestions(tema)
        print(suggestions)
    except Exception as e:
        print(f"❌ Erro ao obter sugestões do Google: {e}")

    try:
        termos = ["onde comprar", "como usar"]
        intent = classificar_intencao(termos)
        print(intent)
    except Exception as e:
        print(f"❌ Erro na classificação da intenção: {e}")

    try:
        h1, h2 = gerar_headers("shampoo sem sulfato")
        print(h1)
        print(h2)
    except Exception as e:
        print(f"❌ Erro ao gerar headers: {e}")

    try:
        api_key = os.getenv('OPENAI_API_KEY')
        otimizados = gerar_titulos_otimizados("Os benefícios do shampoo sem sulfato", api_key)
        print(otimizados)
    except Exception as e:
        print(f"❌ Erro ao gerar títulos otimizados: {e}")

    resultado = {
        'palavra_chave_base': tema,
        'relacionadas_google': suggestions,
        'long_tail_keywords': suggestions,
        'intencao_busca': intent,
        'titulos_sugeridos': otimizados,
        'h1': h1,
        'h2': h2
    }

    salvar_como_markdown(resultado, "campos_semanticos.md")

if __name__ == "__main__":
    main()