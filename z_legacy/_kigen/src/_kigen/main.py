import json
import os
import shutil
import sys
import warnings

from crew import Kigen
from dotenv import load_dotenv
from executar_solucao import executar_solucao
from pathlib import Path
from rich import print

warnings.filterwarnings("ignore", category=SyntaxWarning)

base_dir = Path(__file__).resolve().parent

contexto = base_dir / 'inputs/0_contexto.json'
with open(contexto, 'r', encoding='utf-8') as file:
    instrucoes = json.load(file)

briefing = base_dir / 'inputs/briefing.md'
with open(briefing, 'r', encoding='utf-8') as file:
    problema = file.read()
with open(briefing, 'r', encoding='utf-8') as file:
    nome = file.readline().strip()

log_execucao_m = base_dir / 'inputs/modelos/log_execucao.md'
with open(log_execucao_m, 'r', encoding='utf-8') as file:
    modelo_log_execucao = file.read()

log_correcao_m = base_dir / 'inputs/modelos/log_correcao.md'
with open(log_correcao_m, 'r', encoding='utf-8') as file:
    modelo_log_correcao = file.read()

relatorio_auditoria_m = base_dir / 'inputs/modelos/relatorio_auditoria.md'
with open(relatorio_auditoria_m, 'r', encoding='utf-8') as file:
    modelo_relatorio_auditoria = file.read()
    
status_ambiente_m = base_dir / 'inputs/modelos/status_ambiente.md'
with open(status_ambiente_m, 'r', encoding='utf-8') as file:
    modelo_status_ambiente = file.read()

# Fontes Python e bibliotecas
python_docs = 'https://docs.python.org/3/'
python_patterns = 'https://github.com/faif/python-patterns'
awesome_python = 'https://github.com/vinta/awesome-python'

# Fontes específicas das bibliotecas prioritárias
docling_docs = 'https://pypi.org/project/docling/'
langchain_docs = 'https://docs.langchain.com/docs/'
streamlit_docs = 'https://docs.streamlit.io/'

# Fontes gerais
bibliotecas = 'https://pypi.org/'
github = 'https://github.com/'
stack_overflow = 'https://stackoverflow.com/'

# Fontes CrewAI
crewai_documentacao = 'https://docs.crewai.com/docs'
crewai_conceitos = 'https://docs.crewai.com/concepts/'
crewai_crews = 'https://docs.crewai.com/concepts/crews'

def run_kigen():
    """
    Run the diagnostic crew to evaluate the type of solution.
    """
    inputs = {
        'instrucoes': instrucoes,
        'problema': problema,
        'crewai_documentacao': crewai_documentacao,
        'crewai_conceitos': crewai_conceitos,
        'crewai_crews': crewai_crews,
        'python_docs': python_docs,
        'python_patterns': python_patterns,
        'awesome_python': awesome_python,
        'docling_docs': docling_docs,
        'langchain_docs': langchain_docs,
        'streamlit_docs': streamlit_docs,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
    }

    try:
        Kigen().crew_kigen().kickoff(inputs=inputs)
        outputs_dir = base_dir / 'outputs' # Pasta dentro de src onde são salvos os outputs
        projeto_dir = base_dir.parent.parent # Pasta fora de src
        codigo_dir = projeto_dir / 'z_sandbox' / nome # Pasta fora de src dentro do projeto
        os.makedirs(codigo_dir, exist_ok=True)
        shutil.copy(outputs_dir / 'recomendacao.md', codigo_dir / 'recomendacao.md')

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_codigo():
    """
    Run the solution crew based on the recommendation.
    """
    # Recomendação de solução gerada pelas etapas iniciais
    recomendacao = base_dir / 'outputs/recomendacao.md'
    with open(recomendacao, 'r', encoding='utf-8') as file:
        solucao = file.read()

    inputs = {
        'instrucoes': instrucoes,
        'problema': problema,
        'crewai_documentacao': crewai_documentacao,
        'crewai_conceitos': crewai_conceitos,
        'crewai_crews': crewai_crews,
        'python_docs': python_docs,
        'python_patterns': python_patterns,
        'awesome_python': awesome_python,
        'docling_docs': docling_docs,
        'langchain_docs': langchain_docs,
        'streamlit_docs': streamlit_docs,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
        'solucao': solucao,
    }

    if 'criar_funcoes' in solucao:
        print("▶️ Solução indicada: criar funções. Executando geração de funções...")

        try:
            Kigen().crew_codigo().kickoff(inputs=inputs)
 
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")
    else:
        print("❌ Solução exige criação de crew personalizada, mas a criação de crews ainda não está configurada")

