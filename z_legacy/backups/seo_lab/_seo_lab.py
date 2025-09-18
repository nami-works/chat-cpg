#imports

##complete modules
import os
import locale
import yaml
import sys
import re
import ast
from pathlib import Path
from datetime import datetime

##renamed modules
import streamlit as st

##module functions
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

#internal Nami functions
from chats.seo_lab.utils import parse_creative_outputs, save_creative_outputs, load_local_creative_outputs
from chats.seo_lab.context import SEO_LAB_CONTEXT
# Enhanced keywords system - using keywords.py dictionary instead of CSV files

# Get the absolute path to the project root (current working directory)
base_dir = Path.cwd()

# Add the project root to Python path
if str(base_dir) not in sys.path:
    sys.path.append(str(base_dir))

# Tools import


load_dotenv()

# Import centralized translations
from translations import LANG

def track_user_interaction():
    """
    Track user interactions for the SEO lab flow.
    Increments the interaction counter in session state.
    """
    if 'seo_lab_interaction_count' not in st.session_state:
        st.session_state['seo_lab_interaction_count'] = 0
    
    st.session_state['seo_lab_interaction_count'] += 1

def get_interaction_count():
    """
    Get the current interaction count for the SEO lab flow.
    
    Returns:
        int: Current interaction count
    """
    return st.session_state.get('seo_lab_interaction_count', 0)

def get_selected_brand_id():
    """
    Get the currently selected brand ID from session state.
    
    Returns:
        str: The selected brand ID, or None if not set
    """
    context = st.session_state.get('context', {})
    return context.get('brand_id')

def load_products_from_yaml(brand_id=None):
    """
    Load all product information from YAML files in the products directory.
    
    Args:
        brand_id: Brand identifier (if None, uses selected brand from session state)
        
    Returns:
        dict: Dictionary of products with product_id as key and product data as value
    """
    # Use selected brand if not provided
    if brand_id is None:
        brand_id = get_selected_brand_id()
        if not brand_id:
            st.error(LANG.get('no_brand_selected', 'No brand selected. Please select a brand from the sidebar.'))
            return {}
    try:
        products_dir = base_dir / 'z_brands' / brand_id / 'products'
        products = {}
        
        if not products_dir.exists():
            st.warning(LANG.get('products_directory_not_found', 'Products directory not found: {}').format(products_dir))
            return {}
        
        # Load all YAML files in the products directory
        for yaml_file in products_dir.glob('*.yaml'):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    # Skip the ```yaml wrapper if present
                    content = f.read()
                    if content.startswith('```yaml'):
                        content = content.replace('```yaml', '').replace('```', '').strip()
                    
                    product_data = yaml.safe_load(content)
                    
                    if product_data and 'meta' in product_data:
                        product_id = product_data['meta'].get('product_id')
                        display_name = product_data['meta'].get('display_name')
                        
                        if product_id and display_name:
                            products[product_id] = {
                                'display_name': display_name,
                                'data': product_data,
                                'file': yaml_file.name
                            }
                        
            except Exception as e:
                st.warning(LANG.get('error_loading_product', 'Error loading product from {}: {}').format(yaml_file.name, str(e)))
                continue
                
        return products
        
    except Exception as e:
        st.error(LANG.get('error_loading_products', 'Error loading products: {}').format(str(e)))
        return {}

def seo_lab_sidebar():
    """
    Render SEO lab specific sidebar content.
    This function is called from _nami.py when seo_lab is selected.
    """
    
    # Get brand context from session state (set in setup tab)
    context = st.session_state.get('context', {})
    brand_id = context.get('brand_id')
    
    # If no brand is selected, show warning
    if not brand_id:
        st.warning(f"⚠️ {LANG['brand_id_missing']}")
        st.info(LANG.get('select_brand_setup_first', 'Please select a brand in the Setup tab first.'))
        return []
    
    # Import available brands for validation
    from brands_config import client_brands
    available_brands = client_brands
    
    # Validate brand_id is in available brands
    if brand_id not in available_brands.values():
        st.error(f"⚠️ {LANG['brand_id_invalid'].format(brand_id)}")
        return []
    
    # Show current brand selection
    selected_brand_name = st.session_state.get('selected_brand', 'Unknown')
    st.info(f"{LANG['brand_selection_confirmed'].format(selected_brand_name)}")
    
    # Load available products
    available_products = load_products_from_yaml(brand_id)
    
    if not available_products:
        st.warning(LANG['no_products_found'])
        return []
    
    # Create display options (product_id -> display_name mapping)
    product_options = {
        product_id: product_info['display_name'] 
        for product_id, product_info in available_products.items()
    }
    
    # Product multi-selector
    st.markdown(f"#### {LANG['product_selector_title']}")
    
    # Checkbox to include all products (set to True by default)
    include_all_products = st.checkbox(
        LANG['include_all_products'],
        value=st.session_state.get('include_all_products', True),
        help=LANG['include_all_products_help']
    )
    
    # Get current selection from session state
    current_selection = st.session_state.get('selected_products', [])
    
    # Ensure current selection items still exist in available products
    valid_selection = sorted([p for p in current_selection if p in product_options], 
                           key=lambda x: product_options[x].lower())
    
    # Only show multiselect if include_all_products is False
    selected_product_ids = []
    if not include_all_products:
        # Sort by the display name (A–Z), case-insensitive
        sorted_option_ids = sorted(product_options.keys(), key=lambda pid: product_options.get(pid, pid).casefold())
        
        selected_product_ids = st.multiselect(
            LANG['select_products'],
            options=sorted_option_ids,
            default=valid_selection,
            format_func=lambda x: product_options.get(x, x),
            placeholder=LANG['select_products_placeholder'],
            help=LANG['select_products_help']
        )
    
        # Store both selections in session state (but don't inject yet)
        st.session_state['pending_selected_products'] = selected_product_ids
        st.session_state['pending_include_all_products'] = include_all_products
        
        # Confirmation button
        if st.button(LANG['confirm_product_selection'], type="primary", use_container_width=True):
            # Inject products into the system
            st.session_state['selected_products'] = selected_product_ids
            st.session_state['include_all_products'] = include_all_products
            st.session_state['products_confirmed'] = True
            st.success(LANG['products_confirmed_success'])
            st.rerun()
        
        # Show current status
        if st.session_state.get('products_confirmed', False):
            if include_all_products:
                st.info(f"🌟 {LANG['content_strategy_all_products']} ({len(available_products)} {LANG['products_total']})")
            elif selected_product_ids:
                selected_names = [product_options[pid] for pid in selected_product_ids]
                st.success(f"✅ {len(selected_product_ids)} {LANG['products_selected']}: {', '.join(selected_names)}")
        
        # Quick stats
        st.markdown("---")
        st.markdown(f"#### {LANG['quick_stats_title']}")
        if st.session_state.get('products_confirmed', False):
            if include_all_products:
                st.info(LANG['active_all_products'].format(len(available_products)))
            elif selected_product_ids:
                st.info(LANG['active_selected_products'].format(len(selected_product_ids)))
            else:
                st.info(LANG['no_products_selected'])
        else:
            st.info(LANG['products_not_confirmed'])
    
    # Remove the manual content button since themes are now input directly
    # st.markdown("---")
    # st.markdown(f"#### {LANG['manual_content_title']}")
    # if st.button(f'🟢 {LANG["manually_request_content"]}', use_container_width=True):
    #     process_creative_outputs_manually()

    return selected_product_ids


