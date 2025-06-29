#imports

##complete modules
import os
import yaml
import locale
import json
import re
import spacy

##renamed modules
import streamlit as st

##module functions
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI, OpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from pathlib import Path
from typing import Dict, List, Optional, Tuple

##internal functions
from utils import parse_creative_outputs, save_creative_outputs
import file_reader

# Loading spaCy model for text analysis
try:
    nlp = spacy.load("pt_core_news_md")
except OSError:
    st.warning("⚠️ spaCy Portuguese model not found. Please install it with: python -m spacy download pt_core_news_md")
    nlp = None

# Get system language
system_lang = locale.getdefaultlocale()[0]

# UI text translations
UI_TEXT = {
    'en_US': {
        'functions_tab': 'Functions',
        'references_tab': 'References',
        'knowledge_tab': 'Add Knowledge',
        'brands_tab': 'Brands',
        'llms_tab': 'LLMs',
        'choose_function': 'Choose function',
        'choose_reference': 'Choose reference',
        'choose_brand': 'Choose brand',
        'choose_llm': 'Choose LLM',
        'select_version': 'Select version',
        'restart': 'Restart',
        'upload_files': 'Upload Files',
        'enter_directory': 'Enter directory path to scan:',
        'send_button': 'Send',
        'start_scanning': 'Start Scanning',
        'enter_path_warning': '⚠️ Please enter a directory path',
        'no_files_warning': '⚠️ No files found in directory: {}',
        'processing_files': 'Processing files... ({}/{})',
        'processing_completed': '✅ Processing completed!',
        'file_upload_tab': 'File Upload',
        'directory_scan_tab': 'Directory Scan',
        'missing_files': "Incomplete files for brand '{}'",
        'missing_brand_info': "Oops! Some brand information is missing. Check your inputs!",
        'no_reference': "No reference loaded.",
        'file_not_found': "File not found: {}",
        'empty_guidelines': "Guidelines file is empty",
        'guidelines_error': "Error loading guidelines: {}",
        'no_guidelines': "No specific guidelines loaded.",
        'reference_not_found': "Reference file not found for: {}",
        'no_specific_reference': "No specific references loaded.",
        'chatcpg_not_loaded': "ChatCPG is not loaded yet",
        'click_to_load': "Click here to load!",
        'no_api_key': "⚠️ No API Key defined.",
        'chat_placeholder': "Type your message here..."
    },
    'pt_BR': {
        'functions_tab': 'Funções',
        'references_tab': 'Referências',
        'knowledge_tab': 'Adicionar conhecimento',
        'brands_tab': 'Marcas',
        'llms_tab': 'LLMs',
        'choose_function': 'Escolha a função',
        'choose_reference': 'Escolha a referência',
        'choose_brand': 'Escolha a marca',
        'choose_llm': 'Escolha um LLM',
        'select_version': 'Selecione a versão',
        'restart': 'Reiniciar',
        'upload_files': 'Carregar Arquivos',
        'enter_directory': 'Digite o caminho do diretório para escanear:',
        'send_button': 'Enviar',
        'start_scanning': 'Iniciar Escaneamento',
        'enter_path_warning': '⚠️ Por favor, digite um caminho de diretório',
        'no_files_warning': '⚠️ Nenhum arquivo encontrado no diretório: {}',
        'processing_files': 'Processando arquivos... ({}/{})',
        'processing_completed': '✅ Processamento concluído!',
        'file_upload_tab': 'Upload de Arquivos',
        'directory_scan_tab': 'Escaneamento de Diretório',
        'missing_files': "Arquivos incompletos para a marca '{}'",
        'missing_brand_info': "Ops! Ainda falta alguma informação da marca. Verifique seus inputs!",
        'no_reference': "Sem referência carregada.",
        'file_not_found': "Arquivo não encontrado: {}",
        'empty_guidelines': "Arquivo de orientações está vazio",
        'guidelines_error': "Erro ao carregar orientações: {}",
        'no_guidelines': "Sem orientações específicas carregadas.",
        'reference_not_found': "Arquivo de referência não encontrado para: {}",
        'no_specific_reference': "Sem referências específicas carregadas.",
        'chatcpg_not_loaded': "O ChatCPG ainda não foi carregado",
        'click_to_load': "Clique aqui para carregar!",
        'no_api_key': "⚠️ Nenhuma API Key foi definida.",
        'chat_placeholder': "Digite sua mensagem aqui..."
    }
}

