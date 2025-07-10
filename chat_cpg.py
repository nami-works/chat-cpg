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
from langchain.prompts import ChatPromptTemplate
from pathlib import Path

##internal functions
from utils import parse_creative_outputs, save_creative_outputs
from file_reader import load_input

# Get system language
system_lang = locale.getdefaultlocale()[0]

# UI text translations
UI_TEXT = {
    'en_US': {
        'functions_tab': 'Functions',
        'references_tab': 'References',
        'brands_tab': 'Brands',
        'llms_tab': 'LLMs',
        'knowledge_tab': 'Add Knowledge',
        'choose_function': 'Choose function',
        'choose_reference': 'Choose reference',
        'choose_brand': 'Choose brand',
        'choose_llm': 'Choose LLM',
        'select_version': 'Select version',
        'load': 'Load',
        'upload_files': 'Upload files to add to knowledge base',
        'additional_context': 'Additional context about the files',
        'context_placeholder': 'Provide additional context about these files...',
        'send_knowledge': 'Send to Knowledge Base',
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
        'chat_placeholder': "Type your message here...",
        'knowledge_success': "✅ Files successfully added to knowledge base!",
        'knowledge_error': "❌ Error processing files: {}",
        'no_files_selected': "⚠️ Please select files to upload"
    },
    'pt_BR': {
        'functions_tab': 'Funções',
        'references_tab': 'Referências',
        'brands_tab': 'Marcas',
        'llms_tab': 'LLMs',
        'knowledge_tab': 'Adicionar Conhecimento',
        'choose_function': 'Escolha a função',
        'choose_reference': 'Escolha a referência',
        'choose_brand': 'Escolha a marca',
        'choose_llm': 'Escolha um LLM',
        'select_version': 'Selecione a versão',
        'load': 'Carregar',
        'upload_files': 'Carregue arquivos para adicionar à base de conhecimento',
        'additional_context': 'Contexto adicional sobre os arquivos',
        'context_placeholder': 'Forneça contexto adicional sobre estes arquivos...',
        'send_knowledge': 'Enviar para Base de Conhecimento',
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
        'chat_placeholder': "Digite sua mensagem aqui...",
        'knowledge_success': "✅ Arquivos adicionados com sucesso à base de conhecimento!",
        'knowledge_error': "❌ Erro ao processar arquivos: {}",
        'no_files_selected': "⚠️ Por favor, selecione arquivos para carregar"
    }
}

# Function-specific context configurations
FUNCTION_CONTEXTS = {
    'oraculo': {
        'title': '🦊 ChatCPG | Copiloto',
        'subtitle': 'Bem-vindo ao ChatCPG da GE Beauty!',
        'description': """
        Esse é o assistente inteligente da GE Beauty para tarefas do dia-a-dia!
        Aqui você pode:\n
        • Fazer diversas perguntas e pedir ajuda para questões específicas\n
        • Pesquisar informações específicas da empresa\n
        • Obter respostas rápidas e precisas\n
        • Consultar documentos e políticas\n
        • Acessar dados históricos e relatórios\n
        \n\n
        Como posso te ajudar hoje? 🫡
        """,
        'icon': '🔮'
    },
    'redacao': {
        'title': '🦊 ChatCPG | Copywriter',
        'subtitle': 'Bem-vindo à Redação da GE Beauty!',
        'description': """
        Esse é o assistente especializado para criar conteúdo no tom de voz GE Beauty!
        Aqui você pode:\n
        • Gerar temas e briefings para blog posts\n
        • Criar mensagens personalizadas baseadas nas categorias de RFM\n
        • Desenvolver campanhas de email marketing\n
        • Adaptar conteúdo para diferentes canais\n
        \n\n
        Vamos começar? 💛
        """,
        'icon': '✍️'
    },
    'geocommerce': {
        'title': '🗺️ ChatCPG | GeoCommerce',
        'subtitle': 'Bem-vindo ao GeoCommerce da GE Beauty!',
        'description': """
        Esse é o sistema de análise geográfica e insights de e-commerce da GE Beauty!
        Aqui você pode:\n
        • Analisar dados de vendas por região\n
        • Visualizar performance geográfica dos produtos\n
        • Identificar oportunidades de mercado\n
        • Integrar dados do Shopify com análises geográficas\n
        \n\n
        Conecte-se ao Shopify para começar! 🛍️
        """,
        'icon': '🗺️'
    },
}

