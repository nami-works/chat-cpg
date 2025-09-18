import crewai_tools.tools.base
from os import path, listdir

class ReadMultiplePDFsTool(BaseTool):
    name = "leitor_pdf"
    description = "Lê todos os PDFs em uma pasta e retorna o conteúdo combinado."

    def __init__(self, pasta):
        super().__init__()
        self.pasta = pasta

    def _run(self, input: str = "") -> str:
        textos = []
        for arquivo in listdir(self.pasta):
            if arquivo.endswith(".pdf"):
                caminho = path.join(self.pasta, arquivo)
                leitor = ReadPDFTool(file_path=caminho)
                texto = leitor._run()
                textos.append(f"--- {arquivo} ---\n{texto}\n")
        return "\n".join(textos)