# Default to English if system language not supported
LANG = UI_TEXT.get(system_lang, UI_TEXT['en_US'])

load_dotenv()

client_brands = {
    'GE Beauty': 'gebeauty',
}

available_functions = {
    'Redação CPG': 'redacao',
    'Oráculo CPG': 'oraculo',
}

available_llms = {
    'OpenAI': {'Versions': {
        'GPT-4o Mini': 'gpt-4o-mini',
        'GPT-4o': 'gpt-4o',
        'GPT-3.5 Turbo': 'gpt-3.5-turbo',
        'GPT-3.5 Turbo 16K': 'gpt-3.5-turbo-16k',
        'GPT-3.5 Instruct': 'gpt-3.5-turbo-instruct',
        },
        'Chain': ChatOpenAI},
    'Groq':{
        'Versions': {
            'LLaMA 3 70B': 'llama3-groq-70b-8192-tool-use-preview',
            'LLaMA 3 8B': 'llama3-groq-8b-8192-tool-use-preview',
            'LLaMA 3.3 70B': 'llama-3.3-70b-versatile',
            'LLaMA 3.1 8B': 'llama-3.1-8b-instant',
            'Compound Beta': 'compound-beta',
        },
        'Chain': ChatGroq},
}

available_refs = {
    'Ramping your Brand': 'ryb',
    'The Great CEO Within': 'tgcw',
}

base_dir = Path(__file__).resolve().parent

def extract_relevant_information(text: str) -> Tuple[str, Dict, List[str]]:
    """
    Extracts relevant information from text using NLP and LLM.
    
    Parameters:
    text (str): Original text extracted from document
    
    Returns:
    Tuple[str, Dict, List[str]]: (summary, key_entities, main_topics)
    """
    # Initialize LLM for summarization
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    
    # Split text into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    text_chunks = text_splitter.split_text(text)
    
    # Generate summary using LangChain
    summarization_chain = load_summarize_chain(llm, chain_type="map_reduce")
    text_summary = summarization_chain.run(text_chunks)
    
    # Extract key entities using spaCy (if available)
    extracted_entities = {}
    if nlp:
        document = nlp(text)
        for entity in document.ents:
            if entity.label_ not in extracted_entities:
                extracted_entities[entity.label_] = []
            if entity.text not in extracted_entities[entity.label_]:
                extracted_entities[entity.label_].append(entity.text)
    
    # Identify main topics using keywords and phrases
    identified_topics = []
    if nlp:
        document = nlp(text)
        for sentence in document.sents:
            if any(token.pos_ in ["NOUN", "PROPN"] for token in sentence):
                identified_topics.append(sentence.text.strip())
    
    return text_summary, extracted_entities, identified_topics[:5]  # Limit to 5 main topics

def filter_categories(categories: dict) -> dict:
    """
    Filters categories by removing noise terms.

    Parameters:
    categories (dict): Original categories dictionary.

    Returns:
    dict: Filtered dictionary.
    """
    filtered_dict = {}

    for term, label in categories.items():
        cleaned_term = term.strip()

        # Noise exclusion rules
        if (
            re.search(r'Página \d+', cleaned_term) or
            re.search(r'Click to', cleaned_term) or
            re.search(r'Signed By', cleaned_term) or
            re.search(r'Audit Trail', cleaned_term) or
            re.search(r'User Reference Id', cleaned_term) or
            re.search(r'\bIP\b', cleaned_term) or
            len(cleaned_term) <= 2 or
            re.match(r'^[a-f0-9]{16,}$', cleaned_term, re.IGNORECASE)
        ):
            continue  # Skip noise terms

        filtered_dict[cleaned_term] = label

    return filtered_dict

