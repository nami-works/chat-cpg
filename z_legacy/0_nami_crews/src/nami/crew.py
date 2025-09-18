from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class nAmI():
    """Crew chamada nAmI, especializada em criar crews refinadas e robustas"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def especialista_inputs(self) -> Agent:
        return Agent(
            config=self.agents_config['especialista_inputs'],
            verbose=True
        )

    @agent
    def validador_inputs(self) -> Agent:
        return Agent(
            config=self.agents_config['validador_inputs'],
            verbose=True
        )

    @agent
    def analista_processos(self) -> Agent:
        return Agent(
            config=self.agents_config['analista_processos'],
            verbose=True
        )

    @agent
    def selecionador_llm(self) -> Agent:
        return Agent(
            config=self.agents_config['selecionador_llm'],
            verbose=True
        )

    @agent
    def definidor_agentes(self) -> Agent:
        return Agent(
            config=self.agents_config['definidor_agentes'],
            verbose=True
        )

    @agent
    def criador_tarefas(self) -> Agent:
        return Agent(
            config=self.agents_config['criador_tarefas'],
            verbose=True
        )

    @agent
    def separador_dados(self) -> Agent:
        return Agent(
            config=self.agents_config['separador_dados'],
            verbose=True
        )

    @agent
    def especialista_ferramentas(self) -> Agent:
        return Agent(
            config=self.agents_config['especialista_ferramentas'],
            verbose=True
        )

    @agent
    def integrador_ferramentas(self) -> Agent:
        return Agent(
            config=self.agents_config['integrador_ferramentas'],
            verbose=True
        )

    @agent
    def estrategista_codigo(self) -> Agent:
        return Agent(
            config=self.agents_config['estrategista_codigo'],
            verbose=True
        )

    @agent
    def orquestrador_crew(self) -> Agent:
        return Agent(
            config=self.agents_config['orquestrador_crew'],
            verbose=True
        )

    @agent
    def verificador_qualidade(self) -> Agent:
        return Agent(
            config=self.agents_config['verificador_qualidade'],
            verbose=True
        )

    @agent
    def especialista_crewai(self) -> Agent:
        return Agent(
            config=self.agents_config['especialista_crewai'],
            verbose=True
        )

    @task
    def identificar_inputs(self) -> Task:
        return Task(
            config=self.tasks_config['identificar_inputs'],
            output_file='z_sanka/chizu_kaki/inputs_necessarios.md'
        )

    @task
    def validar_inputs(self) -> Task:
        return Task(
            config=self.tasks_config['validar_inputs'],
            output_file='z_sanka/chizu_kaki/inputs_necessarios.md'
        )

    @task
    def ler_arquivos_usuario(self) -> Task:
        return Task(
            config=self.tasks_config['ler_arquivos_usuario'],
            output_file='z_sanka/chizu_kaki/inputs_usuario.md'
        )

    @task
    def coletar_briefing(self) -> Task:
        return Task(
            config=self.tasks_config['coletar_briefing'],
            output_file='z_sanka/chizu_kaki/briefing_usuario.md'
        )

    @task
    def modelar_processos(self) -> Task:
        return Task(
            config=self.tasks_config['modelar_processos'],
            output_file='z_sanka/chizu_kaki/processos_modelados.md'
        )

    @task
    def escolher_llm(self) -> Task:
        return Task(
            config=self.tasks_config['escolher_llm'],
            output_file='z_sanka/chizu_kaki/llm_recomendada.md'
        )

    @task
    def definir_agentes(self) -> Task:
        return Task(
            config=self.tasks_config['definir_agentes'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/config/agents.yaml'
        )

    @task
    def revisar_agentes(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_agentes'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/config/agents.yaml'
        )

    @task
    def refinar_agentes(self) -> Task:
        return Task(
            config=self.tasks_config['refinar_agentes'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/config/agents.yaml'
        )

    @task
    def criar_tarefas(self) -> Task:
        return Task(
            config=self.tasks_config['criar_tarefas'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/config/tasks.yaml'
        )

    @task
    def revisar_tarefas(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_tarefas'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/config/tasks.yaml'
        )

    @task
    def refinar_tarefas(self) -> Task:
        return Task(
            config=self.tasks_config['refinar_tarefas'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/config/tasks.yaml'
        )

    @task
    def estruturar_dados(self) -> Task:
        return Task(
            config=self.tasks_config['estruturar_dados'],
            output_file='z_sanka/chizu_kaki/estrutura_dados.md'
        )

    @task
    def mapear_bibliotecas(self) -> Task:
        return Task(
            config=self.tasks_config['mapear_bibliotecas'],
            output_file='z_sanka/chizu_kaki/requirements.txt'
        )

    @task
    def revisar_bibliotecas(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_bibliotecas'],
            output_file='z_sanka/chizu_kaki/requirements.txt'
        )

    @task
    def sugerir_ferramentas(self) -> Task:
        return Task(
            config=self.tasks_config['sugerir_ferramentas'],
            output_file='z_sanka/chizu_kaki/ferramentas_sugeridas.md'
        )
      
    @task
    def revisar_sugestao(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_sugestao'],
            output_file='z_sanka/chizu_kaki/ferramentas_sugeridas.md'
        )

    @task
    def criar_ferramentas(self) -> Task:
        return Task(
            config=self.tasks_config['criar_ferramentas'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/tools/custom_tool.py'
        )

    @task
    def revisar_ferramentas(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_ferramentas'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/tools/custom_tool.py'
        )

    @task
    def refinar_ferramentas(self) -> Task:
        return Task(
            config=self.tasks_config['refinar_ferramentas'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/tools/custom_tool.py'
        )

    @task
    def integrar_ferramentas(self) -> Task:
        return Task(
            config=self.tasks_config['integrar_ferramentas'],
            output_file='z_sanka/chizu_kaki/trecho_integracao_tools.py'
        )

    @task
    def modularizar_codigo(self) -> Task:
        return Task(
            config=self.tasks_config['modularizar_codigo'],
            output_file='z_sanka/chizu_kaki/estrutura_recomendada.md'
        )

    @task
    def montar_crew(self) -> Task:
        return Task(
            config=self.tasks_config['montar_crew'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/crew.py'
        )

    @task
    def revisar_crew(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_crew'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/crew.py'
        )

    @task
    def refinar_crew(self) -> Task:
        return Task(
            config=self.tasks_config['refinar_crew'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/crew.py'
        )

    @task
    def montar_main(self) -> Task:
        return Task(
            config=self.tasks_config['montar_main'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/main.py'
        )

    @task
    def integrar_inputs(self) -> Task:
        return Task(
            config=self.tasks_config['integrar_inputs'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/main.py'
        )

    @task
    def revisar_main(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_main'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/main.py'
        )

    @task
    def refinar_main(self) -> Task:
        return Task(
            config=self.tasks_config['refinar_main'],
            output_file='z_sanka/chizu_kaki/src/chizu_kaki/main.py'
        )

    @task
    def auditar_conceitos(self) -> Task:
        return Task(
            config=self.tasks_config['auditar_conceitos'],
            output_file='z_sanka/chizu_kaki/auditoria_conceitual.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            planning=True,
            planning_llm='gpt-4o-mini',
            verbose=True
        )