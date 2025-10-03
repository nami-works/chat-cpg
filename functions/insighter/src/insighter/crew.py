from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Insighter():
    """Insighter crew for comprehensive market research and strategic analysis"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def competitive_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitive_analyst'], # type: ignore[index]
            verbose=True
        )

    @agent
    def customer_insights_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_insights_analyst'], # type: ignore[index]
            verbose=True
        )

    @agent
    def data_scientist(self) -> Agent:
        return Agent(
            config=self.agents_config['data_scientist'], # type: ignore[index]
            verbose=True
        )

    @agent
    def industry_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['industry_expert'], # type: ignore[index]
            verbose=True
        )

    @agent
    def strategic_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['strategic_analyst'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_research_task'], # type: ignore[index]
            output_file='market_research_report.md'
        )

    @task
    def competitive_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['competitive_analysis_task'], # type: ignore[index]
            output_file='competitive_analysis_report.md'
        )

    @task
    def customer_insights_task(self) -> Task:
        return Task(
            config=self.tasks_config['customer_insights_task'], # type: ignore[index]
            output_file='customer_insights_report.md'
        )

    @task
    def data_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_analysis_task'], # type: ignore[index]
            output_file='data_analysis_report.md'
        )

    @task
    def industry_expertise_task(self) -> Task:
        return Task(
            config=self.tasks_config['industry_expertise_task'], # type: ignore[index]
            output_file='industry_expertise_report.md'
        )

    @task
    def strategic_synthesis_task(self) -> Task:
        return Task(
            config=self.tasks_config['strategic_synthesis_task'], # type: ignore[index]
            context=[
                self.market_research_task(),
                self.competitive_analysis_task(),
                self.customer_insights_task(),
                self.data_analysis_task(),
                self.industry_expertise_task()
            ],
            output_file='strategic_analysis_report.md'
        )

    @task
    def final_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['final_report_task'], # type: ignore[index]
            context=[
                self.market_research_task(),
                self.competitive_analysis_task(),
                self.customer_insights_task(),
                self.data_analysis_task(),
                self.industry_expertise_task(),
                self.strategic_synthesis_task()
            ],
            output_file='comprehensive_market_analysis_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Insighter crew for comprehensive market research and analysis"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