def update_knowledge_base(result: str, metadata: dict, save_path=None):
    """
    Updates the consolidated knowledge base in a .md file with the new processed result,
    applying noise filtering on categories and organizing relevant information.

    Parameters:
    result (str): Extracted text.
    metadata (dict): Document associated metadata.
    save_path (str): Path to the consolidated knowledge base file.
    """
    try:
        # Extract key information
        text_summary, entity_list, topic_list = extract_relevant_information(result)
        
        # Filter out noise from categories
        filtered_entity_list = {k: filter_categories({e: k for e in v}) for k, v in entity_list.items()}
        
        # Default save path if not provided
        if save_path is None:
            save_path = base_dir / 'oraculo' / 'conhecimento' / 'knowledge_base.md'
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True) if os.path.dirname(save_path) else None

        with open(save_path, 'a', encoding='utf-8') as knowledge_file:
            knowledge_file.write(f"\n## Document: {metadata.get('source', 'unknown')}\n\n")
            
            # Write summary section
            knowledge_file.write(f"### Summary:\n{text_summary}\n\n")
            
            # Write topics section
            knowledge_file.write("### Main Topics:\n")
            for topic in topic_list:
                knowledge_file.write(f"- {topic}\n")
            knowledge_file.write("\n")
            
            # Write entities section
            knowledge_file.write(f"### Entities:\n```json\n{json.dumps(filtered_entity_list, indent=2, ensure_ascii=False)}\n```\n\n")
            
            # Write full content section
            knowledge_file.write(f"### Full Content:\n<details>\n<summary>Expand</summary>\n\n{result}\n\n</details>\n\n---\n")
        
        print(f"✅ Knowledge base updated with document: {metadata.get('source', 'unknown')}")
    except Exception as error:
        print(f"❌ Error updating knowledge base: {error}")

def scan_directory(directory_path: str) -> List[str]:
    """
    Scans the specified directory and returns a list of all files found.

    Parameters:
    directory_path (str): Path of the directory to be scanned.

    Returns:
    List[str]: A list with complete paths of found files.
    """
    found_files = []
    try:
        for current_folder, _, folder_files in os.walk(directory_path):
            for file in folder_files:
                found_files.append(os.path.join(current_folder, file))
    except Exception as error:
        print(f"❌ Error in scan_directory function: {error}")
    return found_files

def escape_braces(text):
    if isinstance(text, str):
        return text.replace("{", "{{").replace("}", "}}")
    return text

def load_brand_files(brand_name: str):
    brand_folder = base_dir / 'z_brands' / brand_name

    file_registration = brand_folder / 'registration.yaml'
    if not file_registration.exists():
        raise FileNotFoundError(LANG['missing_files'].format(brand_name))
    file_style = brand_folder / 'style.md'
    file_products = brand_folder / 'products.md'
    file_format = brand_folder / 'format_recommendations.md'
    
    if not file_registration.exists() or not file_style.exists() or not file_products.exists():
        raise FileNotFoundError(LANG['missing_files'].format(brand_name))

    with open(file_registration, 'r', encoding='utf-8') as f:
        registration = yaml.safe_load(f)

    with open(file_style, 'r', encoding='utf-8') as f:
        style = f.read()

    with open(file_products, 'r', encoding='utf-8') as f:
        products = f.read()

    with open(file_format, 'r', encoding='utf-8') as f:
        format_recommendations = f.read()

    return registration['brand'], registration['blog'], registration['benchmarks'], style, products, format_recommendations

intro = ConversationBufferMemory()

def load_model(chosen_provider, version_id, api_key):
    context = st.session_state.get('context', {})

    brand = context.get('brand', '')
    blog = context.get('blog', '')
    benchmarks = context.get('benchmarks', '')
    style = context.get('style', '')
    products = context.get('products', '')
    
    if not all([brand, blog, benchmarks, style, products]):
        st.error(LANG['missing_brand_info'])
        st.stop()

    guidelines = st.session_state.get('guidelines', '...')
    reference = st.session_state.get('reference', LANG['no_reference'])

    prompt = f'''
    You have several information about the user's business:
    - {brand}
    - {products}
    - {style}
    - content available at their {blog}
    - {benchmarks}
    
    Besides that, you've been given a detailed set of {guidelines} for this specific interaction.
    You must know everything about the business you're partnering with, and use
    {reference} as your main reference of knowledge and best practices to work with.

    ####
    {st.session_state.get('result', '')}
    ####

    Use all of that as the main ground for all your iterations.
    '''

    template = ChatPromptTemplate.from_messages([
        ('system', prompt),
        ('placeholder', '{chat_history}'),
        ('user', '{input}')
    ])

    chat = available_llms[chosen_provider]['Chain'](model=version_id, api_key=api_key)
    chain = template | chat
    st.session_state['Chain'] = chain