def display_product_selector():
    """
    Display product multi-selection interface at the top of the SEO lab chat.
    DEPRECATED: Use render_seo_lab_sidebar() instead for sidebar integration.
    
    Returns:
        list: List of selected product IDs
    """
    try:
        # Get brand context
        context = st.session_state.get('context', {})
        brand_id = context.get('brand_id')
        if not brand_id:
            st.error(LANG.get('no_brand_selected', 'No brand selected. Please select a brand from the sidebar.'))
            return []
        
        # Load available products
        available_products = load_products_from_yaml(brand_id)
        
        if not available_products:
            st.warning(LANG['no_products_found'])
            return []
        
        # Create display options (product_id -> display_name mapping)
        product_options = {
            product_id: product_info['display_name'] 
            for product_id, product_info in available_products.items()
        }
        
        # Product multi-selector
        st.markdown(f"### 🎯 {LANG['product_selector_title']}")
        
        # NEW: Checkbox to include all products (set to True by default)
        include_all_products = st.checkbox(
            LANG['include_all_products'],
            value=st.session_state.get('include_all_products', True),  # Changed default to True
            help=LANG['include_all_products_help']
        )
        
        # Get current selection from session state
        current_selection = st.session_state.get('selected_products', [])
        
        # Ensure current selection items still exist in available products
        valid_selection = [p for p in current_selection if p in product_options]
        
        # Only show multiselect if include_all_products is False
        selected_product_ids = []
        if not include_all_products:
            selected_product_ids = st.multiselect(
                LANG['select_products'],
                options=list(product_options.keys()),
                default=valid_selection,
                format_func=lambda x: product_options.get(x, x),
                placeholder=LANG['select_products_placeholder'],
                help=LANG['select_products_help']
            )
        
        # Store both selections in session state
        st.session_state['selected_products'] = selected_product_ids
        st.session_state['include_all_products'] = include_all_products
        
        # Visual feedback
        if include_all_products:
            st.info(f"🌟 {LANG['content_strategy_all_products']} ({len(available_products)} {LANG['products_total']})")
        elif selected_product_ids:
            selected_names = [product_options[pid] for pid in selected_product_ids]
            st.success(f"✅ {len(selected_product_ids)} {LANG['products_selected']}: {', '.join(selected_names)}")
            
            # # Show selected products details in an expander
            # with st.expander("🔍 Selected Products Details", expanded=False):
            #     for product_id in selected_product_ids:
            #         product_info = available_products[product_id]
            #         product_data = product_info['data']
                    
            #         st.markdown(f"**{product_info['display_name']}**")
            #         st.markdown(f"- **ID:** {product_id}")
            #         st.markdown(f"- **File:** {product_info['file']}")
                    
            #         # Show key product information
            #         meta = product_data.get('meta', {})
            #         description = product_data.get('product_description', {})
                    
            #         if description.get('short'):
            #             st.markdown(f"- **Description:** {description['short']}")
                    
            #         if meta.get('category'):
            #             st.markdown(f"- **Category:** {meta['category']}")
                    
            #         st.markdown("---")
        
        # return selected_product_ids
        
    except Exception as e:
        st.error(LANG['error_product_selector'].format(str(e)))
        return []

# Legacy CSV-based keyword functions removed - now using enhanced keywords.py dictionary system

def get_products_context(selected_product_ids=None, include_all=False, brand_id=None):
    """
    Generate product context based on selection or all products.
    
    Args:
        selected_product_ids: List of selected product IDs (ignored if include_all=True)
        include_all: If True, include all available products
        brand_id: Brand identifier (if None, uses selected brand from session state)
        
    Returns:
        str: Formatted product context for the SEO lab system
    """
    # Use selected brand if not provided
    if brand_id is None:
        brand_id = get_selected_brand_id()
        if not brand_id:
            st.error(LANG.get('no_brand_selected', 'No brand selected. Please select a brand from the sidebar.'))
            return ""
    try:
        # Load all products
        all_products = load_products_from_yaml(brand_id)
        
        if include_all:
            # Include all products
            products_to_include = list(all_products.keys())
            context_header = "# ALL AVAILABLE PRODUCTS FOR CONTENT DEVELOPMENT\n\n"
        else:
            # Include only selected products
            if not selected_product_ids:
                return ""
            products_to_include = selected_product_ids
            context_header = "# SELECTED PRODUCTS FOR CONTENT DEVELOPMENT\n\n"
        
        # Build context
        products_context = context_header
        
        for product_id in products_to_include:
            if product_id in all_products:
                product_info = all_products[product_id]
                product_data = product_info['data']
                
                # Extract key information for context
                meta = product_data.get('meta', {})
                description = product_data.get('product_description', {})
                benefits = product_data.get('benefits', {})
                actives = product_data.get('actives', [])
                
                products_context += f"## {meta.get('display_name', 'Unknown Product')}\n"
                products_context += f"- **Product ID:** {meta.get('product_id', 'N/A')}\n"
                products_context += f"- **Category:** {meta.get('category', 'N/A')}\n"
                products_context += f"- **Subcategory:** {meta.get('subcategory', 'N/A')}\n"
                products_context += f"- **Price:** {meta.get('price_range', 'N/A')}\n"
                
                if description.get('short'):
                    products_context += f"- **Description:** {description['short']}\n"
                
                if description.get('key_differentiators'):
                    products_context += f"- **Key Differentiators:**\n"
                    for diff in description['key_differentiators']:
                        products_context += f"  - {diff}\n"
                
                # Add key benefits
                all_benefits = []
                for benefit_type, benefit_list in benefits.items():
                    if isinstance(benefit_list, list):
                        all_benefits.extend(benefit_list)
                
                if all_benefits:
                    products_context += f"- **Key Benefits:**\n"
                    # For "all products" mode, limit to top 3 benefits per product to manage context size
                    benefit_limit = 3 if include_all else 5
                    for benefit in all_benefits[:benefit_limit]:
                        products_context += f"  - {benefit}\n"
                
                # Add active ingredients
                if actives:
                    products_context += f"- **Active Ingredients:**\n"
                    # For "all products" mode, limit to top 2 actives per product to manage context size
                    active_limit = 2 if include_all else 3
                    for active in actives[:active_limit]:
                        name = active.get('name', 'Unknown')
                        function = active.get('function', 'No function specified')
                        products_context += f"  - **{name}:** {function}\n"
                
                products_context += "\n"
        
        return products_context
        
    except Exception as e:
        st.error(LANG['error_generating_products_context'].format(str(e)))
        return ""

