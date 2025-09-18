#!/usr/bin/env python3
"""
GeoCommerce Setup Test
Verify that all components are properly installed and configured
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    required_packages = [
        ('streamlit', 'Streamlit'),
        ('pandas', 'Pandas'),
        ('plotly', 'Plotly'),
        ('folium', 'Folium'),
        ('geopy', 'GeoPy'),
        ('sklearn', 'Scikit-learn'),
        ('aiohttp', 'AsyncIO HTTP'),
        ('requests', 'Requests'),
        ('numpy', 'NumPy'),
        ('dotenv', 'Python-dotenv')
    ]
    
    missing_packages = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r geocommerce/requirements.txt")
        return False
    
    print("✅ All required packages are installed!")
    return True

def test_geocommerce_imports():
    """Test GeoCommerce module imports"""
    print("\n🔍 Testing GeoCommerce imports...")
    
    try:
        # Add current directory to path
        current_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(current_dir))
        
        from tools.geocommerce.config import GeoCommerceConfig
        print("  ✅ Config module")
        
        from tools.shopify_connector import ShopifyGraphQLClient
        print("  ✅ Shopify connector")
        
        from tools.geocommerce.api_data_processor import ShopifyDataProcessor
        print("  ✅ Data processor")
        
        from tools.geocommerce.geocommerce_core import GeoCommerceAnalyzer
        print("  ✅ Analytics core")
        
        from tools.geocommerce.geocommerce_shopify import GeoCommerceShopifyApp
        print("  ✅ Streamlit app")
        
        print("✅ All GeoCommerce modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n🔍 Testing environment configuration...")
    
    env_file = Path('.env')
    if env_file.exists():
        print("  ✅ .env file found")
        
        # Load and check environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            'SHOPIFY_SHOP_NAME',
            'SHOPIFY_ACCESS_TOKEN',
            'SHOPIFY_API_VERSION'
        ]
        
        missing_vars = []
        for var in required_vars:
            if os.getenv(var):
                print(f"  ✅ {var} is set")
            else:
                print(f"  ❌ {var} is missing")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        print("✅ Environment variables are properly configured!")
        return True
    else:
        print("  ⚠️  .env file not found")
        print("     Create a .env file with your Shopify credentials")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from tools.geocommerce.config import GeoCommerceConfig
        
        config = GeoCommerceConfig()
        print(f"  ✅ App Name: {config.APP_NAME}")
        print(f"  ✅ Version: {config.APP_VERSION}")
        print(f"  ✅ Default Map Center: {config.DEFAULT_MAP_CENTER}")
        
        # Test credential validation
        validation = config.validate_shopify_credentials()
        if validation['valid']:
            print("  ✅ Shopify credentials validation passed")
        else:
            print("  ⚠️  Shopify credentials validation failed")
            for error in validation['errors']:
                print(f"     - {error}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_directories():
    """Test directory structure"""
    print("\n🔍 Testing directory structure...")
    
    required_files = [
        'geocommerce/__init__.py',
        'geocommerce/config.py',
        'geocommerce/shopify_connector.py',
        'geocommerce/api_data_processor.py',
        'geocommerce/geocommerce_core.py',
        'geocommerce/geocommerce_shopify.py',
        'geocommerce/requirements.txt',
        'geocommerce/README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files are present!")
    return True

def main():
    """Run all tests"""
    print("🧪 GeoCommerce Setup Test")
    print("=" * 50)
    
    tests = [
        test_directories,
        test_imports,
        test_geocommerce_imports,
        test_environment,
        test_config
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! GeoCommerce is ready to use.")
        print("\nTo start the application, run:")
        print("  python run_geocommerce.py")
        print("  or")
        print("  streamlit run geocommerce/geocommerce_shopify.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nFor help, check the README.md file in the geocommerce directory.")

if __name__ == "__main__":
    main()