st.set_page_config(
    page_title='ChatCPG',
    page_icon='🦊'
    )

def sidebar_menu():
    tabs = st.tabs([LANG['functions_tab'], LANG['references_tab'], LANG['knowledge_tab']])

    with tabs[0]:
        selected_function = st.selectbox(LANG['choose_function'], 
                                        available_functions.keys())
        selected_function_id = available_functions[selected_function]
        st.session_state['chosen_function'] = selected_function_id
        
        base_dir = Path(__file__).resolve().parent
        file_guidelines = base_dir / selected_function_id / 'guidelines.md'
              
        try:
            if not file_guidelines.exists():
                raise FileNotFoundError(LANG['file_not_found'].format(file_guidelines))
                
            with open(file_guidelines, 'r', encoding='utf-8') as f:
                guidelines = f.read()
                if not guidelines.strip():
                    raise ValueError(LANG['empty_guidelines'])
                st.session_state['guidelines'] = escape_braces(guidelines)
        
        except (FileNotFoundError, ValueError) as e:
            st.error(LANG['guidelines_error'].format(str(e)))
            st.session_state['guidelines'] = LANG['no_guidelines']

    with tabs[1]:
        selected_ref = st.selectbox(LANG['choose_reference'], 
                                     available_refs.keys())
        selected_ref_id = available_refs[selected_ref]
        st.session_state['selected_ref'] = selected_ref_id

        file_reference = base_dir / 'z_refs'/ f'{selected_ref_id}.md'

        try:
            with open(file_reference, 'r', encoding='utf-8') as f:
                reference = f.read()
                st.session_state['reference'] = reference
        
        except FileNotFoundError:
            st.warning(LANG['reference_not_found'].format(selected_ref_id))
            st.session_state['reference'] = LANG['no_specific_reference']

    with tabs[2]:
        st.subheader(LANG['knowledge_tab'])
        
        # Create sub-tabs for file upload and directory scanning
        upload_tabs = st.tabs([LANG['file_upload_tab'], LANG['directory_scan_tab']])
        
        with upload_tabs[0]:
            st.write("**Upload individual files to the knowledge base:**")
            uploaded_files = st.file_uploader(
                "Choose files", 
                accept_multiple_files=True,
                type=['pdf', 'txt', 'doc', 'docx', 'csv', 'xlsx', 'json', 'md']
            )
            
            if uploaded_files and st.button(LANG['send_button'], key="upload_button"):
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                total_files = len(uploaded_files)
                processed_files = 0
                
                for uploaded_file in uploaded_files:
                    try:
                        progress_text.text(f"{LANG['processing_files'].format(processed_files + 1, total_files)}")
                        
                        # Process the uploaded file
                        processed_result = file_reader.load_input(uploaded_file, uploaded_file.name)
                        file_metadata = {"source": uploaded_file.name}
                        update_knowledge_base(processed_result, file_metadata)
                        
                        processed_files += 1
                        progress_bar.progress(processed_files / total_files)
                        
                    except Exception as error:
                        st.error(f"❌ Error processing file {uploaded_file.name}: {error}")
                
                progress_text.text(LANG['processing_completed'])
                st.success(f"✅ Successfully processed {processed_files} files!")
        
        with upload_tabs[1]:
            st.write("**Scan a directory and process all compatible files:**")
            directory_path = st.text_input(LANG['enter_directory'])
            
            if st.button(LANG['send_button'], key="directory_button"):
                if not directory_path:
                    st.warning(LANG['enter_path_warning'])
                else:
                    try:
                        found_files = scan_directory(directory_path)
                        
                        if not found_files:
                            st.warning(LANG['no_files_warning'].format(directory_path))
                        else:
                            progress_bar = st.progress(0)
                            progress_text = st.empty()
                            
                            total_files = len(found_files)
                            processed_files = 0
                            successful_files = 0
                            
                            for file_path in found_files:
                                try:
                                    progress_text.text(f"{LANG['processing_files'].format(processed_files + 1, total_files)}")
                                    
                                    # Try to process the file
                                    with open(file_path, 'rb') as f:
                                        processed_result = file_reader.load_input(f, file_path)
                                    
                                    file_metadata = {"source": file_path}
                                    update_knowledge_base(processed_result, file_metadata)
                                    successful_files += 1
                                    
                                except Exception as error:
                                    st.warning(f"⚠️ Skipped file {file_path}: {error}")
                                
                                processed_files += 1
                                progress_bar.progress(processed_files / total_files)
                            
                            progress_text.text(LANG['processing_completed'])
                            st.success(f"✅ Successfully processed {successful_files} out of {total_files} files!")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing directory: {e}")

    # Set default brand (GE Beauty)
    brand_id = 'gebeauty'
    try:
        brand, blog, benchmarks, style, products, format_recommendations = load_brand_files(brand_id)
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    st.session_state['context'] = {
        'brand': brand,
        'brand_id': brand_id,
        'blog': blog,
        'benchmarks': benchmarks,
        'style': style,
        'products': products,
        'format_recommendations': format_recommendations,
    }

    # Set default LLM (GPT-4o Mini)
    chosen_provider = 'OpenAI'
    version_id = 'gpt-4o-mini'
    api_key_env = os.getenv('OPENAI_API_KEY')
    api_key = api_key_env
    st.session_state[f'api_key_{chosen_provider}'] = api_key

    if st.button(LANG['restart'], use_container_width=True):
        st.session_state['memory'] = intro

