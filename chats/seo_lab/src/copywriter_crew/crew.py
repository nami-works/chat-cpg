import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pathlib import Path

# Import context chunking system
from chats.seo_lab.context_chunking import ContextChunker, get_task_stage

base_dir = os.path.dirname(os.path.abspath(__file__))

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class SEOLab_CPG():
    """SEOLab_CPG crew with context chunking for token efficiency"""
    def __init__(self, brand_folder: Path):
        self.base_dir = Path(__file__).resolve().parent
        self.brand_folder = brand_folder
        self.agents_config = 'config/agents.yaml'
        self.tasks_config = 'config/tasks.yaml'
        self.context_chunker = None  # Will be initialized with inputs

    def initialize_context_chunker(self, inputs: dict):
        """Initialize the context chunker with full inputs"""
        self.context_chunker = ContextChunker(inputs)

    def get_optimized_context(self, agent_role: str, task_name: str) -> dict:
        """Get optimized context for specific agent and task"""
        if not self.context_chunker:
            return {}
        
        task_stage = get_task_stage(agent_role, task_name)
        return self.context_chunker.get_minimal_context(agent_role, task_stage)

    @agent
    def brand_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['brand_strategist'],
            verbose=True
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            verbose=True
        )

    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['content_strategist'],
            verbose=True,
        )

    @agent
    def seo_copywriter(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_copywriter'],
            verbose=True
        )

    @agent
    def narrative_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['narrative_editor'],
            verbose=True
        )

    @agent
    def content_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_reviewer'],
            verbose=True
        )

    @agent
    def visual_consultant(self) -> Agent:
        return Agent(
            config=self.agents_config['visual_consultant'],
            verbose=True
        )


    @task
    def define_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['define_strategy'],
        )

    @task
    def identify_products(self) -> Task:
        return Task(
            config=self.tasks_config['identify_products'],
        )

    @task
    def map_opportunities(self) -> Task:
        return Task(
            config=self.tasks_config['map_opportunities'],
        )

    @task
    def plan_content(self) -> Task:
        return Task(
            config=self.tasks_config['plan_content'],
            context=[
                self.define_strategy(),
                self.identify_products()]
        )

    @task
    def map_semantic_fields(self) -> Task:
        return Task(
            config=self.tasks_config['plan_content'],
            context=[
                self.define_strategy(),
                self.identify_products(),
                self.plan_content()]
        )

    @task
    def write_content(self) -> Task:
        return Task(
            config=self.tasks_config['write_content'],
            context=[
                self.define_strategy(),
                self.identify_products(),
                self.map_opportunities(),
                self.plan_content()],
            output_file=str(self.brand_folder / 'posts' / 'content.html')
        )

    @task
    def refine_narrative(self) -> Task:
        return Task(
            config=self.tasks_config['refine_narrative'],
            output_file=str(self.brand_folder / 'posts' / 'content.html')
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
    def generate_seo_metafields(self) -> Task:
        return Task(
            config=self.tasks_config['generate_seo_metafields'],
            output_file=str(self.brand_folder / 'posts' / 'metafields.md')
        )




    @crew
    def crew(self) -> Crew:
        """Creates the BlogLab_CPG crew with context chunking"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
