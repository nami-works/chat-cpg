#!/usr/bin/env python3
"""
GeoCommerce - Shopify API Integration
Run script for the Streamlit application
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main function to run the GeoCommerce Shopify application"""
    
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Check if .env file exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your Shopify credentials:")
        print()
        print("SHOPIFY_SHOP_NAME=your-shop-name")
        print("SHOPIFY_ACCESS_TOKEN=your-access-token") 
        print("SHOPIFY_API_VERSION=2024-01")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    # Check if required packages are installed
    try:
        import streamlit
        import pandas
        import plotly
        import folium
        import geopy
        import sklearn
        import aiohttp
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements:")
        print("pip install -r geocommerce/requirements.txt")
        return
    
    # Run the Streamlit application
    print("🚀 Starting GeoCommerce - Shopify API Integration...")
    print("📍 Open your browser to: http://localhost:8501")
    print()
    
    try:
        # Run streamlit with the geocommerce app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(current_dir / "geocommerce" / "geocommerce_shopify.py"),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 GeoCommerce application stopped.")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main()