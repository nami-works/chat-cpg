import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional
import streamlit as st

# Import the Google Ads keyword research class
try:
    from tools.google_ads_keyword_research import GoogleAdsKeywordResearch
    GOOGLE_ADS_RESEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_RESEARCH_AVAILABLE = False
    st.warning("Google Ads keyword research not available")

class MultiBrandKeywordManager:
    """Manages keyword research across multiple brands"""
    
    def __init__(self):
        self.brands_dir = Path("z_brands")
        self.keyword_researchers = {}
    
    def get_available_brands(self) -> List[str]:
        """Get list of available brands with keyword research enabled"""
        available_brands = []
        
        if not self.brands_dir.exists():
            st.warning("z_brands directory not found")
            return available_brands
        
        for brand_dir in self.brands_dir.iterdir():
            if brand_dir.is_dir():
                brand_id = brand_dir.name
                
                # Check if brand has keyword research enabled
                if self._is_keyword_research_enabled(brand_id):
                    available_brands.append(brand_id)
        
        return available_brands
    
    def _is_keyword_research_enabled(self, brand_id: str) -> bool:
        """Check if keyword research is enabled for a brand"""
        try:
            # Check .env file
            env_path = Path(f"z_brands/{brand_id}/.env")
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('KEYWORD_RESEARCH_ENABLED='):
                            return line.strip().split('=')[1].lower() == 'true'
            
            # Check registration.yaml
            registration_path = Path(f"z_brands/{brand_id}/registration.yaml")
            if registration_path.exists():
                with open(registration_path, 'r', encoding='utf-8') as f:
                    registration = yaml.safe_load(f)
                    return registration.get('keyword_research', {}).get('enabled', False)
            
            return False
            
        except Exception as e:
            st.warning(f"Error checking keyword research status for {brand_id}: {str(e)}")
            return False
    
    def get_keyword_researcher(self, brand_id: str) -> Optional[GoogleAdsKeywordResearch]:
        """Get or create keyword researcher for a brand"""
        if not GOOGLE_ADS_RESEARCH_AVAILABLE:
            st.warning("Google Ads keyword research not available")
            return None
            
        if brand_id not in self.keyword_researchers:
            try:
                self.keyword_researchers[brand_id] = GoogleAdsKeywordResearch(brand_id)
            except Exception as e:
                st.error(f"Could not initialize keyword researcher for {brand_id}: {str(e)}")
                return None
        
        return self.keyword_researchers[brand_id]
    
    def get_keywords_for_brand_theme(self, brand_id: str, theme: str, force_refresh: bool = False) -> List[Dict]:
        """Get keywords for a specific brand and theme"""
        researcher = self.get_keyword_researcher(brand_id)
        if not researcher:
            return []
        
        return researcher.get_keywords_for_theme(theme, force_refresh)
    
    def get_opportunities_for_brand_theme(self, brand_id: str, theme: str) -> List[Dict]:
        """Get keyword opportunities for a specific brand and theme"""
        researcher = self.get_keyword_researcher(brand_id)
        if not researcher:
            return []
        
        return researcher.get_keyword_opportunities(theme)
    
    def refresh_all_brand_caches(self):
        """Refresh keyword cache for all brands"""
        brands = self.get_available_brands()
        
        for brand_id in brands:
            try:
                researcher = self.get_keyword_researcher(brand_id)
                if researcher:
                    researcher.clear_cache()
                    st.info(f"🔄 Cache cleared for {brand_id}")
            except Exception as e:
                st.error(f"Error refreshing cache for {brand_id}: {str(e)}")
    
    def get_brand_config(self, brand_id: str) -> Dict:
        """Get brand configuration"""
        try:
            # Load .env file
            env_vars = {}
            env_path = Path(f"z_brands/{brand_id}/.env")
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            env_vars[key] = value
            
            # Load registration.yaml
            registration = {}
            registration_path = Path(f"z_brands/{brand_id}/registration.yaml")
            if registration_path.exists():
                with open(registration_path, 'r', encoding='utf-8') as f:
                    registration = yaml.safe_load(f)
            
            return {
                'env': env_vars,
                'registration': registration
            }
        except Exception as e:
            st.error(f"Error loading brand config for {brand_id}: {str(e)}")
            return {'env': {}, 'registration': {}}
    
    def update_brand_config(self, brand_id: str, config: Dict):
        """Update brand configuration"""
        try:
            # Update .env file
            env_vars = config.get('env', {})
            env_path = Path(f"z_brands/{brand_id}/.env")
            env_path.parent.mkdir(exist_ok=True)
            
            with open(env_path, 'w', encoding='utf-8') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            # Update registration.yaml
            registration = config.get('registration', {})
            registration_path = Path(f"z_brands/{brand_id}/registration.yaml")
            
            with open(registration_path, 'w', encoding='utf-8') as f:
                yaml.dump(registration, f, default_flow_style=False, allow_unicode=True)
            
            st.success(f"✅ Configuration updated for {brand_id}")
            
        except Exception as e:
            st.error(f"Error updating brand config for {brand_id}: {str(e)}")
    
    def test_brand_api_connection(self, brand_id: str) -> bool:
        """Test if the brand's API connection is working"""
        try:
            researcher = self.get_keyword_researcher(brand_id)
            if not researcher:
                return False
            
            # Try to get keywords for a test theme
            test_keywords = researcher.get_keywords_for_theme("test", force_refresh=True)
            return len(test_keywords) > 0
            
        except Exception as e:
            st.error(f"API connection test failed for {brand_id}: {str(e)}")
            return False
    
    def get_brand_status(self, brand_id: str) -> Dict:
        """Get comprehensive status for a brand"""
        status = {
            'brand_id': brand_id,
            'keyword_research_enabled': False,
            'api_configured': False,
            'api_working': False,
            'cache_exists': False,
            'last_update': None
        }
        
        try:
            # Check if keyword research is enabled
            status['keyword_research_enabled'] = self._is_keyword_research_enabled(brand_id)
            
            if status['keyword_research_enabled']:
                # Check if API is configured
                config = self.get_brand_config(brand_id)
                env_vars = config.get('env', {})
                
                required_vars = [
                    'GOOGLE_ADS_DEVELOPER_TOKEN',
                    'GOOGLE_ADS_CLIENT_ID',
                    'GOOGLE_ADS_CLIENT_SECRET',
                    'GOOGLE_ADS_REFRESH_TOKEN',
                    'GOOGLE_ADS_CUSTOMER_ID'
                ]
                
                status['api_configured'] = all(env_vars.get(var) for var in required_vars)
                
                # Check if API is working
                if status['api_configured']:
                    status['api_working'] = self.test_brand_api_connection(brand_id)
                
                # Check cache status
                cache_path = Path(f"z_brands/{brand_id}/cache/keywords_cache.json")
                status['cache_exists'] = cache_path.exists()
                
                if status['cache_exists']:
                    import json
                    import time
                    try:
                        cache_data = json.loads(cache_path.read_text())
                        if cache_data:
                            # Get the most recent timestamp
                            timestamps = [data.get('timestamp', 0) for data in cache_data.values()]
                            if timestamps:
                                latest_timestamp = max(timestamps)
                                status['last_update'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_timestamp))
                    except Exception:
                        pass
            
        except Exception as e:
            st.error(f"Error getting status for {brand_id}: {str(e)}")
        
        return status
    
    def get_all_brands_status(self) -> List[Dict]:
        """Get status for all brands"""
        brands = self.get_available_brands()
        statuses = []
        
        for brand_id in brands:
            status = self.get_brand_status(brand_id)
            statuses.append(status)
        
        return statuses
