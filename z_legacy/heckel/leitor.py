from langchain_community.document_loaders import (WebBaseLoader,
                                                  YoutubeLoader, 
                                                  CSVLoader, 
                                                  PyPDFLoader, 
                                                  TextLoader)

url = ''
def leitor_sites(url):
    leitor = WebBaseLoader(url, raise_for_status=True)
    documento = leitor.load()
    resultado = '\n\n'.join([conteudo.page_content for conteudo in documento])
    return resultado

video_id = 'K4s6Cgicw_A'
def leitor_youtube(video_id):
    leitor = YoutubeLoader(video_id, add_video_info = False, language = ['pt'])
    documento = leitor.load()
    resultado = '\n\n'.join([conteudo.page_content for conteudo in documento])
    return resultado

caminho_pdf = "C:/Users/Lucas Guimarães/Downloads/WGSN x TikTok Shop.pdf"
def leitor_pdf(caminho_pdf):
    leitor = PyPDFLoader(caminho_pdf)
    documento = leitor.load()
    resultado = '\n\n'.join([conteudo.page_content for conteudo in documento])
    return resultado

caminho_csv = ''
def leitor_csv(caminho_csv):
    leitor = CSVLoader(file_path = caminho_csv, encoding = 'utf-8')
    documento = leitor.load()
    resultado = '\n\n'.join([conteudo.page_content for conteudo in documento])
    return resultado

caminho_txt = ''
def leitor_txt(caminho_txt):
    leitor = TextLoader(caminho_txt)
    documento = leitor.load()
    resultado = '\n\n'.join([conteudo.page_content for conteudo in documento])
    return resultado

resultado = leitor_pdf(caminho_pdf)
print(resultado)
