from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class ChizuKaki():
    """Crew chamada ChizuKaki, especializada em criar crews refinadas e robustas"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def processador_ceps(self) -> Agent:
        return Agent(
            config=self.agents_config['processador_ceps'],
            verbose=True
        )

    @agent
    def conversor_geocodificacao(self) -> Agent:
        return Agent(
            config=self.agents_config['conversor_geocodificacao'],
            verbose=True
        )

    @agent
    def calculador_distancias(self) -> Agent:
        return Agent(
            config=self.agents_config['calculador_distancias'],
            verbose=True
        )

    @agent
    def gerador_relatorio(self) -> Agent:
        return Agent(
            config=self.agents_config['gerador_relatorio'],
            verbose=True
        )

    @task
    def validar_inputs(self) -> Task:
        return Task(
            config=self.tasks_config['validar_inputs'],
            output_file='0_crews/chizu_kaki/inputs_necessarios.md'
        )

    @task
    def coletar_ceps(self) -> Task:
        return Task(
            config=self.tasks_config['coletar_ceps'],
        )

    @task
    def validar_ceps_shoppings(self) -> Task:
        return Task(
            config=self.tasks_config['validar_ceps_shoppings'],
            output_file='0_crews/chizu_kaki/briefing_usuario.md'
        )

    @task
    def converter_ceps_para_coordenadas(self) -> Task:
        return Task(
            config=self.tasks_config['converter_ceps_para_coordenadas'],
            output_file='0_crews/chizu_kaki/processos_modelados.md'
        )

    @task
    def calcular_distancias(self) -> Task:
        return Task(
            config=self.tasks_config['calcular_distancias'],
            output_file='0_crews/chizu_kaki/llm_recomendada.md'
        )

    @task
    def gerar_relatorio(self) -> Task:
        return Task(
            config=self.tasks_config['gerar_relatorio'],
            output_file='0_crews/chizu_kaki/src/chizu_kaki/ceps_distancias.csv'
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