import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.tools import BaseTool

# from tools.validar_imports_tool import diagnosticar_imports


base_dir = os.path.dirname(os.path.abspath(__file__))

@CrewBase
class Kigen():
    """Kigen crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def avaliador_problemas(self) -> Agent:
        return Agent(
            config=self.agents_config['avaliador_problemas'],
            verbose=True
        )

    @agent
    def pesquisador_solucoes(self) -> Agent:
        return Agent(
            config=self.agents_config['pesquisador_solucoes'],
            verbose=True
        )

    @agent
    def decisor_estrategico(self) -> Agent:
        return Agent(
            config=self.agents_config['decisor_estrategico'],
            verbose=True
        )

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
    def engenheiro_solucoes(self) -> Agent:
        return Agent(
            config=self.agents_config['engenheiro_solucoes'],
            verbose=True
        )

    @agent
    def mapeador_dependencias(self) -> Agent:
        return Agent(
            config=self.agents_config['mapeador_dependencias'],
            verbose=True
        )

    @agent
    def gerador_modelos(self) -> Agent:
        return Agent(
            config=self.agents_config['gerador_modelos'],
            verbose=True
        )

    @task
    def analisar_problema(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_problema'],
            output_file=os.path.join(base_dir, 'outputs', 'recomendacao.md')
        )

    @task
    def buscar_referencias(self) -> Task:
        return Task(
            config=self.tasks_config['buscar_referencias'],
            output_file=os.path.join(base_dir, 'outputs', 'recomendacao.md')
        )

    @task
    def avaliar_abordagem(self) -> Task:
        return Task(
            config=self.tasks_config['avaliar_abordagem'],
            output_file=os.path.join(base_dir, 'outputs', 'recomendacao.md')
        )

    @task
    def identificar_inputs(self) -> Task:
        return Task(
            config=self.tasks_config['identificar_inputs'],
            output_file=os.path.join(base_dir, 'outputs', 'inputs.md')
        )

    @task
    def validar_inputs(self) -> Task:
        return Task(
            config=self.tasks_config['validar_inputs'],
            output_file=os.path.join(base_dir, 'outputs', 'inputs.md')
        )

    @task
    def gerar_modelos(self) -> Task:
        return Task(
            config=self.tasks_config['gerar_modelos'],
            output_file=os.path.join(base_dir, 'outputs', 'modelo_input.csv')
        )

    @task
    def mapear_funcoes(self) -> Task:
        return Task(
            config=self.tasks_config['mapear_funcoes'],
        )

    @task
    def buscar_padroes_funcoes(self) -> Task:
        return Task(
            config=self.tasks_config['buscar_padroes_funcoes'],
        )

    @task
    def revisar_padroes_funcoes(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_padroes_funcoes'],
        )

    @task
    def escrever_codigo(self) -> Task:
        return Task(
            config=self.tasks_config['escrever_codigo'],
            output_file=os.path.join(base_dir, 'outputs', 'codigo_v1.py')
        )

    @task
    def validar_imports(self) -> Task:
        return Task(
            config=self.tasks_config['validar_imports'],
            output_file=os.path.join(base_dir, 'outputs', 'imports_invalidos.md')
        )

    @task
    def corrigir_imports(self) -> Task:
        return Task(
            config=self.tasks_config['corrigir_imports'],
            context=[
                self.escrever_codigo()],
            output_file=os.path.join(base_dir, 'outputs', 'codigo_v2.py')        
        )

    @task
    def identificar_dependencias(self) -> Task:
        return Task(
            config=self.tasks_config['identificar_dependencias'],
            output_file=os.path.join(base_dir, 'outputs', 'requirements.txt')
        )

    @task
    def mapear_dependencias_extras(self) -> Task:
        return Task(
            config=self.tasks_config['mapear_dependencias_extras'],
            output_file=os.path.join(base_dir, 'outputs', 'requirements.txt')
        )

    @task
    def reescrever_codigo(self) -> Task:
        return Task(
            config=self.tasks_config['reescrever_codigo'],
            output_file=os.path.join(base_dir, 'outputs', 'codigo_v3.py')
        )

    @task
    def auditar_melhoria_iterativa(self) -> Task:
        return Task(
            config=self.tasks_config['auditar_melhoria_iterativa'],
            output_file=os.path.join(base_dir, 'docs', 'relatorio_auditoria.md')
        )

    @task
    def validar_ambiente_execucao(self) -> Task:
        return Task(
            config=self.tasks_config['validar_ambiente_execucao'],
            output_file=os.path.join(base_dir, 'docs', 'status_ambiente.md')
        )

    @task
    def corrigir_requirements(self) -> Task:
        return Task(
            config=self.tasks_config['corrigir_requirements'],
            output_file=os.path.join(base_dir, 'docs', 'novo_requirements.txt')
        )

    @task
    def gerar_env_minimo(self) -> Task:
        return Task(
            config=self.tasks_config['gerar_env_minimo'],
            output_file=os.path.join(base_dir, 'docs', 'env.txt')
        )

    # @tool
    # def validar_imports_tool(self) -> BaseTool:
    #     from tools.custom_tool import ValidarImportsTool
    #     return ValidarImportsTool()

    @crew
    def crew_kigen(self) -> Crew:
        """Creates the Kigen crew"""

        return Crew(
            agents=[
                self.avaliador_problemas(),
                self.pesquisador_solucoes(),
                self.decisor_estrategico(),
                self.especialista_inputs(),
                self.validador_inputs(),
                self.gerador_modelos()
            ],
            tasks=[
                self.analisar_problema(),
                self.buscar_referencias(),
                self.avaliar_abordagem(),
                self.identificar_inputs(),
                self.validar_inputs(),
                self.gerar_modelos()
            ],
            process=Process.sequential,
            verbose=True,
        )
    
    @crew
    def crew_codigo(self) -> Crew:
        """Creates the Kigen crew"""

        return Crew(
            agents=[
                self.avaliador_problemas(),
                self.pesquisador_solucoes(),
                self.engenheiro_solucoes(),
                self.mapeador_dependencias(),
            ],
            tasks=[
                self.mapear_funcoes(),
                self.buscar_padroes_funcoes(),
                self.revisar_padroes_funcoes(),
                self.escrever_codigo(),
                self.validar_imports(),
                self.corrigir_imports(),
                self.identificar_dependencias(),
                self.mapear_dependencias_extras(),
            ],
            process=Process.sequential,
            verbose=True,
        )

    @crew
    def crew_depuracao(self) -> Crew:
        """Creates the Kigen crew"""

        return Crew(
            agents=[
                self.engenheiro_solucoes(),
                self.pesquisador_solucoes(),
                self.mapeador_dependencias(),
                # self.avaliador_problemas(),
                # self.validador_inputs(),
                # self.especialista_inputs()
            ],
            tasks=[
                self.reescrever_codigo(),
                self.validar_imports(),
                self.corrigir_imports(),
                self.identificar_dependencias(),
                self.mapear_dependencias_extras(),
                # self.auditar_melhoria_iterativa(),
                # self.validar_ambiente_execucao(),
                # self.corrigir_requirements(),
                # self.gerar_env_minimo()
            ],
            process=Process.sequential,
            verbose=True,
        )

    @crew
    def crew_crew(self) -> Crew:
        """Creates the Kigen crew"""

        return Crew(
            agents=[
                self.analista_processos(),
                self.selecionador_llm(),
                self.definidor_agentes(),
                self.criador_tarefas(),
                self.separador_dados(),
                self.especialista_ferramentas(),
                self.integrador_ferramentas(),
                self.estrategista_codigo(),
                self.orquestrador_crew(),
                self.verificador_qualidade(),
                self.especialista_crewai(),
            ],
            tasks=[
                self.identificar_inputs(),
                self.validar_inputs(),
                self.ler_arquivos_usuario(),
                self.coletar_briefing(),
                self.modelar_processos(),
                self.escolher_llm(),
                self.definir_agentes(),
                self.revisar_agentes(),
                self.criar_tarefas(),
                self.revisar_tarefas(),
                self.estruturar_dados(),
                self.mapear_bibliotecas(),
                self.revisar_bibliotecas(),
                self.sugerir_ferramentas(),
                self.revisar_sugestao(),
                self.criar_ferramentas(),
                self.revisar_ferramentas(),
                self.integrar_ferramentas(),
                self.modularizar_codigo(),
                self.montar_crew(),
                self.revisar_crew(),
                self.montar_main(),
                self.integrar_inputs(),
                self.revisar_main(),
                self.auditar_conceitos(),
            ],
            process=Process.sequential,
            verbose=True,
        )