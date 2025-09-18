```python
import os
import json
import pdfplumber
from docling import Doc
from unstructured.documents import Document
import spacy
from langchain.llms import LLM
import streamlit as st
from typing import Dict, List, Optional

# Carregando modelo spaCy para a categorização
nlp = spacy.load("pt_core_news_md")

def varrer_diretorio(caminho_diretorio: str) -> List[str]:
    """
    Faz a varredura no diretório especificado e retorna uma lista de todos os arquivos encontrados.

    Parâmetros:
    caminho_diretorio (str): O caminho do diretório onde a varredura será realizada.

    Retorno:
    List[str]: Uma lista com os caminhos completos dos arquivos encontrados.

    Exemplo:
    >>> arquivos = varrer_diretorio('/caminho/para/diretorio')
    >>> print(arquivos)
    ['/caminho/para/diretorio/arquivo1.txt', '/caminho/para/diretorio/arquivo2.pdf']
    """
    arquivos = []
    try:
        for pasta, _, arquivos_na_pasta in os.walk(caminho_diretorio):
            for arquivo in arquivos_na_pasta:
                arquivos.append(os.path.join(pasta, arquivo))
    except Exception as e:
        print(f"❌ Erro na função varrer_diretorio: {e}")
    return arquivos

def extrair_conteudo(caminho_arquivo: str) -> Optional[str]:
    """
    Extrai o conteúdo do arquivo especificado utilizando Docling, pdfplumber ou unstructured.

    Parâmetros:
    caminho_arquivo (str): O caminho do arquivo do qual o conteúdo será extraído.

    Retorno:
    Optional[str]: O conteúdo extraído do arquivo ou None se falhar.

    Exemplo:
    >>> conteudo = extrair_conteudo('/caminho/para/arquivo.pdf')
    >>> print(conteudo)
    'Este é o conteúdo do meu arquivo.'
    """
    try:
        if caminho_arquivo.endswith('.pdf'):
            with pdfplumber.open(caminho_arquivo) as pdf:
                conteudo = ""
                for pagina in pdf.pages:
                    texto = pagina.extract_text()
                    if texto:
                        conteudo += texto
                return conteudo
        elif caminho_arquivo.endswith('.docx'):
            return Doc.extract(caminho_arquivo)  # Verifique se a biblioteca 'docling' está corretamente instalada.
        elif caminho_arquivo.endswith('.txt'):
            doc = Document.from_file(caminho_arquivo)
            return doc.content
    except Exception as e:
        print(f"❌ Erro na função extrair_conteudo: {e}")
        return None

def analisar_e_categorizar(conteudo: str, nome_arquivo: str) -> Dict:
    """
    Analisa o conteúdo e nome do arquivo, retornando um dicionário com categorias semânticas associadas.

    Parâmetros:
    conteudo (str): O conteúdo a ser analisado.
    nome_arquivo (str): O nome do arquivo, que pode ser usado para categorizar.

    Retorno:
    Dict: Dicionário com categorias encontradas no conteúdo.

    Exemplo:
    >>> categorias = analisar_e_categorizar("Esse é o conteúdo do arquivo.", "arquivo_exemplo")
    >>> print(categorias)
    {'entidade': 'EXEMPLO', ...}
    """
    try:
        doc = nlp(conteudo)
        categorias = {ent.text: ent.label_ for ent in doc.ents}
        return categorias
    except Exception as e:
        print(f"❌ Erro na função analisar_e_categorizar: {e}")
        return {}

def gerar_base_conhecimento(dados: Dict) -> Dict:
    """
    Gera uma base de conhecimento estruturada em formato JSON com as categorias e metadados recebidos.

    Parâmetros:
    dados (Dict): Dicionário com dados a serem salvos.

    Retorno:
    Dict: O dicionário de entrada.

    Exemplo:
    >>> dados = {'categoria1': 'valor1', 'categoria2': 'valor2'}
    >>> gerar_base_conhecimento(dados)
    {'categoria1': 'valor1', 'categoria2': 'valor2'}
    """
    try:
        with open('base_conhecimento.json', 'w') as f:
            json.dump(dados, f)
        return dados
    except Exception as e:
        print(f"❌ Erro na função gerar_base_conhecimento: {e}")
        return {}

def consultar_base_conhecimento(pergunta: str, base_conhecimento: Dict) -> str:
    """
    Consulta a base de conhecimento e retorna a resposta mais relevante para a pergunta do usuário.

    Parâmetros:
    pergunta (str): A pergunta a ser consultada.
    base_conhecimento (Dict): A base de conhecimento a ser consultada.

    Retorno:
    str: A resposta encontrada.

    Exemplo:
    >>> resposta = consultar_base_conhecimento("Qual é a categoria do item?", {"categoria": "valor"})
    >>> print(resposta)
    'valor'
    """
    try:
        resposta = LLM.query(pergunta, base_conhecimento)  # Verifique se a biblioteca 'LangChain' está corretamente instalada e configurada.
        return resposta
    except Exception as e:
        print(f"❌ Erro na função consultar_base_conhecimento: {e}")
        return "Desculpe, não consegui encontrar uma resposta."

def exibir_interface_consulta(base_conhecimento: Dict):
    """
    Cria uma interface de consulta utilizando Streamlit para que o usuário possa fazer perguntas.

    Parâmetros:
    base_conhecimento (Dict): A base de conhecimento a ser consultada.

    Retorno:
    None

    Exemplo:
    >>> exibir_interface_consulta({"categoria": "valor"})
    (executado em Streamlit)
    """
    try:
        pergunta = st.text_input("Faça sua pergunta:")
        if pergunta:
            resposta = consultar_base_conhecimento(pergunta, base_conhecimento)
            st.write(resposta)
    except Exception as e:
        print(f"❌ Erro na função exibir_interface_consulta: {e}")

def main():
    """
    Função principal que orquestra o fluxo da aplicação.
    """
    base_conhecimento = {}

    try:
        caminho_diretorio = '/caminho/para/diretorio'  # Definindo o caminho do diretório
        arquivos = varrer_diretorio(caminho_diretorio)
    except Exception as e:
        print(f"❌ Erro na função main ao varrer diretório: {e}")
        arquivos = []

    for arquivo in arquivos:
        try:
            conteudo = extrair_conteudo(arquivo)
            if conteudo:
                categorias = analisar_e_categorizar(conteudo, arquivo)
                base_conhecimento.update(categorias)
        except Exception as e:
            print(f"❌ Erro na função main ao processar o arquivo {arquivo}: {e}")

    try:
        gerar_base_conhecimento(base_conhecimento)
    except Exception as e:
        print(f"❌ Erro na função main ao gerar a base de conhecimento: {e}")

    try:
        exibir_interface_consulta(base_conhecimento)
    except Exception as e:
        print(f"❌ Erro na função main ao exibir a interface de consulta: {e}")

if __name__ == "__main__":
    main()
```