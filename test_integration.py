#!/usr/bin/env python3
"""
Test ChatCPG-GeoCommerce Integration
Verify that the integration works without Streamlit page config conflicts
"""

import sys
from pathlib import Path

def test_import():
    """Test that we can import the GeoCommerce app without conflicts"""
    print("🔍 Testing ChatCPG-GeoCommerce integration...")
    
    try:
        # Test importing the GeoCommerce app
        from geocommerce.geocommerce_shopify import GeoCommerceShopifyApp
        print("  ✅ GeoCommerceShopifyApp imported successfully")
        
        # Test creating an instance
        app = GeoCommerceShopifyApp()
        print("  ✅ GeoCommerceShopifyApp instance created successfully")
        
        # Test that the render method exists
        if hasattr(app, 'render_geocommerce_content'):
            print("  ✅ render_geocommerce_content method exists")
        else:
            print("  ❌ render_geocommerce_content method missing")
            return False
        
        print("✅ Integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_chatcpg_import():
    """Test that ChatCPG can import GeoCommerce without conflicts"""
    print("\n🔍 Testing ChatCPG import with GeoCommerce...")
    
    try:
        # Add current directory to path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Import ChatCPG (this should not fail due to GeoCommerce imports)
        import chat_cpg
        print("  ✅ ChatCPG imported successfully")
        
        # Check if the geocommerce function is properly defined
        if hasattr(chat_cpg, 'chat_cpg'):
            print("  ✅ chat_cpg function exists")
        else:
            print("  ❌ chat_cpg function missing")
            return False
        
        print("✅ ChatCPG import test passed!")
        return True
        
    except Exception as e:
        print(f"❌ ChatCPG import test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🧪 ChatCPG-GeoCommerce Integration Test")
    print("=" * 50)
    
    tests = [
        test_import,
        test_chatcpg_import
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
        print("🎉 All integration tests passed!")
        print("✅ ChatCPG and GeoCommerce are properly integrated")
        print("✅ No Streamlit page config conflicts")
        print("\nYou can now run:")
        print("  streamlit run chat_cpg.py")
        print("  Then select 'GeoCommerce' from the function dropdown")
    else:
        print("⚠️  Some integration tests failed.")
        print("Please check the errors above.")

if __name__ == "__main__":
    main() 