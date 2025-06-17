#imports

##complete modules
import os
import locale
import yaml
import sys


##renamed modules
import streamlit as st

##module functions
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from pathlib import Path

#internal ChatCPG functions
from utils import parse_creative_outputs, save_creative_outputs

# Absolute path for importing locally created tools
tools_path = r'G:\Meu Drive\Pessoal\nAmI\ferramentas'

# Add to sys.path if not already present
if tools_path not in sys.path:
    sys.path.append(tools_path)

# Tools import
from extrator_seo import extrair_seo

load_dotenv()

base_dir = Path(__file__).resolve().parent.parent

def missing_outputs():
    """Check if we need to generate creative outputs."""
    return (
        'themes' not in st.session_state or 
        'seo_themes' not in st.session_state or 
        st.session_state.get('adjustment_mode', False)
    )

def process_creative_outputs():
    """
    Process the creative outputs (themes and seo_themes) and generate the content.
    This function is called when the user clicks the "Request content" button.
    """
    context = st.session_state.get('context', {})
    themes = st.session_state['themes']
    brand_id = context.get("brand_id")
    if not brand_id:
        st.warning("Could not determine brand to save themes.")
        return

    brand_folder = base_dir / 'z_brands' / brand_id
    seo_themes = st.session_state.get('seo_themes', {})
    
    # Save theme files, seo_themes and semantic fields
    semantic_fields = save_creative_outputs(brand_folder, themes, seo_themes, extrair_seo)

    inputs = {
        'style': context.get('style', ''),
        'brand': context.get('brand', ''),
        'products': context.get('products', ''),
        'blog': context.get('blog', ''),
        'benchmarks': context.get('benchmarks', ''),
        'format_recommendations': context.get('format_recommendations', ''),
        'themes': themes,
        'macro_name': st.session_state.get('macro_name'),
        'brand_folder': brand_folder,
        'semantic_fields': semantic_fields
    }

    try:
        from redacao.src.redacao_cpg.main import escrever
        escrever(inputs)
        st.success('✅ Content produced successfully!')
    except Exception as e:
        st.error(f"Error starting content production: {e}")

def handle_redacao_flow(chat_interaction, chain, memory):
    """
    Handle the redacao-specific chat flow.
    Uses the centralized chat_interaction function for UI.
    """
    if missing_outputs():
        # Get response using the centralized chat interaction
        response = chat_interaction('What is today\'s agenda?', chain, memory, key="initial_prompt")
        
        if response:
            # Process the response
            parse_creative_outputs(response)
            
            # If dictionaries weren't parsed, ask explicitly with format example
            if 'themes' not in st.session_state or 'seo_themes' not in st.session_state:
                format_prompt = '''
                Please generate the themes and seo_themes dictionaries again in the correct Python format.
                
                Example of expected format:

                themes = {
                    "Short summary 1": "Complete theme title 1",
                    "Short summary 2": "Complete theme title 2"
                }

                seo_themes = {
                    "Short summary 1": "Generic theme corresponding to theme 1",
                    "Short summary 2": "Generic theme corresponding to theme 2"
                }

                macro_name = "name_of_theme_set"
                '''
                response = chat_interaction(format_prompt, chain, memory, key="format_prompt")
                if response:
                    parse_creative_outputs(response)
            
            st.rerun()
    else:
        # Show action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            adjustments_button = st.button("🔴 Fazer ajustes", use_container_width=True, disabled=False)
            if adjustments_button:
                st.session_state['adjustment_mode'] = True

        with col2:
            request_button = st.button('🟢 Solicitar conteúdo', use_container_width=True, disabled=False)
            if request_button:
                process_creative_outputs()
