#imports

##complete modules
import os
import yaml
import locale

##renamed modules
import streamlit as st

##module functions
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from pathlib import Path

##internal functions
from utils import parse_creative_outputs, save_creative_outputs

# Get system language
system_lang = locale.getdefaultlocale()[0]

# UI text translations
UI_TEXT = {
    'en_US': {
        'functions_tab': 'Functions',
        'references_tab': 'References',
        'brands_tab': 'Brands',
        'llms_tab': 'LLMs',
        'choose_function': 'Choose function',
        'choose_reference': 'Choose reference',
        'choose_brand': 'Choose brand',
        'choose_llm': 'Choose LLM',
        'select_version': 'Select version',
        'restart': 'Restart',
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
        'brands_tab': 'Marcas',
        'llms_tab': 'LLMs',
        'choose_function': 'Escolha a função',
        'choose_reference': 'Escolha a referência',
        'choose_brand': 'Escolha a marca',
        'choose_llm': 'Escolha um LLM',
        'select_version': 'Selecione a versão',
        'restart': 'Reiniciar',
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
    tabs = st.tabs([LANG['functions_tab'], LANG['references_tab']])

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