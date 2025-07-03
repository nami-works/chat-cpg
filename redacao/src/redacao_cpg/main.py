#!/usr/bin/env python
import os
import shutil
import smtplib
import sys
import warnings
import zipfile
import streamlit as st
import re

from redacao.src.redacao_cpg.crew import Redacao_CPG
from datetime import date, datetime
from dotenv import load_dotenv
from email.message import EmailMessage
from pathlib import Path

load_dotenv()

email_de = os.getenv("EMAIL_USER")
email_de_nome = os.getenv("EMAIL_FROM_NAME")
email_senha = os.getenv("EMAIL_PASS")

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

base_dir = Path(__file__).resolve().parent

def sanitize_filename(filename):
    """
    Sanitize filename by removing invalid characters.
    Windows doesn't allow: < > : " | ? * \ /
    """
    # Remove invalid characters completely
    invalid_chars = r'[<>:"|?*\\/]'
    sanitized = re.sub(invalid_chars, '', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = 'untitled'
    
    # Limit length to avoid path too long errors
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized

def enviar_email(destinatario, assunto, corpo, anexos=None):
    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = f'{email_de_nome} <{email_de}'
    msg['To'] = destinatario
    msg.set_content(corpo)

    # Anexos opcionais
    if anexos:
        for arquivo in anexos:
            path = Path(arquivo)
            msg.add_attachment(path.read_bytes(), maintype='application', subtype='octet-stream', filename=path.name)

    # Autenticação
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_de, email_senha)  # Use senha de aplicativo, não sua senha normal
        smtp.send_message(msg)

def run(inputs):
    """
    Run the crew com inputs vindos do frontend.
    """
    temas = inputs['themes']
    estilo = inputs['style']
    marca = inputs['brand']
    produtos = inputs['products']
    blog = inputs['blog']
    benchmarks = inputs['benchmarks']
    recomendacoes_formato = inputs['format_recommendations']
    campos_semanticos = inputs['semantic_fields']
    pasta_marca = inputs['brand_folder']
    nome_macro = inputs.get('macro_name')
    if not nome_macro:
        nome_macro = datetime.now().strftime("%H_%M")

    # email_para = inputs['email_para']
    redacao_cpg = Redacao_CPG(pasta_marca)

    for nome, tema in temas.items():
        inputs_tema = {
            'estilo': estilo,
            'marca': marca,
            'nome' : nome,
            'tema': tema,
            'produtos': produtos,
            'blog': blog,
            'benchmarks': benchmarks,
            'recomendacoes_formato': recomendacoes_formato,
            'campos_semanticos': campos_semanticos,
        }
        
        try:
            redacao_cpg.crew().kickoff(inputs=inputs_tema)
            hoje = date.today().isoformat()
            pasta_posts = base_dir / pasta_marca / 'posts'
            onde_salvar = pasta_posts / f'{hoje}_{nome_macro}'
            os.makedirs(onde_salvar, exist_ok=True)
            
            # Sanitize the filename to avoid invalid characters
            safe_filename = sanitize_filename(nome)
            shutil.copy(pasta_posts / 'content.html', onde_salvar / f'{safe_filename}.html')
            shutil.copy(pasta_posts / 'metafields.md', onde_salvar / f'{safe_filename}_metafields.md')

            # enviar_email(
            # destinatario = email_para,
            # assunto=f'Post {nome} criado pelo ChatGEB',
            # corpo = f'O conteúdo para o tema \'{nome}\' está pronto. Seguem os arquivos em anexo.',
            # anexos=[
            #     tema_dir / 'conteudo.md',
            #     tema_dir / 'conteudo_refinado.md',
            #     tema_dir / 'metacampos.md'
            # ]
            # )

        except Exception as e:
            raise Exception(f"Erro ao rodar a crew para o tema {nome}: {e}")
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    # Create zip file of generated content
    zip_path = onde_salvar.with_suffix('.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in onde_salvar.glob('*'):
            zipf.write(file, file.name)
    
    # Create download link in UI
    st.markdown(f"### 📥 Download Content")
    with open(zip_path, 'rb') as f:
        st.download_button(
            label="Baixar conteúdos produzidos",
            data=f,
            file_name=f"{nome_macro}.zip",
            mime="application/zip"
        )

    # Remove temporary files
    os.remove(pasta_posts / 'semantic_fields.md')
    os.remove(pasta_posts / 'content.html') 
    os.remove(pasta_posts / 'metafields.md')
    os.remove(pasta_posts / 'themes.py')
    os.remove(pasta_posts / 'seo_themes.py')

    print(f"Conteúdo salvo em: {onde_salvar} e arquivos temporários apagados.")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'estilo': estilo,
        'marca': marca,
        'tema': 'Treine com qualquer tema da sua escolha',
        'produtos': produtos,
        'blog': blog,
        'benchmarks': benchmarks,
    }
    try:
        Redacao_CPG().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Redacao_CPG().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'estilo': estilo,
        'marca': marca,
        'tema': 'Teste com qualquer tema da sua escolha',
        'produtos': produtos,
        'blog': blog,
        'benchmarks': benchmarks,
    }
    try:
        Redacao_CPG().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def escrever(inputs):
    run(inputs) 