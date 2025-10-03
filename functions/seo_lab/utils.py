import os
import re
import streamlit as st
import ast

from langchain.memory import ConversationBufferMemory
from pathlib import Path


# Data Type Safety Utilities - Prevent Runtime Errors
def safe_get_nested(data, *keys, default=None):
    """
    Safely get nested dictionary values with type checking.
    Prevents 'list' object has no attribute 'get' and similar errors.
    
    Args:
        data: The data structure to navigate
        *keys: Sequence of keys to traverse
        default: Default value if any step fails
    
    Returns:
        The value at the nested location or default
    """
    if not isinstance(data, dict):
        return default
    
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        if key not in current:
            return default
        current = current[key]
    
    return current

def safe_extract_field(data, field_name, expected_type, default=None):
    """
    Safely extract a field from data with type validation.
    
    Args:
        data: The data structure to extract from
        field_name: Name of the field to extract
        expected_type: Expected type of the field
        default: Default value if extraction fails
    
    Returns:
        The extracted value or default
    """
    try:
        if not isinstance(data, dict):
            print(f"⚠️ Data is not a dictionary: {type(data)}")
            return default
        
        if field_name not in data:
            print(f"⚠️ Field '{field_name}' not found in data")
            return default
        
        value = data[field_name]
        
        if not isinstance(value, expected_type):
            print(f"⚠️ Field '{field_name}' is not {expected_type.__name__}: {type(value)}")
            return default
        
        return value
        
    except Exception as e:
        print(f"⚠️ Error extracting field '{field_name}': {e}")
        return default

def safe_iterate_dict(data, key_type=str, value_type=str):
    """
    Safely iterate over dictionary items with type validation.
    
    Args:
        data: Dictionary to iterate over
        key_type: Expected type for keys
        value_type: Expected type for values
    
    Yields:
        Tuple of (key, value) for valid items only
    """
    if not isinstance(data, dict):
        print(f"⚠️ Cannot iterate over non-dict: {type(data)}")
        return
    
    for key, value in data.items():
        if not isinstance(key, key_type):
            print(f"⚠️ Skipping non-{key_type.__name__} key: {type(key)}")
            continue
            
        if not isinstance(value, value_type):
            print(f"⚠️ Skipping non-{value_type.__name__} value for '{key}': {type(value)}")
            continue
            
        yield key, value

def validate_data_structure(data, required_fields):
    """
    Validate that data has the required structure and types.
    
    Args:
        data: Data to validate
        required_fields: Dict of field_name: expected_type pairs
    
    Returns:
        tuple: (is_valid, missing_fields, type_errors)
    """
    if not isinstance(data, dict):
        return False, [], [f"Expected dict, got {type(data)}"]
    
    missing_fields = []
    type_errors = []
    
    for field_name, expected_type in required_fields.items():
        if field_name not in data:
            missing_fields.append(field_name)
        elif not isinstance(data[field_name], expected_type):
            type_errors.append(f"Field '{field_name}' should be {expected_type.__name__}, got {type(data[field_name])}")
    
    is_valid = len(missing_fields) == 0 and len(type_errors) == 0
    return is_valid, missing_fields, type_errors

# Function to parse creative outputs from model response
def extract_dictionary_with_braces(text, dict_name):
    """
    Extract a dictionary from text by properly counting braces to handle nested structures.
    
    Args:
        text: The text to search in
        dict_name: The name of the dictionary variable (e.g., 'themes', 'keywords')
        
    Returns:
        str: The complete dictionary text including the variable name and assignment
    """
    pattern = re.search(rf'{dict_name}\s*=\s*{{', text, re.DOTALL)
    if not pattern:
        return None
    
    # Find the start position of the dictionary
    start_pos = pattern.end() - 1  # Position of the opening {
    
    # Count braces to find the matching closing brace
    brace_count = 0
    end_pos = start_pos
    
    for i, char in enumerate(text[start_pos:], start_pos):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break
    
    # Extract the complete dictionary
    return text[pattern.start():end_pos]

