import ast
import importlib
from pathlib import Path

def diagnosticar_imports(caminho_codigo: str) -> dict:
    """
    Lê um arquivo .py e retorna os imports inválidos encontrados no formato:
    {
        "modulo": ["simbolo1", "simbolo2"]
    }
    """
    caminho = Path(caminho_codigo)
    if not caminho.exists():
        return {"erro": "Arquivo não encontrado"}

    with open(caminho, "r", encoding="utf-8") as f:
        codigo = f.read()

    tree = ast.parse(codigo)
    erros = {}

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            modulo = node.module
            for alias in node.names:
                nome = alias.name
                try:
                    mod = importlib.import_module(modulo)
                    if not hasattr(mod, nome):
                        raise AttributeError
                except (ModuleNotFoundError, AttributeError):
                    erros.setdefault(modulo, []).append(nome)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                nome = alias.name
                try:
                    importlib.import_module(nome)
                except ModuleNotFoundError:
                    erros.setdefault(nome, []).append("*")

    return erros
