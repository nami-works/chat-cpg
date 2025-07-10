# Import the get_function_context function from the main chat_cpg module
import sys
from pathlib import Path

# Add the parent directory to the path to access chat_cpg module
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from chat_cpg import get_function_context

# GeoCommerce specific context
GEOCOMMERCE_CONTEXT = {
    'title': '🗺️ ChatCPG | GeoCommerce',
    'subtitle': 'Bem-vindo ao GeoCommerce da GE Beauty!',
    'description': """
    Esse é o sistema de análise geográfica e insights de e-commerce da GE Beauty!
    Aqui você pode:\n
    • Analisar dados de vendas por região\n
    • Visualizar performance geográfica dos produtos\n
    • Identificar oportunidades de mercado\n
    • Integrar dados do Shopify com análises geográficas\n
    \n\n
    Conecte-se ao Shopify para começar! 🛍️
    """,
    'icon': '🗺️'
}