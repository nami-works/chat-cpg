from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

from tools.custom_tool import GeocodeTool

class GeocodeResolver:
    def __init__(self):
        self.geocoder = Geocoder()

    def resolve(self, cep):
        return self.geocoder.resolve(cep)


@CrewBase
class Roteirizador():
    """Roteirizador crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def cep_file_reader(self) -> Agent:
        return Agent(
            config=self.agents_config['cep_file_reader'],
            verbose=True
        )

    @agent
    def geocode_resolver(self) -> Agent:
        return Agent(
            config=self.agents_config['geocode_resolver'],
            tools=[GeocodeTool()],
            verbose=True
        )


    @agent
    def distance_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['distance_analyzer'],
            verbose=True
        )

    @agent
    def proximity_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['proximity_evaluator'],
            verbose=True
        )

    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
            verbose=True
        )

    @task
    def ler_ceps_lista_b(self) -> Task:
        return Task(
            config=self.tasks_config['ler_ceps_lista_b'],
        )

    @task
    def resolver_coordenadas_shoppings(self) -> Task:
        return Task(
            config=self.tasks_config['resolver_coordenadas_shoppings'],
        )

    @task
    def resolver_coordenadas_cep_b(self) -> Task:
        return Task(
            config=self.tasks_config['resolver_coordenadas_cep_b'],
        )

    @task
    def calcular_distancia_cep_e_shoppings(self) -> Task:
        return Task(
            config=self.tasks_config['calcular_distancia_cep_e_shoppings'],
        )

    @task
    def avaliar_proximidade_com_shoppings(self) -> Task:
        return Task(
            config=self.tasks_config['avaliar_proximidade_com_shoppings'],
        )

    @task
    def gerar_relatorio_resultados(self) -> Task:
        return Task(
            config=self.tasks_config['gerar_relatorio_resultados'],
            output_file='ceps_distancias.csv'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Roteirizador crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