def handle_chat_interaction(prompt_message: str, chain, memory, key: str = "main_chat"):
    interaction = st.chat_input(LANG['chat_placeholder'], key=key)
    if not interaction:
        return None
        
    chat = st.chat_message('human', avatar='👤')
    chat.markdown(interaction)

    chat = st.chat_message('ai', avatar='🦊')
    response = chat.write_stream(
        chain.stream({
            'input': interaction,
            'chat_history': memory.buffer_as_messages
        })
    )

    if response:
        memory.chat_memory.add_user_message(interaction)
        memory.chat_memory.add_ai_message(response)
        st.session_state['memory'] = memory
        return response
    
    return None

def chat_cpg():
    st.header('🦊 ChatCPG',divider='red')
    st.subheader('Bem-vindo ao ChatCPG da GE Beauty!')
    st.write("""
    ChatCPG é seu assistente virtual para criar conteúdo no tom de voz GE Beauty! Vamos começar? 💛
    """)
    chosen_function = st.session_state.get('chosen_function')
    
    with st.sidebar:
        sidebar_menu()
    
    if 'Chain' not in st.session_state:
        context = st.session_state.get('context', {})
        chosen_provider = 'OpenAI' if 'api_key_OpenAI' in st.session_state else 'Groq'
        version_id = st.session_state.get('version_id', 'gpt-4o')
        api_key = st.session_state.get(f'api_key_{chosen_provider}', None)

    chain = st.session_state.get('Chain')

    if chain is None:
        st.error(LANG['chatcpg_not_loaded'])
        if st.button(LANG['click_to_load'], use_container_width=True):
            context = st.session_state.get('context', {})
            chosen_provider = 'OpenAI' if 'api_key_OpenAI' in st.session_state else 'Groq'
            version_id = st.session_state.get('version_id', 'gpt-4o')
            api_key = st.session_state.get(f'api_key_{chosen_provider}', None)

            if not api_key:
                st.warning(LANG['no_api_key'])
                st.stop()

            load_model(chosen_provider, version_id, api_key)
            st.rerun()
        st.stop()

    memory = st.session_state.get('memory', intro)
    if memory:
        for message in memory.buffer_as_messages:
            chat = st.chat_message(message.type, avatar='👤' if message.type == 'human' else '🦊')
            chat.markdown(message.content)

    if chosen_function == 'redacao':
        from redacao.redacao import handle_redacao_flow
        handle_redacao_flow(handle_chat_interaction, chain, memory)
    elif chosen_function == 'oraculo':
        from oraculo.oraculo import handle_oraculo_flow
        handle_oraculo_flow(handle_chat_interaction, chain, memory)

if __name__ == "__main__":
    chat_cpg()