def get_filtered_products_context(selected_product_ids, brand_id=None):
    """
    Generate filtered product context based on selected products.
    DEPRECATED: Use get_products_context() instead.
    
    Args:
        selected_product_ids: List of selected product IDs
        brand_id: Brand identifier (if None, uses selected brand from session state)
        
    Returns:
        str: Formatted product context for the SEO lab system
    """
    # Use selected brand if not provided
    if brand_id is None:
        brand_id = get_selected_brand_id()
        if not brand_id:
            st.error(LANG.get('no_brand_selected', 'No brand selected. Please select a brand from the sidebar.'))
            return ""
    return get_products_context(selected_product_ids, include_all=False, brand_id=brand_id)

def missing_outputs():
    """Check if we need to generate creative outputs."""
    return (
        'themes' not in st.session_state or 
        'seo_themes' not in st.session_state or 
        'macro_name' not in st.session_state or
        'brief_summaries' not in st.session_state or
        'products' not in st.session_state or
        'themes_displayed' not in st.session_state or
        'refined_themes' not in st.session_state or
        'combined_brief_summary' not in st.session_state or
        st.session_state.get('adjustment_mode', False)
    )

def validate_system_state_for_content_production():
    """
    Validate that the system is ready for content production.
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    error_messages = []
    
    # Check if brand is selected
    context = st.session_state.get('context', {})
    brand_id = context.get('brand_id')
    if not brand_id:
        error_messages.append("No brand selected. Please select a brand from the sidebar.")
    
    # Check if posts folder exists and has required files
    if brand_id:
        brand_folder = base_dir / 'z_brands' / brand_id
        posts_folder = brand_folder / 'posts'
        
        if not posts_folder.exists():
            error_messages.append(f"Posts folder not found: {posts_folder}")
        else:
            # Check for required files
            required_files = ['themes.py', 'seo_themes.py', 'brief_summary.py']
            missing_files = []
            for file_name in required_files:
                if not (posts_folder / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                error_messages.append(f"Missing required files: {', '.join(missing_files)}")
    
    is_valid = len(error_messages) == 0
    return is_valid, error_messages

def process_creative_outputs():
    """
    Process the creative outputs (themes and seo_themes) and generate the content.
    This function is called when the user clicks the "Request content" button.
    """
    # Comprehensive system validation before proceeding
    is_valid, error_messages = validate_system_state_for_content_production()
    
    if not is_valid:
        st.error(LANG.get('critical_error_system_not_ready', '❌ CRITICAL ERROR: System not ready for content production'))
        st.error(LANG.get('critical_error_issues_resolved', 'The following issues must be resolved:'))
        for error in error_messages:
            st.error(error)
        st.error(LANG.get('critical_error_fix_issues', 'Please fix these issues before attempting content production.'))
        return
    
    # If we get here, the system is valid
    st.success(LANG.get('system_validation_passed', '✅ System validation passed - proceeding with content production'))
    
    context = st.session_state.get('context', {})
    brand_id = context.get("brand_id")
    if not brand_id:
        st.warning(LANG['could_not_determine_brand'])
        return

    # Define brand_folder first
    brand_folder = base_dir / 'z_brands' / brand_id
    
    # Get data from session state
    themes = st.session_state['themes']
    seo_themes = st.session_state.get('seo_themes', {})
    brief_summaries = st.session_state.get('brief_summaries', {})
    keywords_dict = st.session_state.get('keywords', {})
    
    # Note: We don't need to call save_creative_outputs again here since it was already called
    # in execute_simplified_seo_flow. We just need the semantic_fields from session state.
    semantic_fields = st.session_state.get('semantic_fields', {})

    inputs = {
        'voice': context.get('voice', ''),
        'brand': context.get('brand', ''),
        'products': context.get('products', ''),
        'blog': context.get('blog', ''),
        'benchmarks': context.get('benchmarks', ''),
        'format_recommendations': context.get('format_recommendations', ''),
        'themes': themes,
        'macro_name': st.session_state.get('macro_name'),
        'brief_summary': st.session_state.get('combined_brief_summary', ''),
        'brand_folder': brand_folder,
        'semantic_fields': semantic_fields,
        'preferred_language': context.get('preferred_language', 'pt_BR')
    }

    try:
        from chats.seo_lab.src.copywriter_crew.main import write
        # Call write function and capture any return value
        result = write(inputs)
        
        # Check if content was actually generated by looking for generated files
        brand_folder_path = Path(brand_folder)
        posts_folder = brand_folder_path / 'posts'
        today = datetime.now().date().isoformat()
        macro_name = st.session_state.get('macro_name', 'content_campaign')
        save_path = posts_folder / f'{today}_{macro_name}'
        
        if save_path.exists() and any(save_path.glob('*.html')):
            st.success(LANG['content_produced_success'])
        else:
            st.warning(LANG.get('content_generation_no_files_warning', '⚠️ Content generation completed but no files were found. Please check the logs above for any errors.'))
            
    except Exception as e:
        st.error(LANG['error_starting_content_production'].format(str(e)))

def process_creative_outputs_manually():
    """
    Process the creative outputs (themes, seo_themes, brief_summaries) inserted manually.
    This function is called when the user clicks the "Request content manually" button.
    """
    # Comprehensive system validation before proceeding
    is_valid, error_messages = validate_system_state_for_content_production()
    
    if not is_valid:
        st.error(LANG.get('critical_error_manual_content', '❌ CRITICAL ERROR: System not ready for manual content production'))
        st.error(LANG.get('critical_error_issues_resolved', 'The following issues must be resolved:'))
        for error in error_messages:
            st.error(error)
        st.error(LANG.get('critical_error_fix_issues', 'Please fix these issues before attempting content production.'))
        return
    
    # If we get here, the system is valid
    st.success(LANG.get('system_validation_passed_manual', '✅ System validation passed - proceeding with manual content production'))
    
    context = st.session_state.get('context', {})
    brand_id = context.get("brand_id")
    if not brand_id:
        st.warning(LANG['could_not_determine_brand'])
        return

    brand_folder = base_dir / 'z_brands' / brand_id
    
    # Load themes, seo_themes, brief_summaries and semantic fields from local files
    try:
        loaded_data = load_local_creative_outputs(brand_folder)
        
        # CRITICAL FIX: Add validation for loaded data structure
        if not isinstance(loaded_data, dict):
            st.error(LANG.get('invalid_data_structure', '❌ Invalid data structure returned: expected dict, got {}').format(type(loaded_data)))
            return
        
        # Extract the loaded data with validation
        themes = loaded_data.get('themes', {})
        seo_themes = loaded_data.get('seo_themes', {})
        brief_summaries = loaded_data.get('brief_summaries', {})
        keywords = loaded_data.get('keywords', {})
        semantic_fields = loaded_data.get('semantic_fields', {})
        macro_name = loaded_data.get('macro_name', 'content_campaign')
        
        # Validate that required data is present
        if not themes or not seo_themes:
            st.error(LANG.get('missing_required_data', '❌ Missing required data: themes or seo_themes not found in local files'))
            st.info(LANG.get('ensure_files_exist', '💡 Please ensure the following files exist in the posts folder:'))
            st.info(LANG.get('themes_file_info', '- themes.py (with \'themes\' dictionary)'))
            st.info(LANG.get('seo_themes_file_info', '- seo_themes.py (with \'seo_themes\' dictionary)'))
            return
        
        # Update session state with loaded data
        st.session_state['themes'] = themes
        st.session_state['seo_themes'] = seo_themes
        st.session_state['brief_summaries'] = brief_summaries
        st.session_state['keywords'] = keywords
        st.session_state['macro_name'] = macro_name
        
        # Set flag to indicate manual mode is active
        st.session_state['manual_mode_active'] = True
        st.session_state['themes_displayed'] = True  # Skip conversational phase
        
        st.success(LANG.get('themes_loaded_success', '✅ Loaded {} themes, {} SEO themes, and {} brief summaries from local files').format(len(themes), len(seo_themes), len(brief_summaries)))
        
    except Exception as e:
        st.error(LANG.get('error_loading_local_files', '❌ Error loading local files: {}').format(str(e)))
        st.error(LANG.get('data_structure_issue', '🔧 This usually means there\'s an issue with the data structure in the posts folder'))
        st.info(LANG.get('check_files_format', '💡 Please check that all required files exist and have the correct format'))
        return
    
    inputs = {
        'voice': context.get('voice', ''),
        'brand': context.get('brand', ''),
        'brand_category': context.get('brand_category', ''),
        'products': context.get('products', ''),
        'blog': context.get('blog', ''),
        'benchmarks': context.get('benchmarks', ''),
        'format_recommendations': context.get('format_recommendations', ''),
        'themes': themes,
        'macro_name': st.session_state.get('macro_name'),
        'brief_summary': st.session_state.get('combined_brief_summary', ''),
        'brand_folder': brand_folder,
        'semantic_fields': semantic_fields,
        'preferred_language': context.get('preferred_language', 'pt_BR')
    }

    try:
        from chats.seo_lab.src.copywriter_crew.main import write
        # Call write function and capture any return value
        result = write(inputs)
        
        # Check if content was actually generated by looking for generated files
        brand_folder_path = Path(brand_folder)
        posts_folder = brand_folder_path / 'posts'
        today = datetime.now().date().isoformat()
        macro_name = st.session_state.get('macro_name', 'content_campaign')
        save_path = posts_folder / f'{today}_{macro_name}'
        
        if save_path.exists() and any(save_path.glob('*.html')):
            st.success(LANG['content_produced_success'])
        else:
            st.warning(LANG.get('content_generation_no_files_warning', '⚠️ Content generation completed but no files were found. Please check the logs above for any errors.'))
            
    except Exception as e:
        st.error(LANG['error_starting_content_production'].format(str(e)))

def render_seo_lab_next_button():
    """Render the Next button for SEO lab flow."""
    # Always show the next button, but check if user has had at least one interaction
    col1, col2 = st.columns([5, 1])
    
    with col2:
        # Check if user has had at least one interaction (memory has messages beyond system message)
        memory = st.session_state.get('memory', None)
        has_interaction = (memory and 
                          len(memory.buffer_as_messages) > 1)  # More than just system message
        
        # Show button with appropriate state
        if st.button(
            LANG['next_step_button'], 
            type="primary", 
            use_container_width=True, 
            help=LANG['next_step_button_help'],
            disabled=not has_interaction
        ):
            if has_interaction:
                # Set flag to trigger next phase in SEO lab
                st.session_state['next_step_triggered'] = True
                st.rerun()
            else:
                # Show guidance for first interaction
                st.warning(LANG.get('next_button_no_interaction', 'Please start a conversation first to enable the Next button.'))
    
    # Show status information in the main column
    with col1:
        if not has_interaction:
            st.info(LANG.get('next_button_status_info', 'Please start a conversation on the chat interface below.'))

def handle_seo_lab_flow(chat_interaction, chain, memory):
    #SEO Lab flow: Input → Save Files → Load Files → Content Generation
       
    # Show direct input interface for themes
    st.markdown(f"### 📝 {LANG.get('input_themes_title', 'Input Blog Themes')}")
    st.info(LANG.get('input_themes_description', 'Enter your blog themes directly in the fields below. The system will automatically save files and start content generation.'))
    
    # Direct input interface
    themes_input = display_themes_input_interface()
    
    # Show content production buttons if ready (after files are saved and loaded)
    if ('themes' in st.session_state and 'seo_themes' in st.session_state and 
        'brief_summaries' in st.session_state and 'combined_brief_summary' in st.session_state and
        'products' in st.session_state and 'keywords' in st.session_state):
        
            st.markdown(f"### 🚀 {LANG['phase_content_production']}")
            show_content_production_buttons()

def display_themes_user_friendly(themes, seo_themes, brief_summaries):
    """
    Display themes in a user-friendly format instead of raw Python dictionaries.
    
    Args:
        themes: Dictionary of themes
        seo_themes: Dictionary of SEO themes
        brief_summaries: Dictionary of brief summaries
        
    Returns:
        str: Formatted themes display
    """
    if not themes or not seo_themes:
        return ""
    
    formatted_output = []
    
    for i, (theme_key, theme_value) in enumerate(themes.items(), 1):
        seo_value = seo_themes.get(theme_key, '')
        brief_value = brief_summaries.get(theme_key, '')
        
        formatted_output.append(f"**Theme {i}** [{seo_value}]")
        formatted_output.append(f"{brief_value}")
        formatted_output.append("")  # Empty line between themes
    
    return "\n".join(formatted_output)

def handle_theme_refinement_chat(chat_interaction, chain, memory, selected_products=None, include_all_products=False):
    """
    Pure conversational theme refinement - no dictionary constraints
    This function now only sets up context and returns None since chat is handled in main nami function
    """
    try:
        # Get context and brand info
        context = st.session_state.get('context', {})
        brand_id = context.get('brand_id')
        if not brand_id:
            st.error(LANG.get('brand_id_missing', 'No brand selected. Please select a brand from the sidebar.'))
            return None
        
    
        # Create product-focused prompt if products are selected or all products are included
        if selected_products or include_all_products:
            # Update context with products
            products_context = get_products_context(
                selected_product_ids=selected_products,
                include_all=include_all_products,
                brand_id=brand_id
            )
            
            if products_context:
                context['products'] = products_context
                
 
        # Update session state with complete context
        st.session_state['context'] = context
        
 
   
    except Exception as e:
        st.error(LANG['theme_refinement_error'].format(str(e)))
        return None






def show_content_production_buttons():
    """Show buttons for content production after dictionaries are ready."""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"🔴 {LANG['make_adjustments']}", use_container_width=True):
            st.session_state['adjustment_mode'] = True
            st.rerun()

    with col2:
        if st.button(f'🟢 {LANG["request_content"]}', use_container_width=True):
            process_creative_outputs()

# Blog Post Editing Functions

def create_blog_posts_template(themes, seo_themes, brief_summaries):
    """
    Create a template for editing blog post elements.
    
    Args:
        themes: Dictionary of themes
        seo_themes: Dictionary of SEO themes
        brief_summaries: Dictionary of brief summaries
        
    Returns:
        str: Formatted template text
    """
    template_lines = []
    
    for i, (theme_key, theme_value) in enumerate(themes.items(), 1):
        seo_value = seo_themes.get(theme_key, '')
        brief_value = brief_summaries.get(theme_key, '')
        
        template_lines.append(f"BLOG POST {i}:")
        template_lines.append(f"THEME: {theme_value}")
        template_lines.append(f"SEO THEME: {seo_value}")
        template_lines.append(f"BRIEF SUMMARY: {brief_value}")
        template_lines.append("")  # Empty line between posts
    
    return "\n".join(template_lines)

def parse_blog_posts_text(text):
    """
    Parse the text area content to extract blog post elements.
    
    Args:
        text: Text from the text area
        
    Returns:
        tuple: (themes, seo_themes, brief_summaries) dictionaries
    """
    themes = {}
    seo_themes = {}
    brief_summaries = {}
    
    current_post = None
    current_section = None
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('BLOG POST'):
            # Extract post number and create key
            post_num = line.split(':')[0].split()[-1]
            current_post = f"post_{post_num}"
            current_section = None
        elif line.startswith('THEME:'):
            current_section = 'theme'
            value = line.split(':', 1)[1].strip()
            if current_post and value:
                themes[current_post] = value
        elif line.startswith('SEO THEME:'):
            current_section = 'seo_theme'
            value = line.split(':', 1)[1].strip()
            if current_post and value:
                seo_themes[current_post] = value
        elif line.startswith('BRIEF SUMMARY:'):
            current_section = 'brief_summary'
            value = line.split(':', 1)[1].strip()
            if current_post and value:
                brief_summaries[current_post] = value
    
    return themes, seo_themes, brief_summaries

def validate_blog_posts_elements(themes, seo_themes, brief_summaries):
    """
    Validate blog post elements for completeness and character limits.
    
    Args:
        themes: Dictionary of themes
        seo_themes: Dictionary of SEO themes
        brief_summaries: Dictionary of brief summaries
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if all dictionaries have the same keys
    all_keys = set(themes.keys()) | set(seo_themes.keys()) | set(brief_summaries.keys())
    
    if not all_keys:
        return False, LANG['blog_posts_empty_error']
    
    # Check if all posts have all three elements
    for key in all_keys:
        if key not in themes or not themes[key].strip():
            return False, f"Missing or empty theme for post {key}"
        if key not in seo_themes or not seo_themes[key].strip():
            return False, f"Missing or empty SEO theme for post {key}"
        if key not in brief_summaries or not brief_summaries[key].strip():
            return False, f"Missing or empty brief summary for post {key}"
    
    # Check character limits
    for key in all_keys:
        if len(themes[key]) > 150:
            return False, f"Theme for post {key} exceeds 150 character limit"
        if len(seo_themes[key]) > 150:
            return False, f"SEO theme for post {key} exceeds 150 character limit"
        if len(brief_summaries[key]) > 500:
            return False, f"Brief summary for post {key} exceeds 500 character limit"
    
    return True, ""

