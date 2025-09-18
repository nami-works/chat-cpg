from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from tools.validar_imports_tool import diagnosticar_imports

class ValidarImportsInput(BaseModel):
    caminho_codigo: str = Field(..., description="Caminho completo para o arquivo Python a ser inspecionado")

class ValidarImportsTool(BaseTool):
    name: str = "validar_imports_tool"
    description: str = "Valida os imports de um arquivo .py, retornando um dicionário com módulos e símbolos inválidos."
    args_schema: Type[BaseModel] = ValidarImportsInput

    def _run(self, caminho_codigo: str) -> str:
        resultado = diagnosticar_imports(caminho_codigo)
        return str(resultado)
