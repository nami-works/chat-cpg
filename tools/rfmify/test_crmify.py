"""
Test script for RFMify functionality
"""

import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rfmify_imports():
    """Test that all RFMify modules can be imported"""
    print("🧪 Testing RFMify imports...")
    
    try:
        from rfmify import CRMifyCore, RFMAnalyzer, ShopifyCustomerExporter
        print("✅ All RFMify modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_rfm_analyzer():
    """Test RFM analyzer functionality"""
    print("\n🧪 Testing RFM Analyzer...")
    
    try:
        from rfmify import RFMAnalyzer
        
        # Create sample data
        customers_data = {
            'customer_id': ['1', '2', '3', '4', '5'],
            'first_name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'last_name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com', 'alice@example.com', 'charlie@example.com'],
            'total_spent': [100.0, 500.0, 150.0, 1000.0, 250.0],
            'orders_count': [1, 3, 1, 5, 2]
        }
        
        orders_data = {
            'customer_id': ['1', '2', '2', '2', '3', '4', '4', '4', '4', '4', '5', '5'],
            'created_at': [
                datetime.now() - timedelta(days=30),
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=10),
                datetime.now() - timedelta(days=15),
                datetime.now() - timedelta(days=25),
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=3),
                datetime.now() - timedelta(days=4),
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=8),
                datetime.now() - timedelta(days=12)
            ],
            'total_price': [100.0, 200.0, 150.0, 150.0, 150.0, 200.0, 200.0, 200.0, 200.0, 200.0, 150.0, 100.0]
        }
        
        customers_df = pd.DataFrame(customers_data)
        orders_df = pd.DataFrame(orders_data)
        
        # Test RFM analysis
        rfm = RFMAnalyzer()
        
        # Calculate RFM scores
        customers_with_rfm = rfm.calculate_rfm_scores(customers_df, orders_df)
        print(f"✅ RFM scores calculated for {len(customers_with_rfm)} customers")
        
        # Classify segments
        segmented_customers = rfm.classify_rfm_segments(customers_with_rfm)
        print(f"✅ RFM segments classified")
        
        # Get summary
        summary = rfm.get_rfm_summary(segmented_customers)
        print(f"✅ RFM summary generated: {summary['segment_distribution']}")
        
        # Get recommendations
        recommendations = rfm.get_customer_recommendations(segmented_customers)
        print(f"✅ Customer recommendations generated: {len(recommendations)} recommendations")
        
        return True
        
    except Exception as e:
        print(f"❌ RFM analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_customer_exporter():
    """Test customer exporter functionality"""
    print("\n🧪 Testing Customer Exporter...")
    
    try:
        from rfmify import ShopifyCustomerExporter
        
        # Create sample data
        customers_data = {
            'customer_id': ['1', '2', '3'],
            'first_name': ['John', 'Jane', 'Bob'],
            'last_name': ['Doe', 'Smith', 'Johnson'],
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'total_spent': [100.0, 500.0, 150.0],
            'orders_count': [1, 3, 1]
        }
        
        orders_data = {
            'customer_id': ['1', '2', '2', '2', '3'],
            'created_at': [
                datetime.now() - timedelta(days=30),
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=10),
                datetime.now() - timedelta(days=15),
                datetime.now() - timedelta(days=25)
            ],
            'total_price': [100.0, 200.0, 150.0, 150.0, 150.0]
        }
        
        customers_df = pd.DataFrame(customers_data)
        orders_df = pd.DataFrame(orders_data)
        
        # Test exporter
        exporter = ShopifyCustomerExporter()
        
        # Test export summary
        summary = exporter.get_export_summary(customers_df, orders_df)
        print(f"✅ Export summary generated: {summary['total_customers']} customers")
        
        # Test data validation
        validation = exporter.validate_export_data(customers_df, orders_df)
        print(f"✅ Data validation completed: {validation['data_quality_score']}% quality score")
        
        # Test filename generation
        filename = exporter.get_export_filename('CSV')
        print(f"✅ Export filename generated: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Customer exporter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rfmify_core():
    """Test RFMify core functionality"""
    print("\n🧪 Testing CRMify Core...")
    
    try:
        from rfmify import CRMifyCore
        
        # Create sample data
        customers_data = {
            'customer_id': ['1', '2', '3'],
            'first_name': ['John', 'Jane', 'Bob'],
            'last_name': ['Doe', 'Smith', 'Johnson'],
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'total_spent': [100.0, 500.0, 150.0],
            'orders_count': [1, 3, 1]
        }
        
        orders_data = {
            'customer_id': ['1', '2', '2', '2', '3'],
            'created_at': [
                datetime.now() - timedelta(days=30),
                datetime.now() - timedelta(days=5),
                datetime.now() - timedelta(days=10),
                datetime.now() - timedelta(days=15),
                datetime.now() - timedelta(days=25)
            ],
            'total_price': [100.0, 200.0, 150.0, 150.0, 150.0]
        }
        
        customers_df = pd.DataFrame(customers_data)
        orders_df = pd.DataFrame(orders_data)
        
        # Test RFMify core
        rfmify = CRMifyCore()
        
        # Test customer segmentation
        segments = rfmify.analyze_customer_segments(customers_df, orders_df)
        print(f"✅ Customer segmentation completed: {segments['total_customers']} customers analyzed")
        
        # Test customer insights
        insights = rfmify.generate_customer_insights(customers_df, orders_df)
        print(f"✅ Customer insights generated: {len(insights['opportunities'])} opportunities found")
        
        # Test dashboard data
        dashboard_data = rfmify.get_customer_dashboard_data(customers_df, orders_df)
        print(f"✅ Dashboard data prepared: {len(dashboard_data['metrics'])} metrics calculated")
        
        # Test data validation
        validation = rfmify.validate_data(customers_df, orders_df)
        print(f"✅ Data validation completed: {validation['data_quality_score']}% quality score")
        
        return True
        
    except Exception as e:
        print(f"❌ CRMify core test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all CRMify tests"""
    print("🚀 RFMify Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_crmify_imports),
        ("RFM Analyzer Test", test_rfm_analyzer),
        ("Customer Exporter Test", test_customer_exporter),
        ("RFMify Core Test", test_rfmify_core)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! RFMify is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
