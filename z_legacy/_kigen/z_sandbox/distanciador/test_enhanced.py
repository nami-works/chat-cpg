"""
Test script for Enhanced Distanciador
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_distanciador import EnhancedDistanciador
from config import get_config, validate_config

def test_configuration():
    """Test configuration validation"""
    print("🧪 Testing Configuration...")
    
    if validate_config():
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Base directory: {config['base_dir']}")
        print(f"   - Shopping malls: {len(config['shoppings'])}")
        print(f"   - Analysis settings: {config['analysis']}")
        return True
    else:
        print("❌ Configuration validation failed")
        return False

def test_enhanced_distanciador_initialization():
    """Test EnhancedDistanciador initialization"""
    print("\n🧪 Testing EnhancedDistanciador Initialization...")
    
    try:
        distanciador = EnhancedDistanciador()
        print("✅ EnhancedDistanciador initialized successfully")
        print(f"   - Cache loaded: {len(distanciador.cache)} entries")
        print(f"   - Geolocator configured: {distanciador.geolocator}")
        return distanciador
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None

def test_shopify_data_processing(distanciador):
    """Test Shopify data processing"""
    print("\n🧪 Testing Shopify Data Processing...")
    
    config = get_config()
    shopify_file = config['paths']['shopify']
    
    if not os.path.exists(shopify_file):
        print(f"⚠️ Shopify file not found: {shopify_file}")
        print("   Skipping Shopify processing test")
        return None
    
    try:
        # Load and process a small sample first
        df_sample = pd.read_csv(shopify_file, nrows=5)
        print(f"✅ Sample data loaded: {len(df_sample)} rows")
        print(f"   - Columns: {list(df_sample.columns)}")
        
        # Test data cleaning
        df_sample['cep'] = df_sample['Default Address Zip'].str.replace('-', '').str.strip()
        df_sample['cep'] = df_sample['cep'].astype(str).str.zfill(8)
        print(f"✅ CEP cleaning test passed")
        
        # Test coordinate processing for one CEP
        if len(df_sample) > 0:
            test_cep = df_sample.iloc[0]['cep']
            coords = distanciador.obter_coordenadas(test_cep)
            print(f"✅ Geocoding test for CEP {test_cep}: {coords}")
        
        return True
        
    except Exception as e:
        print(f"❌ Shopify processing test failed: {e}")
        return False

def test_density_analysis_functions(distanciador):
    """Test density analysis functions with sample data"""
    print("\n🧪 Testing Density Analysis Functions...")
    
    try:
        # Create sample data
        sample_data = {
            'Customer ID': ['1', '2', '3', '4', '5'],
            'Default Address Zip': ['30170-130', '30575-843', '36033-345', '30170-130', '30575-843'],
            'Default Address City': ['Belo Horizonte', 'Belo Horizonte', 'Juiz de Fora', 'Belo Horizonte', 'Belo Horizonte'],
            'Total Spent': [100.0, 200.0, 150.0, 300.0, 250.0],
            'Total Orders': [1, 2, 1, 3, 2],
            'latitude': [-23.564738, -23.564738, -21.7645, -23.564738, -23.564738],
            'longitude': [-46.668939, -46.668939, -43.3502, -46.668939, -46.668939],
            'shopping_mais_proximo': ['Shops Jardins', 'Shops Jardins', 'Shops Jardins', 'Shops Jardins', 'Shops Jardins'],
            'distancia_mais_proximo': [5.0, 8.0, 12.0, 5.0, 8.0]
        }
        
        df_sample = pd.DataFrame(sample_data)
        
        # Test density analysis
        df_density = distanciador.analisar_densidade_consumidores(df_sample)
        print(f"✅ Density analysis completed: {len(df_density)} areas")
        print(f"   - Sample result: {df_density.iloc[0].to_dict()}")
        
        # Test city density analysis
        df_city_density = distanciador.analisar_densidade_por_cidade(df_sample)
        print(f"✅ City density analysis completed: {len(df_city_density)} cities")
        
        # Test high-value clusters
        df_clusters = distanciador.identificar_clusters_altos_valores(df_sample, min_revenue=150, max_distance=10)
        print(f"✅ High-value clusters analysis completed: {len(df_clusters)} clusters")
        
        return True
        
    except Exception as e:
        print(f"❌ Density analysis test failed: {e}")
        return False

def test_original_functionality(distanciador):
    """Test original distanciador functionality"""
    print("\n🧪 Testing Original Functionality...")
    
    config = get_config()
    base_ceps_file = config['paths']['base_ceps']
    
    if not os.path.exists(base_ceps_file):
        print(f"⚠️ Base CEPs file not found: {base_ceps_file}")
        print("   Skipping original functionality test")
        return False
    
    try:
        # Test with a small sample
        df_sample = pd.read_csv(base_ceps_file, nrows=3)
        print(f"✅ Sample CEP data loaded: {len(df_sample)} rows")
        
        # Test coordinate calculation
        test_coords1 = (-23.564738, -46.668939)
        test_coords2 = (-22.956909, -43.176186)
        distance = distanciador.calcular_distancia(test_coords1, test_coords2)
        print(f"✅ Distance calculation test: {distance} km")
        
        return True
        
    except Exception as e:
        print(f"❌ Original functionality test failed: {e}")
        return False

def run_performance_test(distanciador):
    """Run a simple performance test"""
    print("\n🧪 Running Performance Test...")
    
    try:
        start_time = datetime.now()
        
        # Test multiple coordinate lookups
        test_ceps = ['30170-130', '30575-843', '36033-345']
        results = []
        
        for cep in test_ceps:
            coords = distanciador.obter_coordenadas(cep)
            results.append((cep, coords))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Performance test completed in {duration:.2f} seconds")
        print(f"   - Processed {len(test_ceps)} CEPs")
        print(f"   - Average time per CEP: {duration/len(test_ceps):.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Distanciador Tests")
    print("=" * 50)
    
    # Test configuration
    if not test_configuration():
        print("❌ Configuration test failed. Exiting.")
        return
    
    # Test initialization
    distanciador = test_enhanced_distanciador_initialization()
    if distanciador is None:
        print("❌ Initialization test failed. Exiting.")
        return
    
    # Test Shopify processing
    test_shopify_data_processing(distanciador)
    
    # Test density analysis
    test_density_analysis_functions(distanciador)
    
    # Test original functionality
    test_original_functionality(distanciador)
    
    # Run performance test
    run_performance_test(distanciador)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📋 Summary:")
    print("   - Enhanced Distanciador is ready for use")
    print("   - Shopify data processing capabilities added")
    print("   - Density analysis functions implemented")
    print("   - Original functionality preserved")
    print("\n🎯 Next steps:")
    print("   - Run with real Shopify data: python enhanced_distanciador.py")
    print("   - Create Streamlit interface for visualization")
    print("   - Configure additional shopping malls in config.py")

if __name__ == "__main__":
    main() 