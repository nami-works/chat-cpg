"""
GeoCommerce Test Suite
Comprehensive testing for the GeoCommerce platform.
"""

import os
import sys
import pandas as pd
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from geocommerce_core import GeoCommerce
from config import get_default_config, validate_config, get_ecommerce_config, get_retail_config

class GeoCommerceTestSuite:
    """Comprehensive test suite for GeoCommerce"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.geocommerce = None
    
    def setup_test_environment(self):
        """Set up test environment with temporary directory"""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp(prefix="geocommerce_test_")
        
        # Initialize GeoCommerce with test configuration
        test_config = get_default_config()
        test_config['paths']['output'] = self.temp_dir
        
        self.geocommerce = GeoCommerce(test_config)
        
        print(f"✅ Test environment ready: {self.temp_dir}")
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("🧹 Test environment cleaned up")
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        print(f"\n🧪 Running test: {test_name}")
        
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} - PASSED")
                self.test_results.append((test_name, True, None))
            else:
                print(f"❌ {test_name} - FAILED")
                self.test_results.append((test_name, False, "Test returned False"))
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            self.test_results.append((test_name, False, str(e)))
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        print("\n1. Testing Configuration Validation...")
        
        # Test default configuration
        default_config = get_default_config()
        if not validate_config(default_config):
            return False
        
        # Test e-commerce configuration
        ecommerce_config = get_ecommerce_config()
        if not validate_config(ecommerce_config):
            return False
        
        # Test retail configuration
        retail_config = get_retail_config()
        if not validate_config(retail_config):
            return False
        
        # Test invalid configuration
        invalid_config = default_config.copy()
        invalid_config['analysis']['high_value_min_revenue'] = -100
        if validate_config(invalid_config):
            return False  # Should fail validation
        
        return True
    
    def test_geocommerce_initialization(self):
        """Test GeoCommerce initialization"""
        print("\n2. Testing GeoCommerce Initialization...")
        
        # Test with default configuration
        geocommerce = GeoCommerce()
        info = geocommerce.get_system_info()
        
        if info['system_name'] != 'GeoCommerce':
            return False
        
        if info['version'] != '1.0.0':
            return False
        
        if len(info['shopping_locations']) == 0:
            return False
        
        # Test with custom configuration
        custom_config = get_ecommerce_config()
        geocommerce_custom = GeoCommerce(custom_config)
        custom_info = geocommerce_custom.get_system_info()
        
        if custom_info['system_name'] != 'GeoCommerce':
            return False
        
        return True
    
    def test_coordinate_calculation(self):
        """Test distance calculation functionality"""
        print("\n3. Testing Coordinate Calculations...")
        
        # Test valid coordinates
        coords1 = (-23.564738, -46.668939)  # São Paulo
        coords2 = (-22.956909, -43.176186)  # Rio de Janeiro
        
        distance = self.geocommerce.calculate_distance(coords1, coords2)
        
        if not isinstance(distance, float):
            return False
        
        if distance <= 0:
            return False
        
        # Test invalid coordinates
        invalid_coords = (None, None)
        distance_invalid = self.geocommerce.calculate_distance(coords1, invalid_coords)
        
        if distance_invalid != float('inf'):
            return False
        
        return True
    
    def test_sample_data_processing(self):
        """Test data processing with sample data"""
        print("\n4. Testing Sample Data Processing...")
        
        # Create sample Shopify data
        sample_data = {
            'Customer ID': ['1', '2', '3', '4', '5'],
            'Default Address Zip': ['30170-130', '30575-843', '36033-345', '30170-130', '30575-843'],
            'Default Address City': ['Belo Horizonte', 'Belo Horizonte', 'Juiz de Fora', 'Belo Horizonte', 'Belo Horizonte'],
            'Total Spent': [100.0, 200.0, 150.0, 300.0, 250.0],
            'Total Orders': [1, 2, 1, 3, 2],
            'latitude': [-23.564738, -23.564738, -21.7645, -23.564738, -23.564738],
            'longitude': [-46.668939, -46.668939, -43.3502, -46.668939, -46.668939]
        }
        
        df_sample = pd.DataFrame(sample_data)
        
        # Test density analysis
        df_density = self.geocommerce.analyze_customer_density(df_sample)
        
        if len(df_density) == 0:
            return False
        
        if 'customer_count' not in df_density.columns:
            return False
        
        # Test city density analysis
        df_city_density = self.geocommerce.analyze_city_density(df_sample)
        
        if len(df_city_density) == 0:
            return False
        
        if 'total_customers' not in df_city_density.columns:
            return False
        
        # Test high-value clusters
        df_clusters = self.geocommerce.identify_high_value_clusters(df_sample, min_revenue=150, max_distance=10)
        
        if 'high_value_customers' not in df_clusters.columns:
            return False
        
        return True
    
    def test_geocoding_mock(self):
        """Test geocoding with mocked responses"""
        print("\n5. Testing Geocoding (Mocked)...")
        
        # Mock geocoding response
        mock_location = MagicMock()
        mock_location.latitude = -23.564738
        mock_location.longitude = -46.668939
        
        with patch.object(self.geocommerce.geolocator, 'geocode', return_value=mock_location):
            coords = self.geocommerce.get_coordinates('30170-130')
            
            if coords != (-23.564738, -46.668939):
                return False
        
        # Test cache functionality
        coords_cached = self.geocommerce.get_coordinates('30170-130')
        
        if coords_cached != (-23.564738, -46.668939):
            return False
        
        return True
    
    def test_file_operations(self):
        """Test file operations and output generation"""
        print("\n6. Testing File Operations...")
        
        # Create sample data for file operations
        sample_data = {
            'Customer ID': ['1', '2', '3'],
            'Default Address Zip': ['30170-130', '30575-843', '36033-345'],
            'Default Address City': ['Belo Horizonte', 'Belo Horizonte', 'Juiz de Fora'],
            'Total Spent': [100.0, 200.0, 150.0],
            'Total Orders': [1, 2, 1],
            'latitude': [-23.564738, -23.564738, -21.7645],
            'longitude': [-46.668939, -46.668939, -43.3502],
            'nearest_shopping': ['Shops Jardins', 'Shops Jardins', 'Shops Jardins'],
            'distance_to_nearest': [5.0, 8.0, 12.0]
        }
        
        df_sample = pd.DataFrame(sample_data)
        
        # Test CSV output
        csv_path = os.path.join(self.temp_dir, 'test_output.csv')
        df_sample.to_csv(csv_path, index=False)
        
        if not os.path.exists(csv_path):
            return False
        
        # Test JSON output
        json_path = os.path.join(self.temp_dir, 'test_output.json')
        summary = {
            'total_customers': len(df_sample),
            'total_revenue': float(df_sample['Total Spent'].sum()),
            'test_timestamp': datetime.now().isoformat()
        }
        
        import json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        if not os.path.exists(json_path):
            return False
        
        return True
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n7. Testing Error Handling...")
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        
        try:
            df_density = self.geocommerce.analyze_customer_density(empty_df)
            # Should handle empty DataFrame gracefully
        except Exception as e:
            print(f"Error handling empty DataFrame: {e}")
            return False
        
        # Test with missing columns
        incomplete_data = {
            'Customer ID': ['1', '2'],
            'Total Spent': [100.0, 200.0]
        }
        incomplete_df = pd.DataFrame(incomplete_data)
        
        try:
            df_city_density = self.geocommerce.analyze_city_density(incomplete_df)
            # Should handle missing columns gracefully
        except Exception as e:
            print(f"Error handling incomplete data: {e}")
            return False
        
        return True
    
    def test_performance_benchmarks(self):
        """Test performance with larger datasets"""
        print("\n8. Testing Performance Benchmarks...")
        
        # Create larger sample dataset
        large_data = {
            'Customer ID': [str(i) for i in range(100)],
            'Default Address Zip': ['30170-130'] * 100,
            'Default Address City': ['Belo Horizonte'] * 100,
            'Total Spent': [100.0 + i for i in range(100)],
            'Total Orders': [1] * 100,
            'latitude': [-23.564738] * 100,
            'longitude': [-46.668939] * 100,
            'nearest_shopping': ['Shops Jardins'] * 100,
            'distance_to_nearest': [5.0] * 100
        }
        
        df_large = pd.DataFrame(large_data)
        
        # Test processing time
        start_time = datetime.now()
        
        df_density = self.geocommerce.analyze_customer_density(df_large)
        df_city_density = self.geocommerce.analyze_city_density(df_large)
        df_clusters = self.geocommerce.identify_high_value_clusters(df_large)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"   - Processing time: {processing_time:.2f} seconds")
        
        # Should complete within reasonable time (less than 5 seconds)
        if processing_time > 5.0:
            print(f"   - Performance warning: Processing took {processing_time:.2f} seconds")
        
        if len(df_density) == 0 or len(df_city_density) == 0:
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all tests in the suite"""
        print("🚀 Starting GeoCommerce Test Suite")
        print("=" * 60)
        
        try:
            self.setup_test_environment()
            
            # Run all tests
            self.run_test("Configuration Validation", self.test_configuration_validation)
            self.run_test("GeoCommerce Initialization", self.test_geocommerce_initialization)
            self.run_test("Coordinate Calculations", self.test_coordinate_calculation)
            self.run_test("Sample Data Processing", self.test_sample_data_processing)
            self.run_test("Geocoding (Mocked)", self.test_geocoding_mock)
            self.run_test("File Operations", self.test_file_operations)
            self.run_test("Error Handling", self.test_error_handling)
            self.run_test("Performance Benchmarks", self.test_performance_benchmarks)
            
        finally:
            self.cleanup_test_environment()
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_name, passed, error in self.test_results:
                if not passed:
                    print(f"   - {test_name}: {error}")
        
        print("\n✅ Passed Tests:")
        for test_name, passed, _ in self.test_results:
            if passed:
                print(f"   - {test_name}")
        
        # Overall result
        if failed_tests == 0:
            print("\n🎉 All tests passed! GeoCommerce is ready for use.")
        else:
            print(f"\n⚠️ {failed_tests} test(s) failed. Please review and fix issues.")
        
        print("\n" + "=" * 60)

def main():
    """Main function to run the test suite"""
    test_suite = GeoCommerceTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main() 