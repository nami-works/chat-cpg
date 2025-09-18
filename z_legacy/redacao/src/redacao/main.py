#!/usr/bin/env python
import sys
import warnings

from datetime import date

from crew import Redacao

from dotenv import load_dotenv

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

tema = 'O efeito glass skin na dermatologia'
estilo = 'Tom e estilo de linguagem explicativa e ao mesmo tempo próxima, de forma jovial e descontraída, demonstrando domínio técnico sobre o tema e mantendo autoridade médica. Consegue traduzir informações mais complexas de forma simples para facilitar o entendimento. Prefere um estilo de texto conversacional, usando elementos como "Mas quais são os componentes típicos desta rotina?" ao invés de "Aqui está uma lista dos componentes típicos dessa rotina:"'

def run():
    """
    Run the crew.
    """
    inputs = {
        'tema': tema,
        'estilo': estilo,
        'current_year': str(datetime.now().year)
    }
    
    try:
        Redacao().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'tema': tema,
        'estilo': estilo,
    }
    try:
        Redacao().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Redacao().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'tema': tema,
        'estilo': estilo,
        "current_year": str(datetime.now().year)
    }
    try:
        Redacao().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == '__main__':
    load_dotenv()
    run()