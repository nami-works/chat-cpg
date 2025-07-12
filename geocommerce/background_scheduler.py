import os
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional
import schedule
import json
from pathlib import Path

from .shopify_data_manager import ShopifyDataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shopify_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackgroundScheduler:
    """
    Background scheduler for automatic daily Shopify data updates.
    Runs as a separate thread and handles scheduled synchronization.
    """
    
    def __init__(self, data_manager: ShopifyDataManager, config_file: str = "scheduler_config.json"):
        """
        Initialize background scheduler
        
        Args:
            data_manager: ShopifyDataManager instance
            config_file: Configuration file path
        """
        self.data_manager = data_manager
        self.config_file = config_file
        self.is_running = False
        self.scheduler_thread = None
        self._stop_event = threading.Event()
        
        # Load configuration
        self.config = self.load_config()
        
        # Setup schedule
        self.setup_schedule()
        
    def load_config(self) -> Dict:
        """Load scheduler configuration"""
        default_config = {
            "sync_time": "02:00",  # 2 AM daily
            "sync_enabled": True,
            "sync_entities": ["products", "orders", "customers", "collections"],
            "retry_attempts": 3,
            "retry_delay_minutes": 15,
            "orders_days_back": 30,
            "max_log_age_days": 30
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            else:
                # Save default config
                self.save_config(default_config)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
        
        return default_config
    
    def save_config(self, config: Dict):
        """Save scheduler configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
    
    def setup_schedule(self):
        """Setup sync schedule"""
        if self.config.get("sync_enabled", True):
            sync_time = self.config.get("sync_time", "02:00")
            schedule.every().day.at(sync_time).do(self.run_scheduled_sync)
            logger.info(f"Scheduled daily sync at {sync_time}")
        
        # Schedule log cleanup weekly
        schedule.every().sunday.at("03:00").do(self.cleanup_old_logs)
    
    def run_scheduled_sync(self):
        """Run the scheduled sync process"""
        if not self.config.get("sync_enabled", True):
            logger.info("Sync is disabled in configuration")
            return
        
        logger.info("Starting scheduled sync...")
        
        try:
            # Get sync configuration
            entities = self.config.get("sync_entities", ["products", "orders", "customers", "collections"])
            retry_attempts = self.config.get("retry_attempts", 3)
            retry_delay = self.config.get("retry_delay_minutes", 15)
            
            # Track sync results
            sync_results = {}
            
            # Sync each entity type
            for entity in entities:
                success = False
                
                for attempt in range(retry_attempts):
                    try:
                        if entity == "products":
                            success = self.data_manager.sync_products(force_update=True)
                        elif entity == "orders":
                            days_back = self.config.get("orders_days_back", 30)
                            success = self.data_manager.sync_orders(force_update=True, days_back=days_back)
                        elif entity == "customers":
                            success = self.data_manager.sync_customers(force_update=True)
                        elif entity == "collections":
                            success = self.data_manager.sync_collections(force_update=True)
                        
                        if success:
                            logger.info(f"Successfully synced {entity}")
                            break
                        else:
                            logger.warning(f"Failed to sync {entity} (attempt {attempt + 1}/{retry_attempts})")
                            
                    except Exception as e:
                        logger.error(f"Error syncing {entity} (attempt {attempt + 1}/{retry_attempts}): {str(e)}")
                    
                    # Wait before retry (except on last attempt)
                    if attempt < retry_attempts - 1:
                        logger.info(f"Waiting {retry_delay} minutes before retry...")
                        time.sleep(retry_delay * 60)
                
                sync_results[entity] = success
            
            # Log overall results
            successful_syncs = sum(1 for success in sync_results.values() if success)
            total_syncs = len(sync_results)
            
            logger.info(f"Scheduled sync completed: {successful_syncs}/{total_syncs} entities synced successfully")
            
            # Send notifications if configured
            self.send_sync_notification(sync_results)
            
        except Exception as e:
            logger.error(f"Error in scheduled sync: {str(e)}")
    
    def send_sync_notification(self, sync_results: Dict[str, bool]):
        """Send notification about sync results (placeholder for future implementation)"""
        # This can be extended to send email notifications, webhooks, etc.
        pass
    
    def cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            max_age_days = self.config.get("max_log_age_days", 30)
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Clean up JSON cache files
            if hasattr(self.data_manager, 'json_cache_dir'):
                cache_dir = self.data_manager.json_cache_dir
                for file_path in cache_dir.glob("*.json"):
                    if file_path.name.endswith("_latest.json"):
                        continue  # Keep latest files
                    
                    try:
                        # Parse timestamp from filename
                        timestamp_str = file_path.stem.split("_")[-2:]
                        if len(timestamp_str) == 2:
                            timestamp = datetime.strptime(f"{timestamp_str[0]}_{timestamp_str[1]}", "%Y%m%d_%H%M%S")
                            if timestamp < cutoff_date:
                                file_path.unlink()
                                logger.info(f"Deleted old cache file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Could not process cache file {file_path}: {str(e)}")
            
            # Clean up old sync history
            try:
                with self.data_manager.get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        DELETE FROM sync_history 
                        WHERE sync_started < ?
                    ''', (cutoff_date.isoformat(),))
                    
                    deleted_count = cursor.rowcount
                    conn.commit()
                    
                    if deleted_count > 0:
                        logger.info(f"Deleted {deleted_count} old sync history records")
                        
            except Exception as e:
                logger.error(f"Error cleaning up sync history: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in cleanup_old_logs: {str(e)}")
    
    def start(self):
        """Start the background scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Background scheduler started")
    
    def stop(self):
        """Stop the background scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("Background scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        logger.info("Scheduler thread started")
        
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
                
                # Check every minute
                self._stop_event.wait(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler thread: {str(e)}")
                time.sleep(60)
        
        logger.info("Scheduler thread stopped")
    
    def force_sync_now(self, entities: Optional[list] = None):
        """
        Force a sync to run immediately
        
        Args:
            entities: List of entities to sync, or None for all
        """
        if entities is None:
            entities = self.config.get("sync_entities", ["products", "orders", "customers", "collections"])
        
        logger.info(f"Force sync requested for: {entities}")
        
        # Run sync in a separate thread to avoid blocking
        sync_thread = threading.Thread(
            target=self._run_force_sync,
            args=(entities,),
            daemon=True
        )
        sync_thread.start()
    
    def _run_force_sync(self, entities: list):
        """Run force sync in separate thread"""
        try:
            sync_results = {}
            
            for entity in entities:
                try:
                    if entity == "products":
                        success = self.data_manager.sync_products(force_update=True)
                    elif entity == "orders":
                        days_back = self.config.get("orders_days_back", 30)
                        success = self.data_manager.sync_orders(force_update=True, days_back=days_back)
                    elif entity == "customers":
                        success = self.data_manager.sync_customers(force_update=True)
                    elif entity == "collections":
                        success = self.data_manager.sync_collections(force_update=True)
                    else:
                        success = False
                    
                    sync_results[entity] = success
                    
                    if success:
                        logger.info(f"Force sync successful for {entity}")
                    else:
                        logger.error(f"Force sync failed for {entity}")
                        
                except Exception as e:
                    logger.error(f"Error in force sync for {entity}: {str(e)}")
                    sync_results[entity] = False
            
            # Log overall results
            successful_syncs = sum(1 for success in sync_results.values() if success)
            total_syncs = len(sync_results)
            
            logger.info(f"Force sync completed: {successful_syncs}/{total_syncs} entities synced successfully")
            
        except Exception as e:
            logger.error(f"Error in force sync: {str(e)}")
    
    def get_next_sync_time(self) -> Optional[str]:
        """Get the next scheduled sync time"""
        try:
            next_run = schedule.next_run()
            if next_run:
                return next_run.isoformat()
        except Exception as e:
            logger.error(f"Error getting next sync time: {str(e)}")
        
        return None
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "sync_enabled": self.config.get("sync_enabled", True),
            "sync_time": self.config.get("sync_time", "02:00"),
            "next_sync": self.get_next_sync_time(),
            "sync_entities": self.config.get("sync_entities", []),
            "config": self.config
        }
    
    def update_config(self, new_config: Dict):
        """Update scheduler configuration"""
        self.config.update(new_config)
        self.save_config(self.config)
        
        # Restart scheduler to apply new config
        if self.is_running:
            self.stop()
            self.setup_schedule()
            self.start()
        
        logger.info("Scheduler configuration updated")