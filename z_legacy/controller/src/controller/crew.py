import sys
import os
sys.path.append(os.path.dirname(__file__))

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.leitor_pdf import ReadMultiplePDFsTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Controller():
    """Controller crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    leitor_pdf = ReadMultiplePDFsTool(pasta="controller/documentos_fiscais/")

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def contadora_tributaria_senior(self) -> Agent:
        return Agent(
            config=self.agents_config['contadora_tributaria_senior'],
            tools=[self.leitor_pdf],
            verbose=True
        )

    @agent
    def especialista_obg_acessorias_compliance(self) -> Agent:
        return Agent(
            config=self.agents_config['especialista_obg_acessorias_compliance'],
            tools=[self.leitor_pdf],
            verbose=True
        )

    @agent
    def analista_integracao_erp_contabil(self) -> Agent:
        return Agent(
            config=self.agents_config['analista_integracao_erp_contabil'],
            tools=[self.leitor_pdf],
            verbose=True
        )

    @agent
    def auditor_interno_espec_contabilidade_digital(self) -> Agent:
        return Agent(
            config=self.agents_config['auditor_interno_espec_contabilidade_digital'],
            tools=[self.leitor_pdf],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def mapear_regime_tributario(self) -> Task:
        return Task(
            config=self.tasks_config['mapear_regime_tributario'],
        )

    @task
    def apurar_e_registrar_tributos(self) -> Task:
        return Task(
            config=self.tasks_config['apurar_e_registrar_tributos'],
            output_file='report.md'
        )

    @task
    def gerenciar_e_automar_obg_acessorias(self) -> Task:
        return Task(
            config=self.tasks_config['gerenciar_e_automar_obg_acessorias'],
        )

    @task
    def integrar_erp_e_contabil(self) -> Task:
        return Task(
            config=self.tasks_config['integrar_erp_e_contabil'],
            output_file='report.md'
        )

    @task
    def validar_demonstracoes_contabeis(self) -> Task:
        return Task(
            config=self.tasks_config['validar_demonstracoes_contabeis'],
        )

    @task
    def consolidar_indicadores(self) -> Task:
        return Task(
            config=self.tasks_config['consolidar_indicadores'],
            output_file='report.md'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Controller crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
