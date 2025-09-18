#!/usr/bin/env python
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv
from crew import nAmI

warnings.filterwarnings("ignore", category=SyntaxWarning)

base_dir = Path(__file__).resolve().parent
briefing_crew = base_dir / 'briefing_crew.md'

with open(briefing_crew, 'r', encoding='utf-8') as file:
    crew = file.read()

# Variáveis de configuração e fontes externas
documentacao = 'https://docs.crewai.com/docs'
conceitos = 'https://docs.crewai.com/concepts/'
como_fazer = 'https://docs.crewai.com/how-to'
guia_conceitos = 'https://docs.crewai.com/guides/concepts'
agentes = 'https://docs.crewai.com/concepts/agents'
guia_agentes = 'https://docs.crewai.com/guides/agents'
customizacao_agentes = 'https://docs.crewai.com/how-to/customizing-agents'
agentes_multimodais = 'https://docs.crewai.com/how-to/multimodal-agents'
agentes_programadores = 'https://docs.crewai.com/how-to/coding-agents'
tasks = 'https://docs.crewai.com/concepts/tasks'
tarefas_condicionais = 'https://docs.crewai.com/how-to/conditional-tasks'
crews = 'https://docs.crewai.com/concepts/crews'
guia_crews = 'https://docs.crewai.com/guides/crews'
input_humano = 'https://docs.crewai.com/how-to/human-input-on-execution'
fluxos = 'https://docs.crewai.com/concepts/flows'
guia_fluxos = 'https://docs.crewai.com/guides/flows'
conhecimento = 'https://docs.crewai.com/concepts/knowledge'
llms = 'https://docs.crewai.com/concepts/llms'
guia_llms = 'https://docs.crewai.com/how-to/llm-connections'
processos = 'https://docs.crewai.com/concepts/processes'
processos_sequenciais = 'https://docs.crewai.com/how-to/sequential-process'
processos_hierarquicos = 'https://docs.crewai.com/how-to/hierarchical-process'
agente_gestor = 'https://docs.crewai.com/how-to/custom-manager-agent'
colaboracao = 'https://docs.crewai.com/concepts/collaboration'
comunidade = 'https://community.crewai.com/'
treinamento = 'https://docs.crewai.com/concepts/training'
memoria = 'https://docs.crewai.com/concepts/memory'
planejamento = 'https://docs.crewai.com/concepts/planning'
testes = 'https://docs.crewai.com/concepts/testing'
ferramentas = 'https://docs.crewai.com/concepts/tools'
guia_ferramentas = 'https://docs.crewai.com/how-to/create-custom-tools'
tool_output = 'https://docs.crewai.com/how-to/force-tool-output-as-result'
eventos = 'https://docs.crewai.com/concepts/event-listener'
bibliotecas = 'https://pypi.org/'
github = 'https://github.com/'
stack_overflow = 'https://stackoverflow.com/'

def run():
    """
    Run the crew.
    """
    inputs = {
        'crew': crew,
        'documentacao': documentacao,
        'conceitos': conceitos,
        'como_fazer': como_fazer,
        'guia_conceitos': guia_conceitos,
        'agentes': agentes,
        'guia_agentes': guia_agentes,
        'customizacao_agentes': customizacao_agentes,
        'agentes_multimodais': agentes_multimodais,
        'agentes_programadores': agentes_programadores,
        'tasks': tasks,
        'tarefas_condicionais': tarefas_condicionais,
        'crews': crews,
        'guia_crews': guia_crews,
        'input_humano': input_humano,
        'fluxos': fluxos,
        'guia_fluxos': guia_fluxos,
        'conhecimento': conhecimento,
        'llms': llms,
        'guia_llms': guia_llms,
        'processos': processos,
        'processos_sequenciais': processos_sequenciais,
        'processos_hierarquicos': processos_hierarquicos,
        'agente_gestor': agente_gestor,
        'colaboracao': colaboracao,
        'comunidade': comunidade,
        'treinamento': treinamento,
        'memoria': memoria,
        'planejamento': planejamento,
        'testes': testes,
        'ferramentas': ferramentas,
        'guia_ferramentas': guia_ferramentas,
        'tool_output': tool_output,
        'eventos': eventos,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
    }

    try:
        nAmI().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'crew': crew,
        'documentacao': documentacao,
        'conceitos': conceitos,
        'como_fazer': como_fazer,
        'guia_conceitos': guia_conceitos,
        'agentes': agentes,
        'guia_agentes': guia_agentes,
        'customizacao_agentes': customizacao_agentes,
        'agentes_multimodais': agentes_multimodais,
        'agentes_programadores': agentes_programadores,
        'tasks': tasks,
        'tarefas_condicionais': tarefas_condicionais,
        'crews': crews,
        'guia_crews': guia_crews,
        'input_humano': input_humano,
        'fluxos': fluxos,
        'guia_fluxos': guia_fluxos,
        'conhecimento': conhecimento,
        'llms': llms,
        'guia_llms': guia_llms,
        'processos': processos,
        'processos_sequenciais': processos_sequenciais,
        'processos_hierarquicos': processos_hierarquicos,
        'agente_gestor': agente_gestor,
        'colaboracao': colaboracao,
        'comunidade': comunidade,
        'treinamento': treinamento,
        'memoria': memoria,
        'planejamento': planejamento,
        'testes': testes,
        'ferramentas': ferramentas,
        'guia_ferramentas': guia_ferramentas,
        'tool_output': tool_output,
        'eventos': eventos,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
    }
    try:
        nAmI().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        nAmI().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'crew': crew,
        'documentacao': documentacao,
        'conceitos': conceitos,
        'como_fazer': como_fazer,
        'guia_conceitos': guia_conceitos,
        'agentes': agentes,
        'guia_agentes': guia_agentes,
        'customizacao_agentes': customizacao_agentes,
        'agentes_multimodais': agentes_multimodais,
        'agentes_programadores': agentes_programadores,
        'tasks': tasks,
        'tarefas_condicionais': tarefas_condicionais,
        'crews': crews,
        'guia_crews': guia_crews,
        'input_humano': input_humano,
        'fluxos': fluxos,
        'guia_fluxos': guia_fluxos,
        'conhecimento': conhecimento,
        'llms': llms,
        'guia_llms': guia_llms,
        'processos': processos,
        'processos_sequenciais': processos_sequenciais,
        'processos_hierarquicos': processos_hierarquicos,
        'agente_gestor': agente_gestor,
        'colaboracao': colaboracao,
        'comunidade': comunidade,
        'treinamento': treinamento,
        'memoria': memoria,
        'planejamento': planejamento,
        'testes': testes,
        'ferramentas': ferramentas,
        'guia_ferramentas': guia_ferramentas,
        'tool_output': tool_output,
        'eventos': eventos,
        'bibliotecas': bibliotecas,
        'github': github,
        'stack_overflow': stack_overflow,
    }
    try:
        nAmI().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == '__main__':
    load_dotenv()
    run()