def create_combined_brief_summary(brief_summaries):
    """
    Combine individual brief summaries into a single string for crew context.
    
    Args:
        brief_summaries: Dictionary of brief summaries
        
    Returns:
        str: Combined brief summary
    """
    combined = []
    for post_key, summary in brief_summaries.items():
        combined.append(f"Blog Post {post_key}: {summary}")
    
    return "\n\n".join(combined)

def show_blog_posts_summary(themes, seo_themes, brief_summaries):
    """
    Display a summary of the edited blog post elements.
    
    Args:
        themes: Dictionary of themes
        seo_themes: Dictionary of SEO themes
        brief_summaries: Dictionary of brief summaries
    """
    st.markdown(f"### {LANG['blog_posts_summary_title']}")
    
    total_posts = len(themes)
    total_chars = sum(len(summary) for summary in brief_summaries.values())
    
    st.markdown(f"**{LANG['blog_posts_total']}** {total_posts}")
    st.markdown(f"**{LANG['blog_posts_total_characters']}** {total_chars}")
    
    with st.expander(f"📋 {LANG.get('blog_post_elements', 'Blog Post Elements')}", expanded=False):
        for i, (post_key, theme) in enumerate(themes.items(), 1):
            st.markdown(f"**{LANG.get('blog_post', 'Blog Post')} {i}:**")
            st.markdown(f"- **{LANG.get('theme', 'Theme')}:** {theme}")
            st.markdown(f"- **{LANG.get('seo_theme', 'SEO Theme')}:** {seo_themes.get(post_key, 'N/A')}")
            st.markdown(f"- **{LANG.get('brief_summary', 'Brief Summary')}:** {brief_summaries.get(post_key, 'N/A')}")
            st.markdown("---")