def get_function_context(function_id):
    """
    Get dynamic context based on selected function
    
    Args:
        function_id: The selected function identifier
        
    Returns:
        dict: Context information for the function
    """
    default_context = {
        'title': '🦊 ChatCPG',
        'subtitle': 'Bem-vindo ao ChatCPG da GE Beauty!',
        'description': """
        ChatCPG é seu assistente virtual para trabalhar com a GE Beauty! 
        Selecione uma função na barra lateral para começar. 💛
        """,
        'icon': '🦊'
    }
    
    return FUNCTION_CONTEXTS.get(function_id, default_context)

# Default to English if system language not supported
LANG = UI_TEXT.get(system_lang, UI_TEXT['en_US'])

load_dotenv()

client_brands = {
    'GE Beauty': 'gebeauty',
}

available_functions = {
    'Copiloto': 'oraculo',
    'Copywriter': 'redacao',
    'GeoCommerce': 'geocommerce',
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
}

base_dir = Path(__file__).resolve().parent

def escape_braces(text):
    if isinstance(text, str):
        return text.replace("{", "{{").replace("}", "}}")
    return text

def process_knowledge_files(uploaded_files, additional_context=""):
    """
    Process uploaded files and add them to the knowledge base.
    
    Args:
        uploaded_files: List of uploaded files from Streamlit
        additional_context: Additional context provided by the user
    """
    try:
        # Get the brand context to determine where to save the knowledge
        context = st.session_state.get('context', {})
        brand_id = context.get('brand_id', 'gebeauty')
        
        # Define knowledge base path
        knowledge_base_path = base_dir / 'z_brands' / brand_id / 'knowledge.md'
        
        # Ensure the directory exists
        knowledge_base_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            try:
                # Load and process the file content
                file_content = load_input(uploaded_file, uploaded_file.name)
                
                # Create entry metadata
                file_metadata = {
                    'source': uploaded_file.name,
                    'type': uploaded_file.type,
                    'additional_context': additional_context
                }
                
                # Update knowledge base
                update_knowledge_base_entry(file_content, file_metadata, knowledge_base_path)
                
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
                continue
                
    except Exception as e:
        raise Exception(f"Failed to process knowledge files: {str(e)}")

