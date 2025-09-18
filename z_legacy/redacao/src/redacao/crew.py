from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Redacao():
    """Redacao crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def curador_conteudo(self) -> Agent:
        return Agent(
            config=self.agents_config['curador_conteudo'],
            verbose=True
        )

    @agent
    def analista_estrutura(self) -> Agent:
        return Agent(
            config=self.agents_config['analista_estrutura'],
            verbose=True
        )

    @agent
    def pesquisador_casos(self) -> Agent:
        return Agent(
            config=self.agents_config['pesquisador_casos'],
            verbose=True
        )

    @agent
    def analista_dados(self) -> Agent:
        return Agent(
            config=self.agents_config['analista_dados'],
            verbose=True
        )

    @agent
    def redator_criativo(self) -> Agent:
        return Agent(
            config=self.agents_config['redator_criativo'],
            verbose=True
        )

    @agent
    def editor_coesao(self) -> Agent:
        return Agent(
            config=self.agents_config['editor_coesao'],
            verbose=True
        )

    @agent
    def revisor_gramatical(self) -> Agent:
        return Agent(
            config=self.agents_config['revisor_gramatical'],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def sintetizar_conteudo(self) -> Task:
        return Task(
            config=self.tasks_config['sintetizar_conteudo'],
            output_file='1_sintese.md'
        )

    @task
    def planejar_post(self) -> Task:
        return Task(
            config=self.tasks_config['planejar_post'],
            output_file='2_estrutura.md'
        )

    @task
    def coletar_casos(self) -> Task:
        return Task(
            config=self.tasks_config['coletar_casos'],
            output_file='3_casos_reais.md'
        )

    @task
    def coletar_dados(self) -> Task:
        return Task(
            config=self.tasks_config['coletar_dados'],
            output_file='4_dados_estatisticos.md'
        )

    @task
    def escrever_post(self) -> Task:
        return Task(
            config=self.tasks_config['escrever_post'],
            output_file='5_blog_post.md'
        )

    @task
    def refinar_narrativa(self) -> Task:
        return Task(
            config=self.tasks_config['refinar_narrativa'],
            output_file='6_narrativa_fina.md'
        )

    @task
    def revisar_final(self) -> Task:
        return Task(
            config=self.tasks_config['revisar_final'],
            output_file='7_texto_final.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Redacao crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
