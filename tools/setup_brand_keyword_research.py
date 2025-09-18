import os
import yaml
from pathlib import Path
import streamlit as st

def setup_brand_keyword_research(brand_id: str):
    """Setup keyword research for a new brand"""
    
    brand_dir = Path(f"z_brands/{brand_id}")
    brand_dir.mkdir(exist_ok=True)
    
    # Create .env template
    env_template = f"""# Brand Configuration
BRAND_ID={brand_id}
BRAND_NAME="{brand_id.title()}"
BRAND_COUNTRY=BR
BRAND_LANGUAGE=pt_BR

# Google Ads API Configuration
GOOGLE_ADS_CLIENT_ID=your_client_id_here
GOOGLE_ADS_CLIENT_SECRET=your_client_secret_here
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_ADS_CUSTOMER_ID=your_customer_id_here

# Keyword Research Configuration
KEYWORD_RESEARCH_ENABLED=true
KEYWORD_CACHE_DURATION=86400
MAX_KEYWORDS_PER_THEME=50
MIN_SEARCH_VOLUME=100
MAX_SEARCH_VOLUME=100000

# SEO Configuration
SEO_DIFFICULTY_THRESHOLD=30
CPC_THRESHOLD=5.0
COMPETITION_THRESHOLD=0.7

# Content Generation Limits
MAX_CONTENT_LENGTH=2000
MIN_CONTENT_LENGTH=800
KEYWORD_DENSITY_TARGET=0.02

# API Rate Limits
GOOGLE_ADS_RATE_LIMIT=1000
KEYWORD_CACHE_ENABLED=true
"""
    
    env_path = brand_dir / ".env"
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    # Update registration.yaml
    registration_path = brand_dir / "registration.yaml"
    if registration_path.exists():
        with open(registration_path, 'r', encoding='utf-8') as f:
            registration = yaml.safe_load(f)
    else:
        registration = {}
    
    # Add API configuration
    registration['apis'] = {
        'google_ads': {
            'enabled': True,
            'customer_id': 'your_customer_id_here',
            'country_code': 'BR',
            'language_code': 'pt'
        }
    }
    
    registration['keyword_research'] = {
        'enabled': True,
        'primary_source': 'google_ads',
        'fallback_sources': ['google_trends', 'manual_csv'],
        'cache_duration_hours': 24,
        'max_keywords_per_theme': 50,
        'filters': {
            'min_search_volume': 100,
            'max_search_volume': 100000,
            'max_seo_difficulty': 30,
            'min_cpc': 0.1,
            'max_cpc': 10.0
        }
    }
    
    with open(registration_path, 'w', encoding='utf-8') as f:
        yaml.dump(registration, f, default_flow_style=False, allow_unicode=True)
    
    # Create cache directory
    cache_dir = brand_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    st.success(f"✅ Brand keyword research setup complete for {brand_id}")
    st.info(f"📝 Please configure Google Ads API credentials in: z_brands/{brand_id}/.env")

def setup_existing_brand_keyword_research(brand_id: str):
    """Setup keyword research for an existing brand without overwriting existing config"""
    
    brand_dir = Path(f"z_brands/{brand_id}")
    if not brand_dir.exists():
        st.error(f"Brand directory not found: {brand_dir}")
        return
    
    # Check if .env already exists
    env_path = brand_dir / ".env"
    if env_path.exists():
        st.warning(f"Environment file already exists for {brand_id}")
        st.info("Skipping .env creation to preserve existing configuration")
    else:
        # Create .env template
        env_template = f"""# Brand Configuration
BRAND_ID={brand_id}
BRAND_NAME="{brand_id.title()}"
BRAND_COUNTRY=BR
BRAND_LANGUAGE=pt_BR

# Google Ads API Configuration
GOOGLE_ADS_CLIENT_ID=your_client_id_here
GOOGLE_ADS_CLIENT_SECRET=your_client_secret_here
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token_here
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token_here
GOOGLE_ADS_CUSTOMER_ID=your_customer_id_here

# Keyword Research Configuration
KEYWORD_RESEARCH_ENABLED=true
KEYWORD_CACHE_DURATION=86400
MAX_KEYWORDS_PER_THEME=50
MIN_SEARCH_VOLUME=100
MAX_SEARCH_VOLUME=100000

# SEO Configuration
SEO_DIFFICULTY_THRESHOLD=30
CPC_THRESHOLD=5.0
COMPETITION_THRESHOLD=0.7
"""
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_template)
        st.success(f"✅ Created .env file for {brand_id}")
    
    # Update registration.yaml
    registration_path = brand_dir / "registration.yaml"
    if registration_path.exists():
        with open(registration_path, 'r', encoding='utf-8') as f:
            registration = yaml.safe_load(f)
    else:
        registration = {}
    
    # Add API configuration if not exists
    if 'apis' not in registration:
        registration['apis'] = {
            'google_ads': {
                'enabled': True,
                'customer_id': 'your_customer_id_here',
                'country_code': 'BR',
                'language_code': 'pt'
            }
        }
        st.success(f"✅ Added API configuration to registration.yaml for {brand_id}")
    
    # Add keyword research configuration if not exists
    if 'keyword_research' not in registration:
        registration['keyword_research'] = {
            'enabled': True,
            'primary_source': 'google_ads',
            'fallback_sources': ['google_trends', 'manual_csv'],
            'cache_duration_hours': 24,
            'max_keywords_per_theme': 50,
            'filters': {
                'min_search_volume': 100,
                'max_search_volume': 100000,
                'max_seo_difficulty': 30,
                'min_cpc': 0.1,
                'max_cpc': 10.0
            }
        }
        st.success(f"✅ Added keyword research configuration to registration.yaml for {brand_id}")
    
    # Save updated registration.yaml
    with open(registration_path, 'w', encoding='utf-8') as f:
        yaml.dump(registration, f, default_flow_style=False, allow_unicode=True)
    
    # Create cache directory
    cache_dir = brand_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    st.success(f"✅ Brand keyword research setup complete for {brand_id}")
    st.info(f"📝 Please configure Google Ads API credentials in: z_brands/{brand_id}/.env")

