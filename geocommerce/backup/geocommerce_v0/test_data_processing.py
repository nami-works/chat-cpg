"""
Test script for GeoCommerce data processing
Validates Shopify data processing and helps debug issues.
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_shopify_data_processing(csv_path: str):
    """
    Test Shopify data processing without geocoding
    
    Args:
        csv_path: Path to Shopify CSV file
    """
    print("🧪 Testing Shopify Data Processing")
    print("=" * 50)
    
    try:
        # Load raw data
        print(f"📁 Loading data from: {csv_path}")
        df = pd.read_csv(csv_path)
        
        print(f"📊 Initial data shape: {df.shape}")
        print(f"📋 Columns found: {list(df.columns)}")
        
        # Check for required columns
        required_columns = ['Default Address Zip', 'Total Spent', 'Total Orders']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        print("✅ All required columns found")
        
        # Test data cleaning (without geocoding)
        print("\n🧹 Testing data cleaning...")
        
        # Clean CEP data
        df['cep'] = df['Default Address Zip'].astype(str).fillna('')
        df['cep'] = df['cep'].str.replace('-', '').str.strip()
        df['cep'] = df['cep'].str.zfill(8)
        
        # Filter out invalid CEPs
        initial_count = len(df)
        df = df[df['cep'] != '00000000'].copy()
        final_count = len(df)
        
        print(f"   - Initial records: {initial_count}")
        print(f"   - Valid records: {final_count}")
        print(f"   - Filtered out: {initial_count - final_count}")
        
        # Clean Total Spent
        df['Total Spent'] = df['Total Spent'].astype(str).fillna('0')
        df['Total Spent'] = pd.to_numeric(
            df['Total Spent'].str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0)
        
        # Clean Total Orders
        df['Total Orders'] = pd.to_numeric(df['Total Orders'], errors='coerce').fillna(0)
        
        # Show sample of cleaned data
        print("\n📋 Sample of cleaned data:")
        sample_cols = ['cep', 'Total Spent', 'Total Orders']
        if 'Default Address City' in df.columns:
            sample_cols.append('Default Address City')
        
        print(df[sample_cols].head())
        
        # Show data statistics
        print("\n📈 Data Statistics:")
        print(f"   - Total revenue: R$ {df['Total Spent'].sum():,.2f}")
        print(f"   - Total orders: {df['Total Orders'].sum():,}")
        print(f"   - Average order value: R$ {df['Total Spent'].sum() / df['Total Orders'].sum():.2f}")
        print(f"   - Unique CEPs: {df['cep'].nunique()}")
        
        if 'Default Address City' in df.columns:
            print(f"   - Unique cities: {df['Default Address City'].nunique()}")
            print(f"   - Top cities: {df['Default Address City'].value_counts().head(3).to_dict()}")
        
        print("\n✅ Data processing test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during data processing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run data processing tests"""
    print("🚀 GeoCommerce Data Processing Test")
    print("=" * 50)
    
    # Look for Shopify data file
    possible_files = [
        'customers_export.csv',
        'shopify_export.csv',
        'customers.csv'
    ]
    
    csv_file = None
    for filename in possible_files:
        if os.path.exists(filename):
            csv_file = filename
            break
    
    if csv_file:
        print(f"📁 Found Shopify data file: {csv_file}")
        success = test_shopify_data_processing(csv_file)
        
        if success:
            print("\n🎉 All tests passed! Data processing is working correctly.")
        else:
            print("\n⚠️ Some tests failed. Check the error messages above.")
    else:
        print("❌ No Shopify data file found!")
        print("Please place one of these files in the geocommerce directory:")
        for filename in possible_files:
            print(f"   - {filename}")
        print("\nOr run this script with a specific file path.")

if __name__ == "__main__":
    main() 