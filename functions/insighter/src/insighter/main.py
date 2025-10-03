#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from pathlib import Path

from insighter.crew import Insighter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(inputs=None):
    """
    Run the insighter crew for comprehensive market research and analysis.
    
    Args:
        inputs (dict): Dictionary containing:
            - topic: The topic/market to analyze
            - current_year: Current year for analysis
            - output_dir: Directory to save reports (optional)
            - additional_context: Any additional context for analysis (optional)
    """
    if inputs is None:
        inputs = {
            'topic': 'AI and Machine Learning Market',
            'current_year': str(datetime.now().year),
            'output_dir': 'market_analysis_reports',
            'additional_context': 'Focus on enterprise adoption and market trends'
        }
    
    # Ensure output directory exists
    output_dir = inputs.get('output_dir', 'market_analysis_reports')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Run the crew with the provided inputs
        result = Insighter().crew().kickoff(inputs=inputs)
        
        # Move generated reports to output directory
        report_files = [
            'market_research_report.md',
            'competitive_analysis_report.md', 
            'customer_insights_report.md',
            'data_analysis_report.md',
            'industry_expertise_report.md',
            'strategic_analysis_report.md',
            'comprehensive_market_analysis_report.md'
        ]
        
        for file_name in report_files:
            if os.path.exists(file_name):
                os.rename(file_name, os.path.join(output_dir, file_name))
        
        print(f"Market analysis completed successfully. Reports saved in: {output_dir}")
        return result
        
    except Exception as e:
        raise Exception(f"An error occurred while running the insighter crew: {e}")

def analyze_market(topic, additional_context=None, output_dir=None):
    """
    Convenience function to analyze a specific market topic.
    
    Args:
        topic (str): The market topic to analyze
        additional_context (str): Additional context or focus areas
        output_dir (str): Directory to save reports
    """
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year),
        'output_dir': output_dir or f'market_analysis_{topic.lower().replace(" ", "_")}',
        'additional_context': additional_context or ''
    }
    
    return run(inputs)

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "E-commerce Market Analysis",
        'current_year': str(datetime.now().year),
        'output_dir': 'training_reports',
        'additional_context': 'Focus on B2C e-commerce trends and customer behavior'
    }
    
    try:
        Insighter().crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Insighter().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "SaaS Market Analysis",
        "current_year": str(datetime.now().year),
        'output_dir': 'test_reports',
        'additional_context': 'Focus on B2B SaaS trends and competitive landscape'
    }
    
    try:
        Insighter().crew().test(
            n_iterations=int(sys.argv[1]), 
            eval_llm=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def generate_quick_analysis(topic):
    """
    Generate a quick market analysis for a given topic.
    This runs a simplified version focusing on key insights.
    """
    inputs = {
        'topic': topic,
        'current_year': str(datetime.now().year),
        'output_dir': f'quick_analysis_{topic.lower().replace(" ", "_")}',
        'additional_context': 'Quick analysis focusing on key market insights and opportunities'
    }
    
    return run(inputs)

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        elif command == "analyze":
            topic = sys.argv[2] if len(sys.argv) > 2 else "Technology Market"
            generate_quick_analysis(topic)
        else:
            print("Usage: python main.py [train|replay|test|analyze] [topic]")
    else:
        # Default run
        run()