def parse_creative_outputs(resposta):
    # Create hidden containers for debug output (processed but not visible)
    debug_container = st.empty()
    
    # Debug output is processed but hidden from user
    with debug_container.container():
        st.write("Analyzing model response:", resposta)  # Debug output

    # Try to extract themes dictionary from response
    theme_text = extract_dictionary_with_braces(resposta, 'themes')
    if theme_text:
        try:
            with debug_container.container():
                st.write("Theme text found:", theme_text)  # Debug output
            theme_data = ast.literal_eval(theme_text.split('=')[1].strip())
            # Handle both sets and dictionaries
            if isinstance(theme_data, set):
                # Convert set to dictionary with indexed keys
                theme_dict = {f"theme_{i}": theme for i, theme in enumerate(theme_data)}
            elif isinstance(theme_data, dict):
                theme_dict = theme_data
            else:
                theme_dict = None
                
            if theme_dict:
                st.session_state['themes'] = theme_dict
                st.session_state['adjustment_mode'] = False
                with debug_container.container():
                    st.write("✅ Themes extracted successfully:", theme_dict)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting themes: {e}")
            with debug_container.container():
                st.write("Text found:", theme_text)  # Debug output

    # Try to extract seo_themes dictionary from response
    seo_theme_text = extract_dictionary_with_braces(resposta, 'seo_themes')
    if seo_theme_text:
        try:
            with debug_container.container():
                st.write("SEO themes text found:", seo_theme_text)  # Debug output
            seo_theme_data = ast.literal_eval(seo_theme_text.split('=')[1].strip())
            # Handle both sets and dictionaries
            if isinstance(seo_theme_data, set):
                # Convert set to dictionary with indexed keys
                seo_theme_dict = {f"seo_theme_{i}": theme for i, theme in enumerate(seo_theme_data)}
            elif isinstance(seo_theme_data, dict):
                seo_theme_dict = seo_theme_data
            else:
                seo_theme_dict = None
                
            if seo_theme_dict:
                st.session_state['seo_themes'] = seo_theme_dict
                st.session_state['adjustment_mode'] = False
                with debug_container.container():
                    st.write("✅ SEO themes extracted successfully:", seo_theme_dict)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting seo_themes: {e}")
            with debug_container.container():
                st.write("Text found:", seo_theme_text)  # Debug output

    # Try to extract brief_summary dictionary from response
    brief_summary_text = extract_dictionary_with_braces(resposta, 'brief_summary')
    if brief_summary_text:
        try:
            with debug_container.container():
                st.write("Brief summary text found:", brief_summary_text)  # Debug output
            brief_summary_data = ast.literal_eval(brief_summary_text.split('=')[1].strip())
            # Handle both sets and dictionaries
            if isinstance(brief_summary_data, set):
                # Convert set to dictionary with indexed keys
                brief_summary_dict = {f"brief_{i}": summary for i, summary in enumerate(brief_summary_data)}
            elif isinstance(brief_summary_data, dict):
                brief_summary_dict = brief_summary_data
            else:
                brief_summary_dict = None
                
            if brief_summary_dict:
                st.session_state['brief_summaries'] = brief_summary_dict
                st.session_state['adjustment_mode'] = False
                with debug_container.container():
                    st.write("✅ Brief summaries extracted successfully:", brief_summary_dict)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting brief_summary: {e}")
            with debug_container.container():
                st.write("Text found:", brief_summary_text)  # Debug output

    # Try to extract products dictionary from response
    products_text = extract_dictionary_with_braces(resposta, 'products')
    if products_text:
        try:
            with debug_container.container():
                st.write("Products text found:", products_text)  # Debug output
            products_data = ast.literal_eval(products_text.split('=')[1].strip())
            # Handle both sets and dictionaries
            if isinstance(products_data, set):
                # Convert set to dictionary with indexed keys
                products_dict = {f"product_{i}": product for i, product in enumerate(products_data)}
            elif isinstance(products_data, dict):
                products_dict = products_data
            else:
                products_dict = None
                
            if products_dict:
                st.session_state['products'] = products_dict
                st.session_state['adjustment_mode'] = False
                with debug_container.container():
                    st.write("✅ Products dictionary extracted successfully:", products_dict)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting products: {e}")
            with debug_container.container():
                st.write("Text found:", products_text)  # Debug output

    # Try to extract macro_name from response
    macro_name_pattern = re.search(r'macro_name\s*=\s*["\']([^"\']+)["\']', resposta)
    if macro_name_pattern:
        try:
            macro_name = macro_name_pattern.group(1)  # Get the actual name without quotes
            st.session_state['macro_name'] = macro_name
            st.session_state['adjustment_mode'] = False
            with debug_container.container():
                st.write("✅ Macro name extracted successfully:", macro_name)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting macro_name: {e}")
            with debug_container.container():
                st.write("Text found:", macro_name_pattern.group(0))  # Debug output

    # Try to extract keywords dictionary from response
    keywords_text = extract_dictionary_with_braces(resposta, 'keywords')
    if keywords_text:
        try:
            with debug_container.container():
                st.write("Keywords text found:", keywords_text)  # Debug output
            keywords_dict = ast.literal_eval(keywords_text.split('=')[1].strip())
            if isinstance(keywords_dict, dict):
                st.session_state['keywords'] = keywords_dict
                st.session_state['adjustment_mode'] = False
                with debug_container.container():
                    st.write("✅ Keywords dictionary extracted successfully:", keywords_dict)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting keywords: {e}")
            with debug_container.container():
                st.write("Text found:", keywords_text)  # Debug output
    
    # Clear the debug container to ensure it's completely hidden
    debug_container.empty()
    
    # Import translations
    from translations import LANG
    
    # Debug output for session state - MOVED TO EXPANDER
    with st.expander(LANG['technical_details_debug'], expanded=False):
        st.write("Current session state:", {
            'themes': st.session_state.get('themes'),
            'seo_themes': st.session_state.get('seo_themes'),
            'brief_summaries': st.session_state.get('brief_summaries'),
            'products': st.session_state.get('products'),
            'keywords': st.session_state.get('keywords'),
            'macro_name': st.session_state.get('macro_name')
        })
        

