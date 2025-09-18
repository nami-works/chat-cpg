#!/usr/bin/env python
import os
import shutil
import smtplib
import sys
import warnings
import zipfile
import streamlit as st
import re

from chats.seo_lab.src.copywriter_crew.crew import SEOLab_CPG
from datetime import date, datetime
from dotenv import load_dotenv
from email.message import EmailMessage
from pathlib import Path
from translations import LANG

# Enhanced keywords system - no longer using pandas for CSV-based keywords

load_dotenv()

# Legacy CSV-based keyword functions removed - now using enhanced keywords.py dictionary system

def load_brief_summary_from_file(posts_folder):
    """
    Load brief_summary from the generated brief_summary.py file.
    
    Args:
        posts_folder: Path to the posts folder
        
    Returns:
        dict: Brief summary dictionary or empty dict if file doesn't exist
    """
    try:
        brief_summary_file = posts_folder / 'brief_summary.py'
        if brief_summary_file.exists():
            # Execute the file to get the brief_summary variable
            local_vars = {}
            exec(brief_summary_file.read_text(), {}, local_vars)
            return local_vars.get('brief_summary', {})
        else:
            return {}
    except Exception as e:
        print(f"⚠️ Could not load brief_summary.py: {e}")
        return {}

def load_keywords_from_file(posts_folder):
    """
    Load keywords dictionary from the generated keywords.py file.
    
    Args:
        posts_folder: Path to the posts folder
        
    Returns:
        dict: Keywords dictionary with SerpApi-enhanced data or empty dict if file doesn't exist
    """
    try:
        keywords_file = posts_folder / 'keywords.py'
        if keywords_file.exists():
            # Execute the file to get the keywords variable
            local_vars = {}
            exec(keywords_file.read_text(), {}, local_vars)
            keywords_dict = local_vars.get('keywords', {})
            st.info(f"✅ Loaded keywords dictionary with {len(keywords_dict)} theme entries")
            return keywords_dict
        else:
            st.warning("No keywords.py file found - using fallback keyword system")
            return {}
    except Exception as e:
        st.warning(f"Could not load keywords.py: {e}")
        return {}

# Environment variables
email_from = os.getenv("EMAIL_USER")
email_from_name = os.getenv("EMAIL_FROM_NAME")
email_password = os.getenv("EMAIL_PASS")

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

base_dir = Path(__file__).resolve().parent