def display_blog_posts_editor(themes, seo_themes, brief_summaries):
    """
    Display the blog post editing interface.
    
    Args:
        themes: Dictionary of themes
        seo_themes: Dictionary of SEO themes
        brief_summaries: Dictionary of brief summaries
        
    Returns:
        tuple: (themes, seo_themes, brief_summaries) or (None, None, None) if cancelled
    """
    st.markdown(f"### {LANG['edit_blog_posts_title']}")
    st.markdown(LANG['edit_blog_posts_description'])
    
    # Create template
    template_text = create_blog_posts_template(themes, seo_themes, brief_summaries)
    
    # Display template
    with st.expander(f"📝 {LANG['blog_posts_template_title']}", expanded=True):
        st.markdown("```")
        st.markdown(template_text)
        st.markdown("```")
    
    # Text area for editing
    edited_text = st.text_area(
        LANG['edit_blog_posts_text_area'],
        value=template_text,
        height=400,
        help=LANG['edit_blog_posts_instruction']
    )
    
    # Save changes button
    if st.button(LANG['save_changes_button'], type="primary"):
        # Parse and validate
        parsed_themes, parsed_seo_themes, parsed_brief_summaries = parse_blog_posts_text(edited_text)
        
        is_valid, error_message = validate_blog_posts_elements(parsed_themes, parsed_seo_themes, parsed_brief_summaries)
        
        if is_valid:
            st.success(LANG['blog_posts_success'])
            show_blog_posts_summary(parsed_themes, parsed_seo_themes, parsed_brief_summaries)
            return parsed_themes, parsed_seo_themes, parsed_brief_summaries
        else:
            st.error(f"{LANG['blog_posts_validation_error']}: {error_message}")
            return None, None, None
    
    return None, None, None

