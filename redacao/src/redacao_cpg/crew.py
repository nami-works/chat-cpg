import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pathlib import Path

base_dir = os.path.dirname(os.path.abspath(__file__))

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Redacao_CPG():
    """Redacao_CPG crew"""
    def __init__(self, pasta_marca: Path):
        self.base_dir = Path(__file__).resolve().parent
        self.pasta_marca = pasta_marca
        self.agents_config = 'config/agents.yaml'
        self.tasks_config = 'config/tasks.yaml'

    @agent
    def estrategista_marca(self) -> Agent:
        return Agent(
            config=self.agents_config['estrategista_marca'],
            verbose=True
        )

    @agent
    def especialista_seo(self) -> Agent:
        return Agent(
            config=self.agents_config['especialista_seo'],
            verbose=True
        )

    @agent
    def estrategista_conteudo(self) -> Agent:
        return Agent(
            config=self.agents_config['estrategista_conteudo'],
            verbose=True,
        )

    @agent
    def redator_seo(self) -> Agent:
        return Agent(
            config=self.agents_config['redator_seo'],
            verbose=True
        )

    @agent
    def editor_coesao(self) -> Agent:
        return Agent(
            config=self.agents_config['editor_coesao'],
            verbose=True
        )

    @agent
    def revisor_geral(self) -> Agent:
        return Agent(
            config=self.agents_config['revisor_geral'],
            verbose=True
        )

    @agent
    def consultor_visual(self) -> Agent:
        return Agent(
            config=self.agents_config['consultor_visual'],
            verbose=True
        )


    @task
    def definir_estrategia(self) -> Task:
        return Task(
            config=self.tasks_config['definir_estrategia'],
        )

    @task
    def identificar_produtos(self) -> Task:
        return Task(
            config=self.tasks_config['identificar_produtos'],
        )

    @task
    def mapear_oportunidades(self) -> Task:
        return Task(
            config=self.tasks_config['mapear_oportunidades'],
        )

    @task
    def planejar_conteudos(self) -> Task:
        return Task(
            config=self.tasks_config['planejar_conteudos'],
            context=[
                self.definir_estrategia(),
                self.identificar_produtos()]
        )

    @task
    def mapear_campos_semanticos(self) -> Task:
        return Task(
            config=self.tasks_config['planejar_conteudos'],
            context=[
                self.definir_estrategia(),
                self.identificar_produtos(),
                self.planejar_conteudos()]
        )

    @task
    def escrever_conteudo(self) -> Task:
        return Task(
            config=self.tasks_config['escrever_conteudo'],
            context=[
                self.definir_estrategia(),
                self.identificar_produtos(),
                self.mapear_oportunidades(),
                self.planejar_conteudos()],
            output_file=str(self.pasta_marca / 'posts' / 'content.html')
        )

    @task
    def refinar_narrativa(self) -> Task:
        return Task(
            config=self.tasks_config['refinar_narrativa'],
            output_file=str(self.pasta_marca / 'posts' / 'content.html')
        )

    # @task
    # def revisar_tudo(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['revisar_tudo'],
    #         output_file='posts/2025_04_21_buildup/revisar_tudo.md'
    #     )

    # @task
    # def sugerir_elementos(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['sugerir_elementos'],
    #         output_file='posts/2025_04_21_buildup/sugestoes_elementos.md'
    #     )

    @task
    def gerar_metacampos_seo(self) -> Task:
        return Task(
            config=self.tasks_config['gerar_metacampos_seo'],
            output_file=str(self.pasta_marca / 'posts' / 'metafields.md')
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Redacao_CPG crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