def save_creative_outputs(brand_folder, themes, seo_themes, brief_summaries=None, keywords_dict=None):
    """
    Save theme files, seo_themes, brief_summaries, products dictionary, keywords dictionary and semantic fields for the specified brand.
    """
    posts_folder = Path(brand_folder) / 'posts'
    os.makedirs(posts_folder, exist_ok=True)

    # Save themes.py
    with open(posts_folder / 'themes.py', 'w', encoding='utf-8') as f:
        f.write("themes = {\n")
        for k, v in themes.items():
            f.write(f'    "{k}": "{v}",\n')
        f.write("}\n")

    # Save seo_themes.py
    with open(posts_folder / 'seo_themes.py', 'w', encoding='utf-8') as f:
        f.write("seo_themes = {\n")
        for k, v in seo_themes.items():
            f.write(f'    "{k}": "{v}",\n')
        f.write("}\n")

    # Save brief_summary.py
    with open(posts_folder / 'brief_summary.py', 'w', encoding='utf-8') as f:
        f.write("brief_summary = {\n")
        for k, v in brief_summaries.items():
            # Escape quotes in the summary text
            escaped_v = v.replace('"', '\\"').replace('\n', '\\n')
            f.write(f'    "{k}": "{escaped_v}",\n')
        f.write("}\n")

    # Generate and save products.py dictionary
    try:
        from functions.seo_lab._seo_lab import generate_products_dictionary
        # Get selected products from session state
        selected_products = st.session_state.get('selected_products', [])
        include_all_products = st.session_state.get('include_all_products', False)
        brand_id = st.session_state.get('context', {}).get('brand_id')
        if not brand_id:
            # Import translations
            from translations import LANG
            st.error(f"⚠️ {LANG['brand_id_missing']}")
            return {}
        
        products_dict = generate_products_dictionary(
            themes, 
            selected_products, 
            include_all_products, 
            brand_id
        )
        
        # Save products.py
        with open(posts_folder / 'products.py', 'w', encoding='utf-8') as f:
            f.write("products = {\n")
            for k, v in products_dict.items():
                # Convert list to string representation
                products_str = '[' + ', '.join([f'"{p}"' for p in v]) + ']'
                f.write(f'    "{k}": {products_str},\n')
            f.write("}\n")
            
        print(f"✅ Products dictionary saved to {posts_folder / 'products.py'}")
        
    except Exception as e:
        print(f"⚠️ Could not generate products dictionary: {e}")
        # Create empty products dictionary as fallback
        with open(posts_folder / 'products.py', 'w', encoding='utf-8') as f:
            f.write("products = {\n")
            for k in themes.keys():
                f.write(f'    "{k}": [],\n')
            f.write("}\n")

    # Save keywords.py dictionary with SerpApi-enhanced data
    if keywords_dict:
        try:
            with open(posts_folder / 'keywords.py', 'w', encoding='utf-8') as f:
                f.write("keywords = {\n")
                for theme_key, keyword_data in keywords_dict.items():
                    f.write(f'    "{theme_key}": {{\n')
                    
                    # Write primary_keywords
                    primary_keywords = keyword_data.get('primary_keywords', [])
                    f.write(f'        "primary_keywords": {primary_keywords},\n')
                    
                    # Write long_tail_keywords
                    long_tail_keywords = keyword_data.get('long_tail_keywords', [])
                    f.write(f'        "long_tail_keywords": {long_tail_keywords},\n')
                    
                    # Write related_searches
                    related_searches = keyword_data.get('related_searches', [])
                    f.write(f'        "related_searches": {related_searches},\n')
                    
                    # Write search_volume
                    search_volume = keyword_data.get('search_volume', {})
                    f.write(f'        "search_volume": {search_volume},\n')
                    
                    # Write competition_level
                    competition_level = keyword_data.get('competition_level', 'unknown')
                    f.write(f'        "competition_level": "{competition_level}"\n')
                    
                    f.write('    },\n')
                f.write("}\n")
            
            print(f"✅ Keywords dictionary saved to {posts_folder / 'keywords.py'}")
            
        except Exception as e:
            print(f"⚠️ Could not save keywords dictionary: {e}")
            # Create empty keywords dictionary as fallback
            with open(posts_folder / 'keywords.py', 'w', encoding='utf-8') as f:
                f.write("keywords = {\n")
                for k in themes.keys():
                    f.write(f'    "{k}": {{\n')
                    f.write(f'        "primary_keywords": [],\n')
                    f.write(f'        "long_tail_keywords": [],\n')
                    f.write(f'        "related_searches": [],\n')
                    f.write(f'        "search_volume": {{}},\n')
                    f.write(f'        "competition_level": "unknown"\n')
                    f.write(f'    }},\n')
                f.write("}\n")
    else:
        # Create empty keywords dictionary if none provided
        with open(posts_folder / 'keywords.py', 'w', encoding='utf-8') as f:
            f.write("keywords = {\n")
            for k in themes.keys():
                f.write(f'    "{k}": {{\n')
                f.write(f'        "primary_keywords": [],\n')
                f.write(f'        "long_tail_keywords": [],\n')
                f.write(f'        "related_searches": [],\n')
                f.write(f'        "search_volume": {{}},\n')
                f.write(f'        "competition_level": "unknown"\n')
                f.write(f'    }},\n')
            f.write("}\n")
        print(f"📝 Created empty keywords dictionary at {posts_folder / 'keywords.py'}")

    # Generate semantic fields based on enhanced keywords data
    semantic_fields = {}
    
    if keywords_dict:
        # Use enhanced keywords data to generate semantic fields
        for title, short_name in seo_themes.items():
            # Generate semantic fields from keywords data
            title_semantics = generate_semantic_fields_from_keywords(title, keywords_dict)
            name_semantics = generate_semantic_fields_from_keywords(short_name, keywords_dict)
            
            # For combined theme, try to find the best match in keywords
            combined_theme = f"{title}: {short_name}"
            combined_semantics = generate_semantic_fields_from_keywords(combined_theme, keywords_dict)
            
            # If no combined match, use title semantics as fallback
            if not combined_semantics:
                combined_semantics = title_semantics

            semantic_fields[title] = {
                'summary': title_semantics,
                'complete': name_semantics,
                'combined': combined_semantics
            }
    else:
        # Fallback: generate basic semantic fields without external API calls
        for title, short_name in seo_themes.items():
            # Create basic semantic fields structure
            basic_semantics = {
                'base_keyword': title,
                'related_google': [title, short_name],
                'long_tail_keywords': [f"{title} {short_name}", f"como usar {title}"],
                'search_intent': 'informational',
                'suggested_titles': [title, short_name],
                'h1': f"Tudo sobre {title}",
                'h2': [f"O que é {title}", f"Como usar {title}", f"Benefícios do {title}"]
            }
            
            semantic_fields[title] = {
                'summary': basic_semantics,
                'complete': basic_semantics,
                'combined': basic_semantics
            }
    
    # Save semantic_fields.md
    with open(posts_folder / 'semantic_fields.md', 'w', encoding='utf-8') as f:
        for title, short_name in seo_themes.items():
            if title in semantic_fields:
                data = semantic_fields[title]['summary']
                f.write(f"# {title}: {short_name}\n\n")
                f.write("## Related keywords\n")
                for item in data.get('related_google', []):
                    f.write(f"- {item}\n")
                f.write("\n## Intent\n")
                f.write(f"- {data.get('search_intent', 'N/A')}\n")
                f.write("\n## Suggested titles\n")
                for item in data.get('suggested_titles', []):
                    f.write(f"- {item}\n")
                f.write("\n## Headers\n")
                f.write(f"**H1:** {data.get('h1', 'N/A')}\n")
                for h2 in data.get('h2', []):
                    f.write(f"- H2: {h2}\n")
                f.write("\n---\n\n")

    return semantic_fields