def handle_seo_lab_flow_with_editing():
    """
    Handle the new SEO lab flow with pre-generation editing step.
    """
    # Check if we have the required elements in session state
    if 'themes' not in st.session_state or 'seo_themes' not in st.session_state:
        st.error(LANG.get('missing_themes_seo_themes', 'Missing themes and SEO themes. Please run theme refinement first.'))
        return
    
    themes = st.session_state['themes']
    seo_themes = st.session_state['seo_themes']
    
    # Initialize brief_summaries if not present
    if 'brief_summaries' not in st.session_state:
        st.session_state['brief_summaries'] = {key: f"Brief summary for {value}" for key, value in themes.items()}
    
    brief_summaries = st.session_state['brief_summaries']
    
    # Display editor
    edited_themes, edited_seo_themes, edited_brief_summaries = display_blog_posts_editor(
        themes, seo_themes, brief_summaries
    )
    
    if edited_themes and edited_seo_themes and edited_brief_summaries:
        # Update session state
        st.session_state['themes'] = edited_themes
        st.session_state['seo_themes'] = edited_seo_themes
        st.session_state['brief_summaries'] = edited_brief_summaries
        
        # Create combined brief summary for crew context
        combined_brief = create_combined_brief_summary(edited_brief_summaries)
        st.session_state['combined_brief_summary'] = combined_brief
        
        # Show content production buttons
        st.markdown("---")
        show_content_production_buttons()

def generate_products_dictionary(themes, selected_product_ids=None, include_all_products=False, brand_id=None):
    """
    Generate a products dictionary that maps each theme to specific product slugs needed for content.
    This optimizes token usage by only including relevant products per theme.
    
    Args:
        themes: Dictionary of themes
        selected_product_ids: List of selected product IDs (ignored if include_all_products=True)
        include_all_products: If True, include all available products
        brand_id: Brand identifier (if None, uses selected brand from session state)
        
    Returns:
        dict: Dictionary mapping theme keys to list of product slugs needed for that theme
    """
    # Use selected brand if not provided
    if brand_id is None:
        brand_id = get_selected_brand_id()
        if not brand_id:
            st.error(LANG.get('no_brand_selected', 'No brand selected. Please select a brand from the sidebar.'))
            return {}
    try:
        # Load all available products
        all_products = load_products_from_yaml(brand_id)
        
        if not all_products:
            return {}
        
        # Determine which products to consider
        if include_all_products:
            available_product_ids = list(all_products.keys())
        else:
            available_product_ids = selected_product_ids or []
        
        products_dict = {}
        
        for theme_key, theme_value in themes.items():
            # Analyze theme to determine relevant products
            relevant_products = analyze_theme_for_products(theme_value, all_products, available_product_ids)
            products_dict[theme_key] = relevant_products
        
        return products_dict
        
    except Exception as e:
        st.error(LANG.get('error_generating_products_dict', 'Error generating products dictionary: {}').format(str(e)))
        return {}

