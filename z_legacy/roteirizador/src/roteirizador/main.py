#!/usr/bin/env python
import sys
import warnings

from crew import Roteirizador

from dotenv import load_dotenv

from pathlib import Path

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

ceps_shoppings = {
    "Iguatemi Fortaleza": "60811-341",
    "Shopping Recife": "51020-900",
    "Shopping RioMar Recife": "51110-160",
    "Shops Jardins": "01414-002",
    "Shopping RioSul": "22290-070"
}

base_dir = Path(__file__).resolve().parent
file_ceps = base_dir / 'customers_export.csv'

with open(file_ceps, 'r', encoding='utf-8') as file:
    base_ceps = file.read()

def run():
    """
    Run the crew.
    """
    inputs = {
        'ceps_shoppings': ceps_shoppings,
        'base_ceps': base_ceps
    }
    
    try:
        Roteirizador().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'ceps_shoppings': ceps_shoppings,
        'base_ceps': base_ceps
    }
    try:
        Roteirizador().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Roteirizador().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'ceps_shoppings': ceps_shoppings,
        'base_ceps': base_ceps
    }
    try:
        Roteirizador().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == '__main__':
    load_dotenv()
    run()