def generate_semantic_fields_from_keywords(theme_key, keywords_data):
    """
    Generate semantic fields from pre-defined enhanced keywords data.
    This replaces the need for extract_seo by using pre-researched keyword data.
    
    Args:
        theme_key: The theme key to generate semantic fields for
        keywords_data: The enhanced keywords dictionary from keywords.py
        
    Returns:
        dict: Complete semantic fields data for the theme
    """
    # CRITICAL FIX: Use safety utilities for robust type checking
    if not isinstance(theme_key, str):
        print(f"⚠️ Theme key is not a string: {type(theme_key)}")
        return {}
    
    if not isinstance(keywords_data, dict):
        print(f"⚠️ Keywords data is not a dictionary: {type(keywords_data)}")
        return {}
    
    if theme_key not in keywords_data:
        print(f"⚠️ Theme key '{theme_key}' not found in keywords data")
        return {}
    
    theme_data = keywords_data[theme_key]
    
    # Ensure theme_data is a dictionary
    if not isinstance(theme_data, dict):
        print(f"⚠️ Theme data for '{theme_key}' is not a dictionary: {type(theme_data)}")
        return {}
    
    try:
        # Use safe extraction for all fields to prevent type errors
        return {
            'base_keyword': theme_key,
            'related_google': safe_extract_field(theme_data, 'related_searches', list, []),
            'long_tail_keywords': safe_extract_field(theme_data, 'long_tail_keywords', list, []),
            'search_intent': safe_extract_field(theme_data, 'search_intent', str, 'informational'),
            'suggested_titles': safe_extract_field(theme_data, 'suggested_titles', list, []),
            'h1': safe_extract_field(theme_data, 'h1', str, ''),
            'h2': safe_extract_field(theme_data, 'h2', list, []),
            'search_volume': safe_extract_field(theme_data, 'search_volume', dict, {}),
            'competition_level': safe_extract_field(theme_data, 'competition_level', str, 'unknown'),
            'primary_keywords': safe_extract_field(theme_data, 'primary_keywords', list, []),
            'database_keywords': safe_extract_field(theme_data, 'database_keywords', dict, {}),
            'opportunities': safe_extract_field(theme_data, 'opportunities', list, []),
            'high_volume_keywords': safe_extract_field(theme_data, 'high_volume_keywords', list, []),
            'low_difficulty_keywords': safe_extract_field(theme_data, 'low_difficulty_keywords', list, [])
        }
    except Exception as e:
        print(f"⚠️ Error generating semantic fields for '{theme_key}': {e}")
        return {}

