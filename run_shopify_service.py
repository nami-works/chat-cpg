#!/usr/bin/env python3
"""
Shopify Service Runner

This script provides a command-line interface to run and manage the Shopify service.
It can be used to start the service, perform manual syncs, check status, and manage configuration.
"""

import argparse
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from geocommerce import get_shopify_service
from geocommerce.config import get_config, validate_config, get_preset_config

def setup_environment_variables():
    """
    Setup environment variables from .env file if it exists
    """
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # dotenv not available

def initialize_service(args):
    """Initialize the Shopify service"""
    service = get_shopify_service()
    
    if args.shop_name and args.access_token:
        # Initialize with provided credentials
        success = service.initialize(args.shop_name, args.access_token, args.api_version)
    elif args.from_env:
        # Initialize from environment variables
        success = service.initialize_from_env()
    else:
        # Initialize from config file
        success = service.initialize_from_config()
    
    if success:
        print(f"✅ Shopify service initialized successfully")
        if args.test:
            print("🧪 Running connection test...")
            if service.data_manager.connector.test_connection():
                print("✅ Connection test passed")
            else:
                print("❌ Connection test failed")
                return False
    else:
        print("❌ Failed to initialize Shopify service")
        return False
    
    return True

def sync_data(args):
    """Sync data from Shopify"""
    service = get_shopify_service()
    
    if not service.ensure_initialized():
        print("❌ Service not initialized. Please run 'initialize' first.")
        return False
    
    entities = args.entities if args.entities else ["products", "orders", "customers", "collections"]
    
    print(f"🔄 Starting sync for: {', '.join(entities)}")
    
    if args.force:
        print("🔨 Force sync enabled")
    
    # Sync each entity
    for entity in entities:
        print(f"📦 Syncing {entity}...")
        
        try:
            if entity == "products":
                success = service.data_manager.sync_products(force_update=args.force)
            elif entity == "orders":
                success = service.data_manager.sync_orders(force_update=args.force)
            elif entity == "customers":
                success = service.data_manager.sync_customers(force_update=args.force)
            elif entity == "collections":
                success = service.data_manager.sync_collections(force_update=args.force)
            else:
                print(f"❌ Unknown entity: {entity}")
                continue
            
            if success:
                print(f"✅ {entity} synced successfully")
            else:
                print(f"❌ Failed to sync {entity}")
                
        except Exception as e:
            print(f"❌ Error syncing {entity}: {str(e)}")
    
    return True

def show_status(args):
    """Show service status"""
    service = get_shopify_service()
    
    print("📊 Shopify Service Status")
    print("=" * 40)
    
    status = service.get_service_status()
    
    print(f"Initialized: {'✅' if status['is_initialized'] else '❌'}")
    print(f"Shop Name: {status['config'].get('shop_name', 'Not configured')}")
    print(f"Auto Sync: {'✅' if status['config'].get('auto_sync_enabled') else '❌'}")
    print(f"Sync Time: {status['config'].get('sync_time', 'Not configured')}")
    
    if status['scheduler']:
        scheduler_status = status['scheduler']
        print(f"Scheduler Running: {'✅' if scheduler_status['is_running'] else '❌'}")
        if scheduler_status['next_sync']:
            print(f"Next Sync: {scheduler_status['next_sync']}")
    
    print("\n📈 Data Freshness")
    print("-" * 20)
    
    for entity, info in status['data_freshness'].items():
        if info['last_sync']:
            age_str = f"{info['age_hours']:.1f}h ago"
            needs_update = "🔄" if info['needs_update'] else "✅"
            print(f"{entity.title()}: {age_str} {needs_update}")
        else:
            print(f"{entity.title()}: Never synced 🔄")

def show_data_summary(args):
    """Show summary of cached data"""
    service = get_shopify_service()
    
    if not service.ensure_initialized():
        print("❌ Service not initialized. Please run 'initialize' first.")
        return False
    
    print("📋 Data Summary")
    print("=" * 40)
    
    try:
        products = service.get_products()
        orders = service.get_orders()
        customers = service.get_customers()
        collections = service.get_collections()
        
        print(f"Products: {len(products)}")
        print(f"Orders: {len(orders)}")
        print(f"Customers: {len(customers)}")
        print(f"Collections: {len(collections)}")
        
        if args.details:
            print("\n📦 Recent Products (top 5):")
            for product in products[:5]:
                print(f"  - {product.get('title', 'Unknown')}")
            
            print("\n🛍️ Recent Orders (top 5):")
            for order in orders[:5]:
                print(f"  - Order #{order.get('order_number', 'Unknown')} - ${order.get('total_price', '0')}")
    
    except Exception as e:
        print(f"❌ Error retrieving data: {str(e)}")

