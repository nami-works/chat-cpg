import os
import re
import streamlit as st
import ast

from langchain.memory import ConversationBufferMemory
from pathlib import Path


# Function to parse creative outputs from model response
def parse_creative_outputs(resposta):
    st.write("Analyzing model response:", resposta)  # Debug output

    # Try to extract themes dictionary from response
    theme_pattern = re.search(r'themes\s*=\s*\{[^}]+\}', resposta, re.DOTALL)
    if theme_pattern:
        try:
            theme_text = theme_pattern.group(0)
            st.write("Theme text found:", theme_text)  # Debug output
            theme_dict = ast.literal_eval(theme_text.split('=')[1].strip())
            if isinstance(theme_dict, dict):
                st.session_state['themes'] = theme_dict
                st.session_state['adjustment_mode'] = False
                st.write("✅ Themes extracted successfully:", theme_dict)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting themes: {e}")
            st.write("Text found:", theme_pattern.group(0))  # Debug output

    # Try to extract seo_themes dictionary from response
    seo_theme_pattern = re.search(r'seo_themes\s*=\s*\{[^}]+\}', resposta, re.DOTALL)
    if seo_theme_pattern:
        try:
            seo_theme_text = seo_theme_pattern.group(0)
            st.write("SEO themes text found:", seo_theme_text)  # Debug output
            seo_theme_dict = ast.literal_eval(seo_theme_text.split('=')[1].strip())
            if isinstance(seo_theme_dict, dict):
                st.session_state['seo_themes'] = seo_theme_dict
                st.session_state['adjustment_mode'] = False
                st.write("✅ SEO themes extracted successfully:", seo_theme_dict)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting seo_themes: {e}")
            st.write("Text found:", seo_theme_pattern.group(0))  # Debug output

    # Try to extract macro_name from response
    macro_name_pattern = re.search(r'macro_name\s*=\s*["\']([^"\']+)["\']', resposta)
    if macro_name_pattern:
        try:
            macro_name = macro_name_pattern.group(1)  # Get the actual name without quotes
            st.session_state['macro_name'] = macro_name
            st.session_state['adjustment_mode'] = False
            st.write("✅ Macro name extracted successfully:", macro_name)  # Debug output
        except Exception as e:
            st.warning(f"Error interpreting macro_name: {e}")
            st.write("Text found:", macro_name_pattern.group(0))  # Debug output
    
    # Import translations
    from translations import LANG
    
    # Debug output for session state - MOVED TO EXPANDER
    with st.expander(LANG['technical_details_debug'], expanded=False):
        st.write("Current session state:", {
            'themes': st.session_state.get('themes'),
            'seo_themes': st.session_state.get('seo_themes'),
            'macro_name': st.session_state.get('macro_name')
        })
        
        # Also show the raw response for debugging if needed
        if st.checkbox(LANG['show_raw_response'], value=False):
            st.text_area(LANG['raw_response'], value=resposta, height=200, disabled=True)

def save_creative_outputs(brand_folder, themes, seo_themes):
    """
    Save theme files, seo_themes and semantic fields for the specified brand.
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

    # Generate basic semantic fields without external API calls
    semantic_fields = {}
    with open(posts_folder / 'semantic_fields.md', 'w', encoding='utf-8') as f:
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

            f.write(f"# {title}: {short_name}\n\n")
            f.write("## Related keywords\n")
            for item in basic_semantics['related_google']:
                f.write(f"- {item}\n")
            f.write("\n## Intent\n")
            f.write(f"- {basic_semantics['search_intent']}\n")
            f.write("\n## Suggested titles\n")
            for item in basic_semantics['suggested_titles']:
                f.write(f"- {item}\n")
            f.write("\n## Headers\n")
            f.write(f"**H1:** {basic_semantics['h1']}\n")
            for h2 in basic_semantics['h2']:
                f.write(f"- H2: {h2}\n")
            f.write("\n---\n\n")

    return semantic_fields