def load_local_creative_outputs(brand_folder):
    """
    Load themes, seo_themes, brief_summaries and semantic fields from the specified brand folder.
    Returns a dictionary with all loaded data.
    """
    posts_folder = Path(brand_folder) / 'posts'
    
    # Check if posts folder exists
    if not posts_folder.exists():
        raise FileNotFoundError(f"Posts folder not found: {posts_folder}")
    
    loaded_data = {}
    
    # Load themes.py
    themes_file = posts_folder / 'themes.py'
    if themes_file.exists():
        try:
            # Read the file and extract the themes dictionary
            with open(themes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Execute the Python code to get the themes dictionary
            local_vars = {}
            exec(content, {}, local_vars)
            loaded_data['themes'] = local_vars.get('themes', {})
            
            # Extract macro_name from the same file
            loaded_data['macro_name'] = local_vars.get('macro_name', 'content_campaign')
            print(f"✅ Loaded themes and macro_name from {themes_file}")
        except Exception as e:
            print(f"⚠️ Error loading themes: {e}")
            loaded_data['themes'] = {}
            loaded_data['macro_name'] = 'content_campaign'
    else:
        print(f"⚠️ Themes file not found: {themes_file}")
        loaded_data['themes'] = {}
        loaded_data['macro_name'] = 'content_campaign'
    
    # Load seo_themes.py
    seo_themes_file = posts_folder / 'seo_themes.py'
    if seo_themes_file.exists():
        try:
            # Read the file and extract the seo_themes dictionary
            with open(seo_themes_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Execute the Python code to get the seo_themes dictionary
            local_vars = {}
            exec(content, {}, local_vars)
            loaded_data['seo_themes'] = local_vars.get('seo_themes', {})
            print(f"✅ Loaded seo_themes from {seo_themes_file}")
        except Exception as e:
            print(f"⚠️ Error loading seo_themes: {e}")
            loaded_data['seo_themes'] = {}
    else:
        print(f"⚠️ SEO themes file not found: {seo_themes_file}")
        loaded_data['seo_themes'] = {}
    
    # Load brief_summary.py
    brief_summary_file = posts_folder / 'brief_summary.py'
    if brief_summary_file.exists():
        try:
            # Read the file and extract the brief_summary dictionary
            with open(brief_summary_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Execute the Python code to get the brief_summary dictionary
            local_vars = {}
            exec(content, {}, local_vars)
            loaded_data['brief_summaries'] = local_vars.get('brief_summary', {})
            print(f"✅ Loaded brief_summaries from {brief_summary_file}")
        except Exception as e:
            print(f"⚠️ Error loading brief_summary: {e}")
            loaded_data['brief_summaries'] = {}
    else:
        print(f"⚠️ Brief summary file not found: {brief_summary_file}")
        loaded_data['brief_summaries'] = {}
    
    # Load products.py
    products_file = posts_folder / 'products.py'
    if products_file.exists():
        try:
            # Read the file and extract the products dictionary
            with open(products_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Execute the Python code to get the products dictionary
            local_vars = {}
            exec(content, {}, local_vars)
            loaded_data['products'] = local_vars.get('products', {})
            print(f"✅ Loaded products dictionary from {products_file}")
        except Exception as e:
            print(f"⚠️ Error loading products: {e}")
            loaded_data['products'] = {}
    else:
        print(f"⚠️ Products file not found: {products_file}")
        loaded_data['products'] = {}
    
    # Load keywords.py
    keywords_file = posts_folder / 'keywords.py'
    if keywords_file.exists():
        try:
            # Read the file and extract the keywords dictionary
            with open(keywords_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Execute the Python code to get the keywords dictionary
            local_vars = {}
            exec(content, {}, local_vars)
            loaded_data['keywords'] = local_vars.get('keywords', {})
            print(f"✅ Loaded keywords dictionary from {keywords_file}")
        except Exception as e:
            print(f"⚠️ Error loading keywords: {e}")
            loaded_data['keywords'] = {}
    else:
        print(f"⚠️ Keywords file not found: {keywords_file}")
        loaded_data['keywords'] = {}
    
    # Generate semantic fields based on loaded keywords data
    semantic_fields = {}
    seo_themes = safe_extract_field(loaded_data, 'seo_themes', dict, {})
    keywords = safe_extract_field(loaded_data, 'keywords', dict, {})
    
    # CRITICAL FIX: Handle different seo_themes structures and generate semantic fields
    if seo_themes:
        try:
            for title, seo_data in seo_themes.items():
                if not isinstance(title, str):
                    print(f"⚠️ Skipping non-string theme title: {type(title)}")
                    continue
                
                # Handle different seo_themes structures
                if isinstance(seo_data, str):
                    # String format (expected by semantic fields generation)
                    short_name = seo_data
                elif isinstance(seo_data, list):
                    # List format (from current seo_themes.py) - use first item as short name
                    short_name = seo_data[0] if seo_data else title
                else:
                    # Unknown format - use title as fallback
                    short_name = title
                
                # Generate semantic fields from keywords data if available
                if keywords and isinstance(keywords, dict):
                    title_semantics = generate_semantic_fields_from_keywords(title, keywords)
                    name_semantics = generate_semantic_fields_from_keywords(short_name, keywords)
                    
                    # For combined theme, try to find the best match in keywords
                    combined_theme = f"{title}: {short_name}"
                    combined_semantics = generate_semantic_fields_from_keywords(combined_theme, keywords)
                    
                    # If no combined match, use title semantics as fallback
                    if not combined_semantics:
                        combined_semantics = title_semantics

                    semantic_fields[title] = {
                        'summary': title_semantics,
                        'complete': name_semantics,
                        'combined': combined_semantics
                    }
                else:
                    # No keywords available - generate basic semantic fields
                    basic_semantics = {
                        'base_keyword': title,
                        'related_google': [title, short_name],
                        'long_tail_keywords': [f"{title} {short_name}", f"como usar {title}"],
                        'search_intent': 'informational',
                        'suggested_titles': [title, short_name],
                        'h1': f"Tudo sobre {title}",
                        'h2': [f"O que é {title}", f"Como usar {title}", f"Benefícios do {title}"]
                    }
                    
                    semantic_fields[title] = {
                        'summary': basic_semantics,
                        'complete': basic_semantics,
                        'combined': basic_semantics
                    }
                    
        except Exception as e:
            print(f"⚠️ Error generating semantic fields: {e}")
            semantic_fields = {}
    
    # Ensure semantic_fields is always a dictionary
    if not isinstance(semantic_fields, dict):
        print(f"⚠️ Semantic fields is not a dictionary: {type(semantic_fields)}")
        semantic_fields = {}
    
    # CRITICAL: Ensure semantic_fields is never empty - content generation requires it
    if not semantic_fields:
        print("⚠️ Warning: No semantic fields generated. Content generation may fail.")
        # Generate minimal semantic fields for each theme to prevent content generation failure
        themes = safe_extract_field(loaded_data, 'themes', dict, {})
        if themes:
            for title in themes.keys():
                if isinstance(title, str):
                    minimal_semantics = {
                        'base_keyword': title,
                        'related_google': [title],
                        'long_tail_keywords': [f"como usar {title}"],
                        'search_intent': 'informational',
                        'suggested_titles': [title],
                        'h1': f"Tudo sobre {title}",
                        'h2': [f"O que é {title}", f"Como usar {title}"]
                    }
                    
                    semantic_fields[title] = {
                        'summary': minimal_semantics,
                        'complete': minimal_semantics,
                        'combined': minimal_semantics
                    }

    loaded_data['semantic_fields'] = semantic_fields
    
    return loaded_data

def display_product_selector():

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