def show_sync_history(args):
    """Show sync history"""
    service = get_shopify_service()
    
    if not service.ensure_initialized():
        print("❌ Service not initialized. Please run 'initialize' first.")
        return False
    
    print("📜 Sync History")
    print("=" * 40)
    
    try:
        history = service.get_sync_history(args.limit)
        
        if not history:
            print("No sync history found.")
            return
        
        for record in history:
            status_icon = "✅" if record['status'] == 'completed' else "❌" if record['status'] == 'failed' else "🔄"
            print(f"{status_icon} {record['entity_type']} - {record['sync_started']}")
            if record['status'] == 'completed':
                print(f"    Records: {record['records_processed']}")
            elif record['status'] == 'failed' and record['error_message']:
                print(f"    Error: {record['error_message']}")
    
    except Exception as e:
        print(f"❌ Error retrieving sync history: {str(e)}")

def configure_service(args):
    """Configure service settings"""
    service = get_shopify_service()
    
    if args.preset:
        print(f"🔧 Applying preset: {args.preset}")
        try:
            config = get_preset_config(args.preset)
            service.update_config(config)
            print("✅ Configuration updated successfully")
        except ValueError as e:
            print(f"❌ {str(e)}")
            return False
    
    if args.sync_time:
        print(f"⏰ Setting sync time to: {args.sync_time}")
        service.update_config({"sync_time": args.sync_time})
        print("✅ Sync time updated")
    
    if args.enable_sync is not None:
        sync_enabled = args.enable_sync
        print(f"🔄 {'Enabling' if sync_enabled else 'Disabling'} auto sync")
        service.update_config({"auto_sync_enabled": sync_enabled})
        print("✅ Auto sync setting updated")
    
    return True

def run_service(args):
    """Run the service in the foreground"""
    service = get_shopify_service()
    
    if not service.ensure_initialized():
        print("❌ Service not initialized. Please run 'initialize' first.")
        return False
    
    print("🚀 Starting Shopify service...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print(f"⏰ Service running... {time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Stopping service...")
        service.stop()
        print("✅ Service stopped")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Shopify Service Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize with credentials
  python run_shopify_service.py init --shop-name myshop --access-token xxxxx
  
  # Initialize from environment
  python run_shopify_service.py init --from-env
  
  # Sync all data
  python run_shopify_service.py sync
  
  # Sync specific entities
  python run_shopify_service.py sync --entities products orders
  
  # Force sync
  python run_shopify_service.py sync --force
  
  # Show status
  python run_shopify_service.py status
  
  # Show data summary
  python run_shopify_service.py data --details
  
  # Configure service
  python run_shopify_service.py config --preset production
  python run_shopify_service.py config --sync-time 03:00 --enable-sync
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize the service')
    init_parser.add_argument('--shop-name', help='Shopify shop name')
    init_parser.add_argument('--access-token', help='Shopify access token')
    init_parser.add_argument('--api-version', default='2024-01', help='API version')
    init_parser.add_argument('--from-env', action='store_true', help='Initialize from environment variables')
    init_parser.add_argument('--test', action='store_true', help='Test connection after initialization')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync data from Shopify')
    sync_parser.add_argument('--entities', nargs='+', choices=['products', 'orders', 'customers', 'collections'],
                           help='Entities to sync')
    sync_parser.add_argument('--force', action='store_true', help='Force sync even if data is recent')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show service status')
    
    # Data command
    data_parser = subparsers.add_parser('data', help='Show data summary')
    data_parser.add_argument('--details', action='store_true', help='Show detailed information')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show sync history')
    history_parser.add_argument('--limit', type=int, default=10, help='Number of records to show')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure service')
    config_parser.add_argument('--preset', choices=['development', 'production', 'testing'],
                             help='Apply configuration preset')
    config_parser.add_argument('--sync-time', help='Set sync time (HH:MM format)')
    config_parser.add_argument('--enable-sync', action='store_true', help='Enable auto sync')
    config_parser.add_argument('--disable-sync', action='store_false', dest='enable_sync',
                             help='Disable auto sync')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run service in foreground')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup environment
    setup_environment_variables()
    
    # Execute command
    try:
        if args.command == 'init':
            success = initialize_service(args)
        elif args.command == 'sync':
            success = sync_data(args)
        elif args.command == 'status':
            success = show_status(args)
        elif args.command == 'data':
            success = show_data_summary(args)
        elif args.command == 'history':
            success = show_sync_history(args)
        elif args.command == 'config':
            success = configure_service(args)
        elif args.command == 'run':
            success = run_service(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            success = False
        
        if not success:
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()