def sanitize_filename(filename):
    """
    Sanitize filename by removing invalid characters.
    Windows doesn't allow: < > : " | ? * \\ /
    """
    # Remove invalid characters completely
    invalid_chars = r'[<>:"|?*\\\/]'
    sanitized = re.sub(invalid_chars, '', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = 'untitled'
    
    # Limit length to avoid path too long errors
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized

def send_email(recipient, subject, body, attachments=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f'{email_from_name} <{email_from}'
    msg['To'] = recipient
    msg.set_content(body)

    # Optional attachments
    if attachments:
        for file in attachments:
            path = Path(file)
            msg.add_attachment(path.read_bytes(), maintype='application', subtype='octet-stream', filename=path.name)

    # Authentication
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_from, email_password)  # Use app password, not your regular password
        smtp.send_message(msg)

def run(inputs):
    """
    Run the crew with inputs from the frontend.
    """
    
    themes = inputs['themes']
    voice = inputs['voice']
    brand = inputs['brand']
    products = inputs['products']
    blog = inputs['blog']
    benchmarks = inputs['benchmarks']
    format_recommendations = inputs['format_recommendations']
    semantic_fields = inputs['semantic_fields']
    brand_folder = inputs['brand_folder']
    macro_name = inputs.get('macro_name')
    if not macro_name:
        macro_name = datetime.now().strftime("%H_%M")

    # Keywords are now loaded from the enhanced keywords.py dictionary
    # The old CSV-based prioritized keywords system has been replaced

    # Handle selected products filtering
    selected_products = st.session_state.get('selected_products', [])
    if selected_products:
        try:
            from chats.seo_lab._seo_lab import get_products_context, load_products_from_yaml
            # Get brand_id from context - warn if not defined
            context = st.session_state.get('context', {})
            brand_id = context.get('brand_id')
            
            if not brand_id:
                st.error(f"⚠️ {LANG['brand_id_missing']}")
                return
            
            filtered_products = get_products_context(selected_products, brand_id=brand_id)
            if filtered_products:
                products = filtered_products
                all_products = load_products_from_yaml(brand_id)
                selected_names = [all_products[pid]['display_name'] for pid in selected_products if pid in all_products]
                st.info(f"🎯 Generating content focused on: {', '.join(selected_names)}")
                inputs['selected_products'] = selected_products
                inputs['selected_product_names'] = selected_names
        except Exception as e:
            st.warning(f"Could not apply product filtering in crew: {str(e)}")

    # Setup final save path
    today = date.today().isoformat()
    posts_folder = base_dir / brand_folder / 'posts'
    save_path = posts_folder / f'{today}_{macro_name}'
    os.makedirs(save_path, exist_ok=True)
    
    # Load brief_summary from generated file
    brief_summary_dict = load_brief_summary_from_file(posts_folder)
    
    # Load keywords dictionary with SerpApi-enhanced data
    keywords_dict = load_keywords_from_file(posts_folder)
    
    # Load products dictionary for optimized context
    products_dict = {}
    products_file = posts_folder / 'products.py'
    if products_file.exists():
        try:
            local_vars = {}
            exec(products_file.read_text(), {}, local_vars)
            products_dict = local_vars.get('products', {})
            st.info(f"✅ Loaded products dictionary with {len(products_dict)} theme mappings")
        except Exception as e:
            st.warning(f"Could not load products dictionary: {str(e)}")
    
    # Load editorial guidelines from simple markdown file
    editorials_content = ""
    editorials_file = base_dir / brand_folder / 'editorials.md'
    if editorials_file.exists():
        try:
            editorials_content = editorials_file.read_text(encoding='utf-8')
            st.info(f"✅ Loaded editorial guidelines from editorials.md")
        except Exception as e:
            st.warning(f"Could not load editorials.md: {str(e)}")
    
    # Get brand_id from context for theme processing
    context = st.session_state.get('context', {})
    brand_id = context.get('brand_id')
    if not brand_id:
        st.warning("⚠️ Brand ID not found in context - some features may not work properly")
    else:
        st.info("📝 No editorials.md found - using default content structure")
    
    # Track generated content
    generated_content = []
    
    st.markdown(f"### 📊 Content Generation")
    st.markdown(f"**Generating content for {len(themes)} themes**")
    
    # Add progress tracking
    theme_count = len(themes)
    processed_count = 0
    
    # Process each theme
    for theme_name, theme in themes.items():
        processed_count += 1
        st.markdown(f"---")
        st.markdown(f"### 🎯 Processing Theme {processed_count}/{theme_count}: {theme_name}")
        
        st.info(f"🔄 Generating content for theme: {theme_name} ({processed_count}/{theme_count})")
        
        # Extract keywords for this theme - prioritize SerpApi-enhanced data
        theme_keywords = []
        theme_keywords_data = {}
        
        # First, try to use keywords from keywords.py
        if keywords_dict and theme_name in keywords_dict:
            theme_keywords_data = keywords_dict[theme_name]
            if theme_keywords_data:
                # Check if theme_keywords_data is a list (simple format) or dict (enhanced format)
                if isinstance(theme_keywords_data, list):
                    # Simple list format - use directly
                    theme_keywords = theme_keywords_data
                    st.info(f"🎯 Using simple keywords list for theme '{theme_name}':")
                    st.info(f"   - Total: {len(theme_keywords)} keywords")
                elif isinstance(theme_keywords_data, dict):
                    # Enhanced dictionary format with SerpApi data
                    primary_keywords = theme_keywords_data.get('primary_keywords', [])
                    long_tail_keywords = theme_keywords_data.get('long_tail_keywords', [])
                    related_searches = theme_keywords_data.get('related_searches', [])
                    
                    # Combine all keyword types
                    theme_keywords = primary_keywords + long_tail_keywords + related_searches
                    
                    st.info(f"🎯 Using SerpApi-enhanced keywords for theme '{theme_name}':")
                    st.info(f"   - Primary: {len(primary_keywords)} keywords")
                    st.info(f"   - Long-tail: {len(long_tail_keywords)} keywords")
                    st.info(f"   - Related: {len(related_searches)} keywords")
                    st.info(f"   - Total: {len(theme_keywords)} keywords")
                    
                    # Show search volume data if available
                    search_volume = theme_keywords_data.get('search_volume', {})
                    if search_volume:
                        st.info(f"   - Search volume data available for {len(search_volume)} keywords")
                    
                    # Show competition level
                    competition_level = theme_keywords_data.get('competition_level', 'unknown')
                    st.info(f"   - Competition level: {competition_level}")
                else:
                    st.warning(f"⚠️ Unexpected keywords data format for theme '{theme_name}': {type(theme_keywords_data)}")
            else:
                st.info(f"📝 No keywords data found for theme: {theme_name}")
        else:
            st.info(f"📝 No keywords dictionary found for theme: {theme_name}")
        
        # No fallback needed - keywords.py dictionary is the primary source
        if not theme_keywords:
            st.info(f"📝 No keyword data available for theme: {theme}")
        
        # Get optimized products context for this specific theme
        theme_products = ""
        if products_dict and theme_name in products_dict:
            try:
                from chats.seo_lab._seo_lab import get_optimized_products_context
                theme_products = get_optimized_products_context(theme_name, products_dict, brand_id=brand_id)
                if theme_products:
                    st.info(f"🎯 Using optimized product context for theme: {theme_name}")
                else:
                    st.info(f"📝 No specific products found for theme: {theme_name}")
            except Exception as e:
                st.warning(f"Could not get optimized products for theme: {str(e)}")
        
        # Build theme inputs with all required variables
        theme_inputs = {
            'voice': voice,
            'brand': brand,
            'name': theme_name,
            'theme': theme,
            'products': theme_products or products,  # Use optimized context if available, fallback to full context
            'blog': blog,
            'benchmarks': benchmarks,
            'format_recommendations': format_recommendations,
            'semantic_fields': semantic_fields,
            'theme_keywords': theme_keywords,
            'keyword_opportunities': theme_keywords[:5] if theme_keywords else [],
            'preferred_language': inputs.get('preferred_language', 'pt_BR'),
            'brief_summary': brief_summary_dict.get(theme_name, f'Brief summary for theme: {theme}'),  # Use loaded brief_summary
            'theme_products': products_dict.get(theme_name, []) if products_dict else [],  # Add theme-specific products
            # Enhanced keywords data from SerpApi (only if it's a dict)
            'theme_keywords_data': theme_keywords_data if isinstance(theme_keywords_data, dict) else {},
            'primary_keywords': theme_keywords_data.get('primary_keywords', []) if isinstance(theme_keywords_data, dict) else [],
            'long_tail_keywords': theme_keywords_data.get('long_tail_keywords', []) if isinstance(theme_keywords_data, dict) else [],
            'related_searches': theme_keywords_data.get('related_searches', []) if isinstance(theme_keywords_data, dict) else [],
            'search_volume': theme_keywords_data.get('search_volume', {}) if isinstance(theme_keywords_data, dict) else {},
            'competition_level': theme_keywords_data.get('competition_level', 'unknown') if isinstance(theme_keywords_data, dict) else 'unknown'
        }
        
        # Inject simple editorial guidelines
        if editorials_content:
            theme_inputs['editorial_guidelines'] = editorials_content
            st.info(f"🎨 Using editorial guidelines from editorials.md")
        else:
            st.info(f"📝 Using default editorial structure for theme: {theme_name}")
        
        # Debug: Print available variables
        st.info(f"🔍 Available variables for theme '{theme_name}': {list(theme_inputs.keys())}")
        
        # Validate required variables
        required_vars = ['voice', 'brand', 'theme', 'products', 'blog', 'benchmarks', 'format_recommendations', 'semantic_fields', 'brief_summary']
        missing_vars = [var for var in required_vars if not theme_inputs.get(var)]
        if missing_vars:
            error_msg = f"❌ CRITICAL ERROR: Missing required variables for theme '{theme_name}': {missing_vars}"
            st.error(error_msg)
            st.error("Content generation cannot proceed without these variables.")
            st.error("Please check your brand setup and ensure all required data is loaded.")
            st.error("Stopping content generation for this theme.")
            continue  # Skip this theme and continue with next one
        
        # Additional validation: Check for empty strings or generic values
        generic_values = ['', 'Selected Brand', 'Available products', 'Brand blog content', 'Leading brands in the category', 'HTML format with proper structure', 'Relevant industry terms']
        problematic_vars = []
        
        for var in required_vars:
            value = theme_inputs.get(var, '')
            if value in generic_values:
                problematic_vars.append(f"{var}='{value}'")
        
        if problematic_vars:
            error_msg = f"❌ CRITICAL ERROR: Theme '{theme_name}' contains generic/empty values: {', '.join(problematic_vars)}"
            st.error(error_msg)
            st.error("Content generation cannot proceed with generic placeholder data.")
            st.error("Please ensure all context fields contain meaningful brand-specific information.")
            st.error("Stopping content generation for this theme.")
            continue  # Skip this theme and continue with next one
        
        # Initialize context chunker
        try:
            seo_lab_cpg = SEOLab_CPG(brand_folder)
            seo_lab_cpg.initialize_context_chunker(theme_inputs)
            st.info(f"✅ Context chunking initialized for theme: {theme}")
        except Exception as e:
            st.warning(f"⚠️ Could not initialize context chunking: {str(e)}")
        
        # Generate content
        try:
            seo_lab_cpg.crew().kickoff(inputs=theme_inputs)
            
            # Get file paths
            content_file = posts_folder / 'content.html'
            metafields_file = posts_folder / 'metafields.md'
            
            # Save content directly to final folder
            safe_filename = sanitize_filename(theme_name)
            final_content_path = save_path / f'{safe_filename}.html'
            final_metafields_path = save_path / f'{safe_filename}_metafields.md'
            
            shutil.copy(content_file, final_content_path)
            shutil.copy(metafields_file, final_metafields_path)
            
            generated_content.append({
                'name': theme_name,
                'content_path': final_content_path,
                'metafields_path': final_metafields_path
            })
            
            st.success(f"✅ Content generated for theme: {theme_name}")
            
        except Exception as e:
            st.error(f"❌ Error processing theme '{theme_name}': {str(e)}")
            continue
        

    
    # All themes processed - show final summary based on actual results
    if generated_content:
        st.markdown("### 🎉 Content Generation Complete!")
        st.success(f"✅ Successfully generated {len(generated_content)} content pieces:")
        
        for content in generated_content:
            st.markdown(f"- **{content['name']}**: {content['content_path'].name}")
        
        # Create zip file of generated content
        zip_path = save_path.with_suffix('.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in save_path.glob('*'):
                zipf.write(file, file.name)
        
        # Create download link
        st.markdown(f"### 📥 Download Content")
        with open(zip_path, 'rb') as f:
            st.download_button(
                label="Download generated content",
                data=f,
                file_name=f"{macro_name}.zip",
                mime="application/zip"
            )
    else:
        st.markdown("### ❌ Content Generation Failed")
        st.error("⚠️ No content was generated. Please check the error messages above and try again.")
    
    # Cleanup temporary files
    try:
        print(f"Content saved in: {save_path}")
    except FileNotFoundError:
        pass  # Files may not exist if validation was interrupted

def train(inputs):
    """
    Train the crew for a given number of iterations.
    """
    voice = inputs['voice']
    brand = inputs['brand']
    products = inputs['products']
    blog = inputs['blog']
    benchmarks = inputs['benchmarks']
    train_inputs = {
        'voice': voice,
        'brand': brand,
        'theme': 'Train with any theme of your choice',
        'products': products,
        'blog': blog,
        'benchmarks': benchmarks,
    }
    try:
        SEOLab_CPG().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=train_inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SEOLab_CPG().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test(inputs):
    """
    Test the crew execution and returns the results.
    """
    voice = inputs['voice']
    brand = inputs['brand']
    products = inputs['products']
    blog = inputs['blog']
    benchmarks = inputs['benchmarks']
    test_inputs = {
        'voice': voice,
        'brand': brand,
        'theme': 'Test with any theme of your choice',
        'products': products,
        'blog': blog,
        'benchmarks': benchmarks,
    }
    try:
        SEOLab_CPG().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=test_inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def write(inputs):
    run(inputs)