def analyze_theme_for_products(theme_value, all_products, available_product_ids):
    """
    Analyze a theme to determine which products are relevant for that specific content.
    
    Args:
        theme_value: The theme text to analyze
        all_products: Dictionary of all available products
        available_product_ids: List of product IDs to consider
        
    Returns:
        list: List of product slugs relevant to this theme
    """
    theme_lower = theme_value.lower()
    relevant_products = []
    
    # Define product keyword mappings
    product_keywords = {
        'booster-antifrizz': ['antifrizz', 'frizz', 'alinhamento', 'controle'],
        'booster-antioxidante': ['antioxidante', 'proteção', 'cor', 'vitalidade'],
        'booster-fortificante': ['fortificante', 'fortalecimento', 'queda', 'resistência'],
        'booster-hidratante': ['hidratante', 'hidratação', 'brilho', 'maciez'],
        'booster-definicao': ['definição', 'cachos', 'ondas', 'textura'],
        'leave-in-pluma': ['leave-in', 'pluma', 'proteção térmica', 'finalização'],
        'leave-in-com-protecao-termica': ['leave-in', 'proteção térmica', 'calor'],
        'mascara-condicionadora': ['máscara', 'condicionadora', 'nutrição', 'tratamento'],
        'primer-cachos-definidos': ['primer', 'cachos', 'definição', 'leveza'],
        'primer-liso-intacto': ['primer', 'liso', 'alinhamento', 'intacto'],
        'shampoo-a-seco': ['shampoo a seco', 'limpeza', 'frescor'],
        'shampoo-sem-sulfato': ['shampoo sem sulfato', 'limpeza suave', 'sem sulfato']
    }
    
    # Check each available product for relevance
    for product_id in available_product_ids:
        if product_id in all_products:
            product_info = all_products[product_id]
            product_data = product_info['data']
            
            # Get product keywords for this product
            product_keywords_list = product_keywords.get(product_id, [])
            
            # Check if any product keywords appear in the theme
            is_relevant = any(keyword in theme_lower for keyword in product_keywords_list)
            
            # Also check product display name and description
            if not is_relevant:
                display_name = product_data.get('meta', {}).get('display_name', '').lower()
                description = product_data.get('product_description', {}).get('short', '').lower()
                
                # Check if product name or description keywords appear in theme
                is_relevant = (display_name in theme_lower or 
                             any(word in theme_lower for word in display_name.split()))
            
            if is_relevant:
                # Get the product slug (product_id)
                relevant_products.append(product_id)
    
    # If no specific products found, include core products for general themes
    if not relevant_products and available_product_ids:
        # Include basic products for general beauty care themes
        basic_products = ['shampoo-sem-sulfato', 'booster-hidratante']
        relevant_products = [pid for pid in basic_products if pid in available_product_ids]
    
    return relevant_products

def get_optimized_products_context(theme_key, products_dict, brand_id=None):
    """
    Get optimized product context for a specific theme, including only relevant products.
    
    Args:
        theme_key: The theme key to get products for
        products_dict: Dictionary mapping themes to product slugs
        brand_id: Brand identifier (if None, uses selected brand from session state)
        
    Returns:
        str: Formatted product context optimized for the specific theme
    """
    # Use selected brand if not provided
    if brand_id is None:
        brand_id = get_selected_brand_id()
        if not brand_id:
            st.error(LANG.get('no_brand_selected', 'No brand selected. Please select a brand from the sidebar.'))
            return ""
    try:
        # Get relevant products for this theme
        relevant_product_ids = products_dict.get(theme_key, [])
        
        if not relevant_product_ids:
            return ""
        
        # Load all products
        all_products = load_products_from_yaml(brand_id)
        
        if not all_products:
            return ""
        
        # Build optimized context
        products_context = f"# PRODUCTS FOR THEME: {theme_key}\n\n"
        
        for product_id in relevant_product_ids:
            if product_id in all_products:
                product_info = all_products[product_id]
                product_data = product_info['data']
                
                # Extract key information for context
                meta = product_data.get('meta', {})
                description = product_data.get('product_description', {})
                benefits = product_data.get('benefits', {})
                actives = product_data.get('actives', [])
                
                products_context += f"## {meta.get('display_name', 'Unknown Product')}\n"
                products_context += f"- **Product ID:** {meta.get('product_id', 'N/A')}\n"
                products_context += f"- **Category:** {meta.get('category', 'N/A')}\n"
                products_context += f"- **Subcategory:** {meta.get('subcategory', 'N/A')}\n"
                
                if description.get('short'):
                    products_context += f"- **Description:** {description['short']}\n"
                
                if description.get('key_differentiators'):
                    products_context += f"- **Key Differentiators:**\n"
                    for diff in description['key_differentiators']:
                        products_context += f"  - {diff}\n"
                
                # Add key benefits (limited for token optimization)
                all_benefits = []
                for benefit_type, benefit_list in benefits.items():
                    if isinstance(benefit_list, list):
                        all_benefits.extend(benefit_list)
                
                if all_benefits:
                    products_context += f"- **Key Benefits:**\n"
                    for benefit in all_benefits[:3]:  # Limit to top 3 benefits
                        products_context += f"  - {benefit}\n"
                
                # Add active ingredients (limited for token optimization)
                if actives:
                    products_context += f"- **Active Ingredients:**\n"
                    for active in actives[:2]:  # Limit to top 2 actives
                        name = active.get('name', 'Unknown')
                        function = active.get('function', 'No function specified')
                        products_context += f"  - **{name}:** {function}\n"
                
                products_context += "\n"
        
        return products_context
        
    except Exception as e:
        st.error(LANG.get('error_generating_optimized_context', 'Error generating optimized products context: {}').format(str(e)))
        return ""

def get_available_product_options():
    """
    Get available products for selection in the input interface.
    
    Returns:
        dict: Dictionary mapping product IDs to display names
    """
    try:
        context = st.session_state.get('context', {})
        brand_id = context.get('brand_id')
        
        if not brand_id:
            return {}
        
        available_products = load_products_from_yaml(brand_id)
        
        return {
            product_id: product_info['display_name'] 
            for product_id, product_info in available_products.items()
        }
        
    except Exception as e:
        st.error(LANG.get('error_loading_products', 'Error loading products: {}').format(str(e)))
        return {}