def setup_all_brands_keyword_research():
    """Setup keyword research for all existing brands"""
    
    brands_dir = Path("z_brands")
    if not brands_dir.exists():
        st.error("z_brands directory not found")
        return
    
    brands = [brand_dir.name for brand_dir in brands_dir.iterdir() if brand_dir.is_dir()]
    
    if not brands:
        st.warning("No brands found in z_brands directory")
        return
    
    st.info(f"Found {len(brands)} brands: {', '.join(brands)}")
    
    for brand_id in brands:
        st.markdown(f"### Setting up {brand_id}")
        setup_existing_brand_keyword_research(brand_id)
        st.markdown("---")
    
    st.success(f"✅ Keyword research setup complete for all {len(brands)} brands")

def get_google_ads_setup_instructions():
    """Get instructions for setting up Google Ads API"""
    
    instructions = """
## 🔧 Google Ads API Setup Instructions

### Step 1: Create Google Ads API Account
1. Go to [Google Ads API Center](https://developers.google.com/google-ads/api/docs/first-call/dev-token)
2. Sign in with your Google account
3. Create a new application
4. Get your Developer Token

### Step 2: Create OAuth 2.0 Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Ads API
4. Create OAuth 2.0 credentials
5. Get Client ID and Client Secret

### Step 3: Generate Refresh Token
1. Use the OAuth 2.0 Playground: https://developers.google.com/oauthplayground/
2. Set up OAuth 2.0 configuration
3. Authorize your application
4. Exchange authorization code for refresh token

### Step 4: Get Customer ID
1. Log into your Google Ads account
2. Go to Tools & Settings > Setup > Account access
3. Copy your Customer ID (format: XXX-XXX-XXXX)

### Step 5: Configure Brand Environment
1. Edit the `.env` file in your brand directory
2. Replace placeholder values with your actual credentials:
   ```
   GOOGLE_ADS_CLIENT_ID=your_actual_client_id
   GOOGLE_ADS_CLIENT_SECRET=your_actual_client_secret
   GOOGLE_ADS_DEVELOPER_TOKEN=your_actual_developer_token
   GOOGLE_ADS_REFRESH_TOKEN=your_actual_refresh_token
   GOOGLE_ADS_CUSTOMER_ID=your_actual_customer_id
   ```

### Step 6: Test Connection
1. Run the brand status check
2. Verify API connection is working
3. Test keyword research functionality

## 📚 Additional Resources
- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [OAuth 2.0 Setup Guide](https://developers.google.com/google-ads/api/docs/oauth/overview)
- [Keyword Planner API Guide](https://developers.google.com/google-ads/api/docs/keyword-planning/overview)
"""
    
    return instructions

def main():
    """Main function for brand setup"""
    
    st.title("🔧 Brand Keyword Research Setup")
    
    # Check if tools directory exists
    tools_dir = Path("tools")
    if not tools_dir.exists():
        st.error("Tools directory not found. Please run this from the project root.")
        return
    
    # Get available brands
    brands_dir = Path("z_brands")
    if brands_dir.exists():
        brands = [brand_dir.name for brand_dir in brands_dir.iterdir() if brand_dir.is_dir()]
    else:
        brands = []
    
    st.markdown("### Setup Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Setup New Brand", use_container_width=True):
            brand_id = st.text_input("Enter brand ID (e.g., mybrand):")
            if brand_id:
                setup_brand_keyword_research(brand_id)
    
    with col2:
        if st.button("Setup All Existing Brands", use_container_width=True):
            if brands:
                setup_all_brands_keyword_research()
            else:
                st.warning("No brands found in z_brands directory")
    
    if brands:
        st.markdown("### Setup Specific Brand")
        selected_brand = st.selectbox("Select brand to setup:", brands)
        if st.button(f"Setup {selected_brand}"):
            setup_existing_brand_keyword_research(selected_brand)
    
    st.markdown("### Setup Instructions")
    with st.expander("Google Ads API Setup Instructions", expanded=False):
        st.markdown(get_google_ads_setup_instructions())

if __name__ == "__main__":
    main()