def run_depuracao():
    """
    Run the depuration crew based on the code developed.
    """
    # Caminhos base
    base_dir = Path(__file__).resolve().parent

    codigo = base_dir / 'outputs' / 'codigo_v2.py'
    requirements = base_dir / 'outputs' / 'requirements.txt'

    executar_solucao(codigo, requirements)

    recomendacao = base_dir / 'outputs/recomendacao.md'
    with open(recomendacao, 'r', encoding='utf-8') as file:
        solucao = file.read()

    arquivo_log = base_dir / 'outputs' / 'log_execucao.md'
    with open(arquivo_log, 'r', encoding='utf-8') as file:
        log_execucao = file.read()

    arquivo_codigo = base_dir / 'outputs' / 'codigo_v2.py'
    with open(arquivo_codigo, 'r', encoding='utf-8') as file:
        codigo_a_depurar = file.read()

    inputs = {
        'instrucoes': instrucoes,
        'problema': problema,
        'crewai_documentacao': crewai_documentacao,
        'crewai_conceitos': crewai_conceitos,
        'crewai_crews': crewai_crews,
        'python_docs': python_docs,
        'python_patterns': python_patterns,
        'awesome_python': awesome_python,
        'docling_docs': docling_docs,
        'langchain_docs': langchain_docs,
        'streamlit_docs': streamlit_docs,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
        'solucao': solucao,
        'codigo': codigo_a_depurar,
        'log_execucao': log_execucao
    }

    try:
        arquivo_codigo = base_dir / 'outputs' / 'codigo_v2.py'
        with open(arquivo_codigo, 'r', encoding='utf-8') as file:
            codigo_a_depurar = file.read()

        arquivo_requirements = base_dir / 'outputs' / 'requirements.txt'
        with open(arquivo_requirements, 'r', encoding='utf-8') as file:
            requirements_a_avaliar = file.read()

        arquivo_log = base_dir / 'outputs' / 'log_execucao.md'
        with open(arquivo_log, 'r', encoding='utf-8') as file:
            log_execucao = file.read()

        novos_inputs = {
            'codigo': codigo_a_depurar,
            'requirements': requirements_a_avaliar,
            'log_execucao': log_execucao
        }

        inputs.update(novos_inputs)

        Kigen().crew_depuracao().kickoff(inputs=inputs)

        max_tentativas = 7
        tentativas = 0

        while '❌ A execução foi finalizada com erros.' in log_execucao and tentativas < max_tentativas:
            tentativas += 1
            print(f'Tentativa {tentativas} de {max_tentativas}')

            codigo = base_dir / 'outputs' / 'codigo_v3.py'
            
            requirements = base_dir / 'outputs' / 'requirements.txt'

            executar_solucao(codigo, requirements)

            arquivo_log = base_dir / 'outputs' / 'log_execucao.md'
            with open(arquivo_log, 'r', encoding='utf-8') as file:
                log_execucao = file.read()

            arquivo_codigo = base_dir / 'outputs' / 'codigo_v3.py'
            with open(arquivo_codigo, 'r', encoding='utf-8') as file:
                codigo_a_depurar = file.read()

            arquivo_requirements = base_dir / 'outputs' / 'requirements.txt'
            with open(arquivo_requirements, 'r', encoding='utf-8') as file:
                requirements_a_avaliar = file.read()

            novos_inputs = {
                'codigo': codigo_a_depurar,
                'requirements': requirements_a_avaliar,
                'log_execucao': log_execucao
            }

            inputs.update(novos_inputs)

            Kigen().crew_depuracao().kickoff(inputs=inputs)

            inputs_dir = base_dir / 'inputs' # Pasta dentro de src onde foram salvos os inputs
            outputs_dir = base_dir / 'outputs' # Pasta dentro de src onde serão salvos os outputs
            projeto_dir = base_dir.parent.parent # Pasta fora de src
            codigo_dir = projeto_dir / 'z_sandbox' / nome # Pasta fora de src dentro do projeto
            os.makedirs(codigo_dir, exist_ok=True)
            shutil.copy(inputs_dir / 'briefing.md', codigo_dir / 'briefing.md')
            shutil.copy(outputs_dir / 'recomendacao.md', codigo_dir / 'recomendacao.md')
            shutil.copy(outputs_dir / 'inputs.md', codigo_dir / 'inputs.md')
            shutil.copy(outputs_dir / 'modelo_input.csv', codigo_dir / 'modelo_input.csv')
            shutil.copy(outputs_dir / 'codigo_v1.py', codigo_dir / 'codigo_v1.py')
            shutil.copy(outputs_dir / 'codigo_v2.py', codigo_dir / 'codigo_v2.py')
            shutil.copy(outputs_dir / 'codigo_v3.py', codigo_dir / 'codigo_v3.py')
            shutil.copy(outputs_dir / 'requirements.txt', codigo_dir / 'requirements.txt')
          
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'instrucoes': instrucoes,
        'problema': problema,
        'crewai_documentacao': crewai_documentacao,
        'crewai_conceitos': crewai_conceitos,
        'crewai_crews': crewai_crews,
        'python_docs': python_docs,
        'python_patterns': python_patterns,
        'awesome_python': awesome_python,
        'docling_docs': docling_docs,
        'langchain_docs': langchain_docs,
        'streamlit_docs': streamlit_docs,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
    }
    try:
        Kigen().crew_kigen().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Kigen().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'instrucoes': instrucoes,
        'problema': problema,
        'crewai_documentacao': crewai_documentacao,
        'crewai_conceitos': crewai_conceitos,
        'crewai_crews': crewai_crews,
        'python_docs': python_docs,
        'python_patterns': python_patterns,
        'awesome_python': awesome_python,
        'docling_docs': docling_docs,
        'langchain_docs': langchain_docs,
        'streamlit_docs': streamlit_docs,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
    }
    try:
        Kigen().crew_kigen().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == '__main__':
    load_dotenv()
    run_kigen()
    run_codigo()
    run_depuracao()

