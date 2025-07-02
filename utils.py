import os
import re
import streamlit as st
import ast

from langchain.memory import ConversationBufferMemory
from pathlib import Path

# Function to parse creative outputs from model response
def parse_creative_outputs(resposta):
    """
    Parse themes, seo_themes, and macro_name from LLM response.
    This function extracts Python dictionaries and variables from the response text.
    """
    
    # Try to extract themes dictionary from response
    # Improved pattern to handle multi-line dictionaries and various formatting
    theme_pattern = re.search(r'themes\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', resposta, re.DOTALL)
    if theme_pattern:
        try:
            theme_text = f"themes = {{{theme_pattern.group(1)}}}"
            # Clean up the text and try to evaluate it
            theme_dict = ast.literal_eval(theme_text.split('=')[1].strip())
            if isinstance(theme_dict, dict) and theme_dict:
                st.session_state['themes'] = theme_dict
                st.session_state['adjustment_mode'] = False
        except Exception:
            # Try alternative pattern for simpler cases
            try:
                simple_pattern = re.search(r'themes\s*=\s*(\{[^{}]*\})', resposta, re.DOTALL)
                if simple_pattern:
                    theme_dict = ast.literal_eval(simple_pattern.group(1))
                    if isinstance(theme_dict, dict) and theme_dict:
                        st.session_state['themes'] = theme_dict
                        st.session_state['adjustment_mode'] = False
            except Exception:
                pass

    # Try to extract seo_themes dictionary from response
    seo_theme_pattern = re.search(r'seo_themes\s*=\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', resposta, re.DOTALL)
    if seo_theme_pattern:
        try:
            seo_theme_text = f"seo_themes = {{{seo_theme_pattern.group(1)}}}"
            seo_theme_dict = ast.literal_eval(seo_theme_text.split('=')[1].strip())
            if isinstance(seo_theme_dict, dict) and seo_theme_dict:
                st.session_state['seo_themes'] = seo_theme_dict
                st.session_state['adjustment_mode'] = False
        except Exception:
            # Try alternative pattern for simpler cases
            try:
                simple_pattern = re.search(r'seo_themes\s*=\s*(\{[^{}]*\})', resposta, re.DOTALL)
                if simple_pattern:
                    seo_theme_dict = ast.literal_eval(simple_pattern.group(1))
                    if isinstance(seo_theme_dict, dict) and seo_theme_dict:
                        st.session_state['seo_themes'] = seo_theme_dict
                        st.session_state['adjustment_mode'] = False
            except Exception:
                pass

    # Try to extract macro_name from response
    macro_name_pattern = re.search(r'macro_name\s*=\s*["\']([^"\']+)["\']', resposta)
    if macro_name_pattern:
        try:
            macro_name = macro_name_pattern.group(1)
            st.session_state['macro_name'] = macro_name
            st.session_state['adjustment_mode'] = False
        except Exception:
            pass

def save_creative_outputs(brand_folder, themes, seo_themes, extrair_seo):
    """
    Save theme files, seo_themes and semantic fields for the specified brand.
    """
    posts_folder = Path(brand_folder) / 'posts'
    os.makedirs(posts_folder, exist_ok=True)

    # Save temas.py
    with open(posts_folder / 'themes.py', 'w', encoding='utf-8') as f:
        f.write("themes = {\n")
        for k, v in themes.items():
            f.write(f'    "{k}": "{v}",\n')
        f.write("}\n")

    # Save temas_seo.py
    with open(posts_folder / 'seo_themes.py', 'w', encoding='utf-8') as f:
        f.write("seo_themes = {\n")
        for k, v in seo_themes.items():
            f.write(f'    "{k}": "{v}",\n')
        f.write("}\n")

    # Save campos_semanticos.md
    semantic_fields = {}
    with open(posts_folder / 'semantic_fields.md', 'w', encoding='utf-8') as f:
        for titulo, nome_resumido in seo_themes.items():
            # Extract for complete title
            semantica_titulo = extrair_seo(titulo)
            # Extract for short name
            semantica_nome = extrair_seo(nome_resumido)
            tema_combinado = f"{titulo}: {nome_resumido}"
            semantica_combinada = extrair_seo(tema_combinado)

            semantic_fields[titulo] = {
                'resumido': semantica_titulo,
                'completo': semantica_nome,
                'combinado': semantica_combinada
            }

            f.write(f"# {titulo}: {nome_resumido}\n\n")
            f.write("## Related keywords\n")
            for item in semantica_titulo['relacionadas_google']:
                f.write(f"- {item}\n")
            for item in semantica_nome['relacionadas_google']:
                f.write(f"- {item}\n")
            f.write("\n## Intent\n")
            f.write(f"- {semantica_titulo['intencao_busca']}\n")
            f.write("\n## Suggested titles\n")
            for item in semantica_combinada['titulos_sugeridos']:
                f.write(f"- {item}\n")
            f.write("\n## Headers\n")
            f.write(f"**H1:** {semantica_titulo['h1']}\n")
            f.write(f"**H1:** {semantica_nome['h1']}\n")
            for h2 in semantica_titulo['h2']:
                f.write(f"- H2: {h2}\n")
            for h2 in semantica_nome['h2']:
                f.write(f"- H2: {h2}\n")
            f.write("\n---\n\n")

    return semantic_fields