def update_knowledge_base_entry(content, metadata, knowledge_base_path):
    """
    Update the knowledge base with a new entry.
    
    Args:
        content: The processed file content
        metadata: File metadata including source, type, and context
        knowledge_base_path: Path to the knowledge base file
    """
    try:
        # Create the knowledge base file if it doesn't exist
        if not knowledge_base_path.exists():
            with open(knowledge_base_path, 'w', encoding='utf-8') as f:
                f.write("# Knowledge Base\n\n")
        
        # Append new entry to knowledge base
        with open(knowledge_base_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## Document: {metadata.get('source', 'unknown')}\n\n")
            
            # Add additional context if provided
            if metadata.get('additional_context'):
                f.write(f"### Context:\n{metadata['additional_context']}\n\n")
            
            # Add file metadata
            f.write(f"### Metadata:\n")
            f.write(f"- **Source**: {metadata.get('source', 'unknown')}\n")
            f.write(f"- **Type**: {metadata.get('type', 'unknown')}\n\n")
            
            # Add the content
            f.write(f"### Content:\n<details>\n<summary>Expand</summary>\n\n{content}\n\n</details>\n\n---\n")
            
    except Exception as e:
        raise Exception(f"Failed to update knowledge base: {str(e)}")

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

    # Always load the correct guidelines for the selected function
    chosen_function = st.session_state.get('chosen_function', 'oraculo')
    base_dir = Path(__file__).resolve().parent
    file_guidelines = base_dir / chosen_function / 'guidelines.md'
    
    try:
        if not file_guidelines.exists():
            raise FileNotFoundError(LANG['file_not_found'].format(file_guidelines))
            
        with open(file_guidelines, 'r', encoding='utf-8') as f:
            guidelines = f.read()
            if not guidelines.strip():
                raise ValueError(LANG['empty_guidelines'])
            guidelines = escape_braces(guidelines)
    
    except (FileNotFoundError, ValueError) as e:
        st.error(LANG['guidelines_error'].format(str(e)))
        guidelines = LANG['no_guidelines']

    reference = st.session_state.get('reference', LANG['no_reference'])
    
    # Load knowledge base if it exists
    knowledge_base = ""
    context = st.session_state.get('context', {})
    brand_id = context.get('brand_id', 'gebeauty')
    knowledge_base_path = base_dir / 'z_brands' / brand_id / 'knowledge.md'
    
    if knowledge_base_path.exists():
        try:
            with open(knowledge_base_path, 'r', encoding='utf-8') as f:
                knowledge_base = f.read()
        except Exception as e:
            st.warning(f"Could not load knowledge base: {e}")

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

    {"Additional Knowledge Base:" if knowledge_base else ""}
    {knowledge_base}

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
    tabs = st.tabs([LANG['functions_tab'], LANG['knowledge_tab']])

    with tabs[0]:
        selected_function = st.selectbox(LANG['choose_function'], 
                                        available_functions.keys())
        selected_function_id = available_functions[selected_function]
        st.session_state['chosen_function'] = selected_function_id
        
        if st.button(LANG['load'], use_container_width=True):
            st.session_state['memory'] = intro
            # Load model when button is clicked
            context = st.session_state.get('context', {})
            chosen_provider = 'OpenAI' if 'api_key_OpenAI' in st.session_state else 'Groq'
            version_id = st.session_state.get('version_id', 'gpt-4o-mini')
            api_key = st.session_state.get(f'api_key_{chosen_provider}', None)
            
            if api_key:
                load_model(chosen_provider, version_id, api_key)
                st.rerun()
            else:
                st.warning(LANG['no_api_key'])

    with tabs[1]:
        # Knowledge tab
        st.write(LANG['upload_files'])
        uploaded_files = st.file_uploader(
            "Choose files", 
            accept_multiple_files=True,
            type=['pdf', 'txt', 'doc', 'docx', 'md', 'csv', 'json']
        )
        
        # Additional context input field
        additional_context = st.text_area(
            LANG['additional_context'],
            placeholder=LANG['context_placeholder'],
            height=100
        )
        
        # Send button (removed load button as requested)
        if st.button(LANG['send_knowledge'], use_container_width=True):
            if not uploaded_files:
                st.warning(LANG['no_files_selected'])
            else:
                try:
                    # Process uploaded files and add to knowledge base
                    process_knowledge_files(uploaded_files, additional_context)
                    st.success(LANG['knowledge_success'])
                    st.rerun()
                except Exception as e:
                    st.error(LANG['knowledge_error'].format(str(e)))

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
    chosen_function = st.session_state.get('chosen_function')
    
    # Get dynamic context based on selected function
    context_info = get_function_context(chosen_function)
    
    # Display dynamic header and content
    st.header(context_info['title'], divider='red')
    st.subheader(context_info['subtitle'])
    st.write(context_info['description'])
    
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
    elif chosen_function == 'geocommerce':
        from geocommerce.geocommerce_shopify import GeoCommerceShopifyApp
        app = GeoCommerceShopifyApp()
        app.render_geocommerce_content()

if __name__ == "__main__":
    chat_cpg()