def display_themes_input_interface():
    """
    Display single text area interface for pasting complete content block.
    Uses parse_creative_outputs to extract dictionaries from the text.
    
    Returns:
        dict: Dictionary with themes, seo_themes, brief_summaries, keywords, products, and macro_name
    """
    st.markdown(f"#### {LANG.get('single_input_title', 'Paste Your Complete Content Block')}")
    st.info(LANG.get('single_input_description', 'Paste your complete content block below. The system will automatically parse all dictionaries from the text.'))
    
    # Show example format
    with st.expander(f"📋 {LANG.get('example_format_title', 'Example Format')}", expanded=False):
        st.code('''themes = {
    "Cachos definidos": "Cachos definidos e hidratados: a rotina personalizada GE Beauty",
    "Frizz cachos": "Como controlar o frizz e manter a leveza dos cachos todos os dias"
}

seo_themes = {
    "Cachos definidos": "hidratação cachos definidos",
    "Frizz cachos": "cabelos cacheados sem frizz"
}

brief_summary = {
    "Cachos definidos": "Conteúdo educativo para mulheres cacheadas...",
    "Frizz cachos": "Guia prático para consumidoras com frizz..."
}

products = {
    "Cachos definidos": ["booster-definicao", "booster-hidratante"],
    "Frizz cachos": ["booster-antifrizz", "leave-in-pluma"]
}

keywords = {
    "Cachos definidos": {
        "primary_keywords": ["cachos definidos hidratação"],
        "competition_level": "médio"
    }
}

macro_name = "rotinas_personalizadas_por_tipo"''')
    
    # Single text area for complete content block
    content_input = st.text_area(
        LANG.get('content_input_label', 'Complete Content Block:'),
        key="complete_content_block",
        placeholder=LANG.get('content_input_placeholder', 'Paste your complete content block here...'),
        height=400,
        help=LANG.get('content_input_help', 'Paste the complete content block with all dictionaries and macro_name')
    )
    
    # Process button
    if st.button(LANG.get('process_content_button', 'Process Content'), type="primary", use_container_width=True):
        if content_input:
            try:
                # Use parse_creative_outputs to extract dictionaries from the text
                from chats.seo_lab.utils import parse_creative_outputs
                parse_creative_outputs(content_input)
                
                # Check if parsing was successful by checking session state
                if (st.session_state.get('themes') and 
                    st.session_state.get('seo_themes') and 
                    st.session_state.get('brief_summaries') and
                    st.session_state.get('products') and
                    st.session_state.get('keywords') and
                    st.session_state.get('macro_name')):
                    
                    st.success(LANG.get('content_parsed_success', '✅ Content parsed successfully! All dictionaries extracted.'))
                    
                    # Create themes_data from session state
                themes_data = {
                        'themes': st.session_state['themes'],
                        'seo_themes': st.session_state['seo_themes'],
                        'brief_summaries': st.session_state['brief_summaries'],
                        'keywords': st.session_state['keywords'],
                        'products': st.session_state['products'],
                        'macro_name': st.session_state['macro_name']
                    }
                
                # SIMPLIFIED FLOW: Save files → Load files → Start content generation
                if execute_simplified_seo_flow(themes_data):
                    st.success(LANG.get('content_generation_started', '🚀 Content generation started! Check the progress below.'))
                    st.rerun()
                
                    return themes_data
                else:
                    st.error(LANG.get('parsing_failed_error', '❌ Failed to parse content. Please check the format and try again.'))
                    st.info(LANG.get('parsing_format_help', 'Make sure your content includes all required dictionaries: themes, seo_themes, brief_summary, products, keywords, and macro_name.'))
                    return None
                
            except Exception as e:
                st.error(LANG.get('error_parsing_content', '❌ Error parsing content: {}').format(str(e)))
                st.error(LANG.get('error_parsing_format', 'Please ensure the content is in valid Python dictionary format.'))
                return None
        else:
            st.error(LANG.get('error_missing_content', 'Please paste your content block before processing.'))
            return None
    
    return None

# REMOVED: process_themes_input function is no longer needed in simplified flow

def execute_simplified_seo_flow(themes_data):
    """
    SIMPLIFIED SEO FLOW: Save files → Load files → Start content generation
    
    This function implements the streamlined flow:
    1. Save creative outputs to brand folder
    2. Load local creative outputs
    3. Start content production
    
    Args:
        themes_data: Dictionary containing all theme information
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get brand context
        context = st.session_state.get('context', {})
        brand_id = context.get('brand_id')
        if not brand_id:
            st.error(LANG.get('brand_id_missing', '❌ No brand selected. Please select a brand from the sidebar.'))
            return False
        
        brand_folder = base_dir / 'z_brands' / brand_id
        
        st.info(LANG.get('starting_simplified_seo_flow', '🎯 Starting simplified SEO flow for brand: {}').format(brand_id))
        
        # STEP 1: Save creative outputs to brand folder
        st.info(LANG.get('step1_saving_creative_outputs', '📁 Step 1: Saving creative outputs to brand folder...'))
        try:
            from chats.seo_lab.utils import save_creative_outputs
            
            semantic_fields = save_creative_outputs(
                brand_folder, 
                themes_data['themes'], 
                themes_data['seo_themes'], 
                themes_data['brief_summaries'], 
                themes_data['keywords']
            )
            
            if semantic_fields:
                st.success(LANG.get('step1_complete_success', '✅ Step 1 complete: All dictionary files saved successfully!'))
            else:
                st.warning(LANG.get('step1_warning_files', '⚠️ Step 1 warning: Some files may not have been saved properly'))
                
        except Exception as e:
            st.error(LANG.get('step1_failed_error', '❌ Step 1 failed: Error saving creative outputs: {}').format(str(e)))
            return False
        
        # STEP 2: Load local creative outputs
        st.info(LANG.get('step2_loading_creative_outputs', '📂 Step 2: Loading local creative outputs...'))
        try:
            from chats.seo_lab.utils import load_local_creative_outputs
            
            loaded_data = load_local_creative_outputs(brand_folder)
            
            if loaded_data and 'themes' in loaded_data:
                st.success(LANG.get('step2_complete_success', '✅ Step 2 complete: Loaded {} themes from local files').format(len(loaded_data['themes'])))
                
                # Update session state with loaded data
                st.session_state['themes'] = loaded_data['themes']
                st.session_state['seo_themes'] = loaded_data.get('seo_themes', {})
                st.session_state['brief_summaries'] = loaded_data.get('brief_summaries', {})
                st.session_state['keywords'] = loaded_data.get('keywords', {})
                st.session_state['products'] = loaded_data.get('products', {})
                st.session_state['macro_name'] = themes_data['macro_name']
                st.session_state['semantic_fields'] = loaded_data.get('semantic_fields', {})
                
                # Create combined brief summary for crew context
                if 'brief_summaries' in loaded_data:
                    combined_brief = create_combined_brief_summary(loaded_data['brief_summaries'])
                    st.session_state['combined_brief_summary'] = combined_brief
                    st.session_state['brief_summary'] = combined_brief
                
            else:
                st.error(LANG.get('step2_failed_error', '❌ Step 2 failed: Could not load local creative outputs'))
                return False
                
        except Exception as e:
            st.error(LANG.get('step2_failed_loading_error', '❌ Step 2 failed: Error loading local creative outputs: {}').format(str(e)))
            return False
        
        # STEP 3: Start content production
        st.info(LANG.get('step3_starting_content_production', '🚀 Step 3: Starting content production...'))
        try:
            # Call process_creative_outputs to start content generation
            process_creative_outputs()
            st.success(LANG.get('step3_complete_success', '✅ Step 3 complete: Content production started successfully!'))
            return True
            
        except Exception as e:
            st.error(LANG.get('step3_failed_error', '❌ Step 3 failed: Error starting content production: {}').format(str(e)))
            return False
            
    except Exception as e:
        st.error(LANG.get('critical_error_simplified_flow', '❌ Critical error in simplified SEO flow: {}').format(str(e)))
        return False
