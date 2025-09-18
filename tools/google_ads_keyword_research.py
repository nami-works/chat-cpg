import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import streamlit as st

# Try to import Google Ads client, but don't fail if not available
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_AVAILABLE = False
    st.warning("Google Ads API not available. Install with: pip install google-ads")

class GoogleAdsKeywordResearch:
    """Google Ads API integration for keyword research"""
    
    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.brand_env_path = Path(f"z_brands/{brand_id}/.env")
        self.client = None
        self.cache_path = Path(f"z_brands/{brand_id}/cache/keywords_cache.json")
        
        # Create cache directory
        self.cache_path.parent.mkdir(exist_ok=True)
        
        # Load brand configuration
        self.config = self._load_brand_config()
        
        # Initialize Google Ads client
        self._initialize_client()
    
    def _load_brand_config(self) -> Dict:
        """Load brand-specific configuration with security priority"""
        try:
            # Priority 1: Brand-specific .env file (most secure for multi-brand)
            env_vars = self._load_from_brand_env_file()
            
            # Priority 2: Environment variables (fallback)
            if not self._has_complete_credentials(env_vars):
                env_vars.update(self._load_from_environment_variables())
            
            # Priority 3: Secure config file (if exists)
            if not self._has_complete_credentials(env_vars):
                secure_creds = self._load_from_secure_config()
                env_vars.update(secure_creds)
            
            # Priority 4: Registration.yaml (least secure - only for non-sensitive config)
            registration_path = Path(f"z_brands/{self.brand_id}/registration.yaml")
            if registration_path.exists():
                import yaml
                with open(registration_path, 'r', encoding='utf-8') as f:
                    registration = yaml.safe_load(f)
            else:
                registration = {}
            
            # Extract non-sensitive config from registration.yaml
            if 'apis' in registration and 'google_ads' in registration['apis']:
                google_ads_config = registration['apis']['google_ads']
                env_vars.update({
                    'BRAND_COUNTRY': google_ads_config.get('country_code', 'BR'),
                    'BRAND_LANGUAGE': google_ads_config.get('language_code', 'pt')
                })
            
            # Load keyword research settings
            if 'keyword_research' in registration:
                keyword_config = registration['keyword_research']
                env_vars.update({
                    'KEYWORD_RESEARCH_ENABLED': str(keyword_config.get('enabled', True)).lower(),
                    'KEYWORD_CACHE_DURATION': str(keyword_config.get('cache_duration_hours', 24) * 3600),
                    'MAX_KEYWORDS_PER_THEME': str(keyword_config.get('max_keywords_per_theme', 50)),
                    'MIN_SEARCH_VOLUME': str(keyword_config.get('filters', {}).get('min_search_volume', 100)),
                    'MAX_SEARCH_VOLUME': str(keyword_config.get('filters', {}).get('max_search_volume', 100000)),
                    'SEO_DIFFICULTY_THRESHOLD': str(keyword_config.get('filters', {}).get('max_seo_difficulty', 30)),
                    'MIN_CPC': str(keyword_config.get('filters', {}).get('min_cpc', 0.1)),
                    'MAX_CPC': str(keyword_config.get('filters', {}).get('max_cpc', 10.0))
                })
            
            return {
                'env': env_vars,
                'registration': registration
            }
        except Exception as e:
            st.error(f"Error loading brand config for {self.brand_id}: {str(e)}")
            return {'env': {}, 'registration': {}}
    
    def _load_from_brand_env_file(self) -> Dict:
        """Load credentials from brand-specific .env file (most secure for multi-brand)"""
        env_vars = {}
        
        # Load from brand-specific .env file
        if self.brand_env_path.exists():
            try:
                with open(self.brand_env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')  # Remove quotes
                            
                            # Map .env keys to our internal format
                            if key in ['GOOGLE_ADS_DEVELOPER_TOKEN', 'DEVELOPER_TOKEN']:
                                env_vars['GOOGLE_ADS_DEVELOPER_TOKEN'] = value
                            elif key in ['GOOGLE_ADS_CLIENT_ID', 'CLIENT_ID']:
                                env_vars['GOOGLE_ADS_CLIENT_ID'] = value
                            elif key in ['GOOGLE_ADS_CLIENT_SECRET', 'CLIENT_SECRET']:
                                env_vars['GOOGLE_ADS_CLIENT_SECRET'] = value
                            elif key in ['GOOGLE_ADS_REFRESH_TOKEN', 'REFRESH_TOKEN']:
                                env_vars['GOOGLE_ADS_REFRESH_TOKEN'] = value
                            elif key in ['GOOGLE_ADS_CUSTOMER_ID', 'CUSTOMER_ID']:
                                env_vars['GOOGLE_ADS_CUSTOMER_ID'] = value
                            elif key in ['BRAND_COUNTRY', 'COUNTRY_CODE']:
                                env_vars['BRAND_COUNTRY'] = value
                            elif key in ['BRAND_LANGUAGE', 'LANGUAGE_CODE']:
                                env_vars['BRAND_LANGUAGE'] = value
                            
                st.info(f"📁 Loaded configuration from {self.brand_env_path}")
                
            except Exception as e:
                st.warning(f"Could not load .env file from {self.brand_env_path}: {str(e)}")
        
        return env_vars
    
    def _load_from_environment_variables(self) -> Dict:
        """Load credentials from environment variables (fallback)"""
        env_vars = {}
        
        # Check for brand-specific environment variables
        brand_prefix = f"{self.brand_id.upper()}_"
        
        # Brand-specific credentials
        env_vars.update({
            'GOOGLE_ADS_DEVELOPER_TOKEN': os.getenv(f"{brand_prefix}DEVELOPER_TOKEN") or os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            'GOOGLE_ADS_CLIENT_ID': os.getenv(f"{brand_prefix}CLIENT_ID") or os.getenv("GOOGLE_ADS_CLIENT_ID"),
            'GOOGLE_ADS_CLIENT_SECRET': os.getenv(f"{brand_prefix}CLIENT_SECRET") or os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            'GOOGLE_ADS_REFRESH_TOKEN': os.getenv(f"{brand_prefix}REFRESH_TOKEN") or os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            'GOOGLE_ADS_CUSTOMER_ID': os.getenv(f"{brand_prefix}CUSTOMER_ID") or os.getenv("GOOGLE_ADS_CUSTOMER_ID"),
        })
        
        return env_vars
    
    def _load_from_secure_config(self) -> Dict:
        """Load credentials from secure config file (outside repository)"""
        secure_configs = [
            Path("config/secure_credentials.yaml"),
            Path("config/credentials.yaml"),
            Path(f"z_brands/{self.brand_id}/credentials.yaml"),
            Path(f"z_brands/{self.brand_id}/secure.yaml")
        ]
        
        for config_path in secure_configs:
            if config_path.exists():
                try:
                    import yaml
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = yaml.safe_load(f)
                    
                    # Extract credentials for this brand
                    if 'brands' in config and self.brand_id in config['brands']:
                        brand_config = config['brands'][self.brand_id]
                        if 'google_ads' in brand_config:
                            google_ads_config = brand_config['google_ads']
                            return {
                                'GOOGLE_ADS_DEVELOPER_TOKEN': google_ads_config.get('developer_token', ''),
                                'GOOGLE_ADS_CLIENT_ID': google_ads_config.get('client_id', ''),
                                'GOOGLE_ADS_CLIENT_SECRET': google_ads_config.get('client_secret', ''),
                                'GOOGLE_ADS_REFRESH_TOKEN': google_ads_config.get('refresh_token', ''),
                                'GOOGLE_ADS_CUSTOMER_ID': google_ads_config.get('customer_id', ''),
                            }
                except Exception as e:
                    st.warning(f"Could not load secure config from {config_path}: {str(e)}")
                    continue
        
        return {}
    
    def _has_complete_credentials(self, env_vars: Dict) -> bool:
        """Check if we have all required credentials"""
        required_vars = [
            'GOOGLE_ADS_DEVELOPER_TOKEN',
            'GOOGLE_ADS_CLIENT_ID',
            'GOOGLE_ADS_CLIENT_SECRET',
            'GOOGLE_ADS_REFRESH_TOKEN',
            'GOOGLE_ADS_CUSTOMER_ID'
        ]
        
        return all(env_vars.get(var) for var in required_vars)
    
    def _initialize_client(self):
        """Initialize Google Ads API client"""
        if not GOOGLE_ADS_AVAILABLE:
            st.warning("Google Ads API not available. Install with: pip install google-ads")
            return
            
        try:
            env_vars = self.config['env']
            
            # Check if required credentials are available
            required_vars = [
                'GOOGLE_ADS_DEVELOPER_TOKEN',
                'GOOGLE_ADS_CLIENT_ID', 
                'GOOGLE_ADS_CLIENT_SECRET',
                'GOOGLE_ADS_REFRESH_TOKEN'
            ]
            
            missing_vars = [var for var in required_vars if not env_vars.get(var)]
            if missing_vars:
                st.warning(f"Missing Google Ads credentials for {self.brand_id}: {', '.join(missing_vars)}")
                return
            
            # Create temporary google-ads.yaml for this brand
            google_ads_config = {
                'developer_token': env_vars.get('GOOGLE_ADS_DEVELOPER_TOKEN'),
                'client_id': env_vars.get('GOOGLE_ADS_CLIENT_ID'),
                'client_secret': env_vars.get('GOOGLE_ADS_CLIENT_SECRET'),
                'refresh_token': env_vars.get('GOOGLE_ADS_REFRESH_TOKEN'),
                'use_proto_plus': True
            }
            
            # Save temporary config
            config_path = Path(f"z_brands/{self.brand_id}/google-ads.yaml")
            config_path.parent.mkdir(exist_ok=True)
            
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(google_ads_config, f)
            
            # Initialize client
            self.client = GoogleAdsClient.load_from_storage(str(config_path))
            
            # Clean up temporary config
            config_path.unlink()
            
            st.success(f"✅ Google Ads client initialized for {self.brand_id}")
            
        except Exception as e:
            st.warning(f"Could not initialize Google Ads client for {self.brand_id}: {str(e)}")
            self.client = None
    
    def get_keywords_for_theme(self, theme: str, force_refresh: bool = False) -> List[Dict]:
        """Get keywords for a specific theme"""
        
        # Check cache first
        if not force_refresh and self._is_cache_valid(theme):
            cached_keywords = self._load_from_cache(theme)
            if cached_keywords:
                st.info(f"📋 Using cached keywords for '{theme}' ({len(cached_keywords)} keywords)")
                return cached_keywords
        
        # Get keywords from Google Ads API
        keywords = self._fetch_from_google_ads(theme)
        
        # Cache results
        if keywords:
            self._save_to_cache(theme, keywords)
        
        return keywords
    
    def _fetch_from_google_ads(self, theme: str) -> List[Dict]:
        """Fetch keywords from Google Ads API"""
        if not self.client:
            st.error("Google Ads client not initialized")
            return []
        
        try:
            # Get configuration
            env_vars = self.config['env']
            customer_id = env_vars.get('GOOGLE_ADS_CUSTOMER_ID')
            country_code = env_vars.get('BRAND_COUNTRY', 'BR')
            
            if not customer_id:
                st.error("Google Ads customer ID not configured")
                return []
            
            # Create keyword plan
            keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")
            
            # Build request
            request = self.client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = customer_id
            request.language = f"languageConstants/{country_code.lower()}"
            request.geo_target_constants = [f"geoTargetConstants/{country_code}"]
            request.keyword_plan_network = self.client.get_type("KeywordPlanNetworkEnum").KeywordPlanNetwork.GOOGLE_SEARCH
            
            # Add keyword texts
            keyword_texts = self.client.get_type("KeywordText")
            keyword_texts.text = theme
            request.keyword_texts = [keyword_texts]
            
            # Generate keyword ideas
            response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
            
            # Process results
            keywords = []
            for result in response.results:
                keyword_data = {
                    'keyword': result.text,
                    'search_volume': result.keyword_idea_metrics.avg_monthly_searches,
                    'competition': result.keyword_idea_metrics.competition.name,
                    'low_top_of_page_bid_micros': result.keyword_idea_metrics.low_top_of_page_bid_micros / 1000000,
                    'high_top_of_page_bid_micros': result.keyword_idea_metrics.high_top_of_page_bid_micros / 1000000,
                    'competition_index': result.keyword_idea_metrics.competition_index,
                    'source': 'google_ads'
                }
                keywords.append(keyword_data)
            
            st.success(f"✅ Fetched {len(keywords)} keywords from Google Ads API")
            return keywords
            
        except GoogleAdsException as ex:
            st.error(f"Google Ads API error: {ex}")
            return []
        except Exception as e:
            st.error(f"Error fetching keywords: {str(e)}")
            return []
    
    def _is_cache_valid(self, theme: str) -> bool:
        """Check if cached data is still valid"""
        if not self.cache_path.exists():
            return False
        
        try:
            cache_data = json.loads(self.cache_path.read_text())
            theme_cache = cache_data.get(theme, {})
            
            # Check if cache exists and is not expired
            cache_time = theme_cache.get('timestamp', 0)
            cache_duration = int(self.config['env'].get('KEYWORD_CACHE_DURATION', 86400))
            
            return (time.time() - cache_time) < cache_duration
            
        except Exception:
            return False
    
    def _load_from_cache(self, theme: str) -> List[Dict]:
        """Load keywords from cache"""
        try:
            cache_data = json.loads(self.cache_path.read_text())
            return cache_data.get(theme, {}).get('keywords', [])
        except Exception:
            return []
    
    def _save_to_cache(self, theme: str, keywords: List[Dict]):
        """Save keywords to cache"""
        try:
            # Load existing cache
            cache_data = {}
            if self.cache_path.exists():
                cache_data = json.loads(self.cache_path.read_text())
            
            # Update cache
            cache_data[theme] = {
                'keywords': keywords,
                'timestamp': time.time(),
                'count': len(keywords)
            }
            
            # Save cache
            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            st.warning(f"Could not save to cache: {str(e)}")
    
    def get_keyword_opportunities(self, theme: str) -> List[Dict]:
        """Get high-value keyword opportunities"""
        keywords = self.get_keywords_for_theme(theme)
        
        # Apply filters from brand configuration
        env_vars = self.config['env']
        min_volume = int(env_vars.get('MIN_SEARCH_VOLUME', 100))
        max_difficulty = int(env_vars.get('SEO_DIFFICULTY_THRESHOLD', 30))
        min_cpc = float(env_vars.get('MIN_CPC', 0.1))
        
        opportunities = []
        for kw in keywords:
            # Calculate opportunity score
            volume = kw.get('search_volume', 0)
            cpc = kw.get('low_top_of_page_bid_micros', 0)
            competition = kw.get('competition_index', 100)
            
            # Apply filters
            if (volume >= min_volume and 
                competition <= max_difficulty and 
                cpc >= min_cpc):
                
                # Calculate opportunity score
                opportunity_score = (volume * cpc) / (competition + 1)
                
                kw['opportunity_score'] = opportunity_score
                opportunities.append(kw)
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return opportunities
    
    def clear_cache(self):
        """Clear all cached keywords"""
        try:
            if self.cache_path.exists():
                self.cache_path.unlink()
                st.success(f"✅ Cache cleared for {self.brand_id}")
        except Exception as e:
            st.error(f"Error clearing cache: {str(e)}")
