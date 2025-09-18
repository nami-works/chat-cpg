#!/usr/bin/env python3
"""
Brand Environment Files Setup Script

This script helps you set up .env files for each brand with Google Ads API credentials.
"""

import os
import shutil
from pathlib import Path
import streamlit as st

def setup_brand_env_files():
    """Setup .env files for all brands"""
    
    st.title("🔐 Brand Environment Files Setup")
    st.write("This tool helps you set up secure .env files for each brand.")
    
    # Get available brands
    brands_dir = Path("z_brands")
    available_brands = [d.name for d in brands_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    st.write(f"Found {len(available_brands)} brands: {', '.join(available_brands)}")
    
    # Setup each brand
    for brand_id in available_brands:
        st.subheader(f"🏷️  {brand_id.upper()}")
        
        brand_dir = brands_dir / brand_id
        env_example = brand_dir / "env.example"
        env_file = brand_dir / ".env"
        
        if env_example.exists():
            if env_file.exists():
                st.success(f"✅ {brand_id}: .env file already exists")
                
                # Show current configuration
                with open(env_file, 'r') as f:
                    current_config = f.read()
                
                with st.expander(f"Current {brand_id} .env configuration"):
                    st.code(current_config, language="bash")
                    
            else:
                st.info(f"📝 {brand_id}: env.example found, .env file needs to be created")
                
                # Show template
                with open(env_example, 'r') as f:
                    template = f.read()
                
                with st.expander(f"{brand_id} env.example template"):
                    st.code(template, language="bash")
                
                # Instructions
                st.write(f"""
                **To complete setup for {brand_id}:**
                1. Copy the template above
                2. Create a new file: `z_brands/{brand_id}/.env`
                3. Paste the template and fill in your actual Google Ads API credentials
                4. Save the file
                """)
                
                # Manual setup button
                if st.button(f"Create {brand_id} .env file manually"):
                    st.info(f"Please create `z_brands/{brand_id}/.env` manually with your credentials")
        else:
            st.warning(f"⚠️  {brand_id}: env.example not found")
    
    # Security reminders
    st.subheader("🔒 Security Reminders")
    st.write("""
    - **NEVER commit .env files to version control**
    - Add `.env` to your `.gitignore` file
    - Keep your API credentials secure
    - Rotate credentials regularly
    - Use different credentials for each brand if possible
    """)
    
    # .gitignore check
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
        
        if ".env" in gitignore_content:
            st.success("✅ .env files are properly excluded in .gitignore")
        else:
            st.warning("⚠️  .env files are NOT excluded in .gitignore")
            st.write("Add these lines to your .gitignore file:")
            st.code("""
# Environment files
.env
**/.env
*.env
            """, language="gitignore")
    else:
        st.warning("⚠️  .gitignore file not found")
        st.write("Create a .gitignore file with these entries:")
        st.code("""
# Environment files
.env
**/.env
*.env
        """, language="gitignore")

def create_env_file_for_brand(brand_id: str, credentials: dict):
    """Create .env file for a specific brand"""
    
    brand_dir = Path(f"z_brands/{brand_id}")
    env_file = brand_dir / ".env"
    
    # Create .env content
    env_content = f"""# {brand_id.upper()} - Google Ads API Configuration
# 
# ⚠️  SECURITY WARNING: This file contains sensitive API credentials
# 
# 1. NEVER commit this file to version control
# 2. Add .env to .gitignore
# 3. Keep credentials secure

# Google Ads API Credentials
DEVELOPER_TOKEN={credentials.get('developer_token', 'your_developer_token_here')}
CLIENT_ID={credentials.get('client_id', 'your_client_id_here')}
CLIENT_SECRET={credentials.get('client_secret', 'your_client_secret_here')}
REFRESH_TOKEN={credentials.get('refresh_token', 'your_refresh_token_here')}
CUSTOMER_ID={credentials.get('customer_id', 'your_customer_id_here')}

# Brand Configuration
BRAND_COUNTRY={credentials.get('country_code', 'BR')}
BRAND_LANGUAGE={credentials.get('language_code', 'pt')}

# Optional: Override default settings
# KEYWORD_CACHE_DURATION=86400
# MAX_KEYWORDS_PER_THEME=50
# MIN_SEARCH_VOLUME=100
# MAX_SEARCH_VOLUME=100000
# MAX_SEO_DIFFICULTY=30
# MIN_CPC=0.1
# MAX_CPC=10.0
"""
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        st.success(f"✅ Created .env file for {brand_id}")
        return True
        
    except Exception as e:
        st.error(f"❌ Error creating .env file for {brand_id}: {str(e)}")
        return False

if __name__ == "__main__":
    setup_brand_env_files()
