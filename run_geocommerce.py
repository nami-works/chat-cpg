#!/usr/bin/env python3
"""
GeoCommerce - Análise Geográfica
Main script to run the GeoCommerce application
"""

import sys
import os
from pathlib import Path

def main():
    """Main function to run the GeoCommerce application"""
    
    # Add the project root to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Check for environment variables
    required_vars = ['SHOPIFY_SHOP_NAME', 'SHOPIFY_ACCESS_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Variáveis de ambiente necessárias não encontradas!")
        print("Por favor, crie um arquivo .env com suas credenciais:")
        print("SHOPIFY_SHOP_NAME=seu-nome-da-loja")
        print("SHOPIFY_ACCESS_TOKEN=seu-token-de-acesso")
        print("SHOPIFY_API_VERSION=2024-01")
        return 1
    
    try:
        print("🚀 Iniciando GeoCommerce - Análise Geográfica...")
        
        # Import and run the application
        sys.path.insert(0, 
            str(current_dir / "geocommerce" / "geocommerce_shopify.py"),
        )
        
        from geocommerce.geocommerce_shopify import GeoCommerceShopifyApp
        
        app = GeoCommerceShopifyApp()
        app.run()
        
        return 0
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("Certifique-se de que todas as dependências estão instaladas:")
        print("pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())