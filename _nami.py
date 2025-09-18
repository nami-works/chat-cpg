#imports

##complete modules
import os
import yaml
import locale
import time

##renamed modules
import streamlit as st

##module functions
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pathlib import Path

##internal functions
from chats.seo_lab.utils import parse_creative_outputs, save_creative_outputs
from tools.file_reader import load_input
from chats.copilot.context import COPILOT_CONTEXT
from chats.seo_lab.context import SEO_LAB_CONTEXT
from chats.seo_lab._seo_lab import seo_lab_sidebar
from chats.crm_lab.context import CRM_LAB_CONTEXT
from chats.insighter.context import INSIGHTER_CONTEXT
from tools.geocommerce.context import GEOCOMMERCE_CONTEXT

# Import centralized translations
from translations import LANG

# Function-specific context configurations
FUNCTION_CONTEXTS = {
    'copilot': COPILOT_CONTEXT,
    'seo_lab': SEO_LAB_CONTEXT,  # Use SEO lab context
    'crm_lab': CRM_LAB_CONTEXT,  # Use CRM Lab context
    'insighter': INSIGHTER_CONTEXT,
    'geocommerce': GEOCOMMERCE_CONTEXT,
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
        'title': '🦊 Nami',
        'subtitle': {
            'pt_BR': 'Bem-vindo ao Nami!',
            'en_US': 'Welcome to Nami!'
        },
        'description': {
            'pt_BR': """
            Nami é seu assistente virtual inteligente! 
            Selecione uma função na barra lateral para começar. 💛
            """,
            'en_US': """
            Nami is your intelligent virtual assistant! 
            Select a function in the sidebar to get started. 💛
            """
        },
        'icon': '🦊',
        'chat_enabled': False,
        'how_to_use_col1': {
            'pt_BR': """
            Selecione uma função na barra lateral para começar a usar o Nami.
            """,
            'en_US': """
            Select a function in the sidebar to start using Nami.
            """
        },
        'how_to_use_col2': {
            'pt_BR': """
            Cada função tem recursos específicos para diferentes necessidades.
            """,
            'en_US': """
            Each function has specific features for different needs.
            """
        }
    }
    
    context = FUNCTION_CONTEXTS.get(function_id, default_context)
    
    # Get the current language from system
    import locale
    system_lang = locale.getdefaultlocale()[0]
    current_lang = 'pt_BR' if system_lang and system_lang.startswith('pt') else 'en_US'
    
    # Process bilingual content
    processed_context = {}
    for key, value in context.items():
        if isinstance(value, dict) and ('pt_BR' in value or 'en_US' in value):
            # This is bilingual content
            processed_context[key] = value.get(current_lang, value.get('en_US', value))
        else:
            # This is language-agnostic content
            processed_context[key] = value
    
    return processed_context

# LANG is now imported from translations.py

load_dotenv()

from brands_config import client_brands

available_chats = {
    'Copiloto': 'copilot',
    'Insighter': 'insighter',

}

available_analyses = {
    'GeoCommerce': 'geocommerce',
    'RFMify': 'rfmify',
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

def process_product_files(uploaded_files, additional_context="", product_url=""):
    """
    Process uploaded files and generate individual YAML files with product information.
    Supports all file formats that file_reader.py can handle: PDF, CSV, TXT, DOC, DOCX, PPT, PPTX, XLS, XLSX, JSON, MD.
    
    Args:
        uploaded_files: List of uploaded files from Streamlit
        additional_context: Additional context provided by the user
        product_url: URL of the product being documented
        
    Returns:
        list: List of dictionaries containing information about processed products
    """
    processed_products = []
    
    try:
        # Import supported file types from file_reader
        from tools.file_reader import valid_inputs
        
        # Get the brand context to determine where to save the product info
        context = st.session_state.get('context', {})
        brand_id = context.get('brand_id', 'gebeauty')
        
        # Define products directory path
        products_dir = base_dir / 'z_brands' / brand_id / 'products'
        
        # Ensure the directory exists
        products_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            try:
                # Get file extension
                _, file_extension = os.path.splitext(uploaded_file.name.lower())
                file_extension = file_extension.lstrip('.')  # remove dot
                
                # Validate file type against supported formats
                if file_extension not in valid_inputs:
                    st.warning(f"Skipping {uploaded_file.name} - file type '.{file_extension}' not supported. Supported formats: {', '.join(valid_inputs)}")
                    continue
                
                # Load and process the file content
                file_content = load_input(uploaded_file, uploaded_file.name)
                
                # Extract product handle from URL or generate from filename
                if product_url:
                    product_handle = extract_handle_from_url(product_url)
                else:
                    # Generate handle from filename by removing extension and cleaning up
                    base_filename = os.path.splitext(uploaded_file.name)[0]
                    product_handle = base_filename.lower().replace(' ', '-').replace('_', '-')
                
                # Fallback if handle extraction fails
                if not product_handle:
                    product_handle = os.path.splitext(uploaded_file.name)[0].lower().replace(' ', '-').replace('_', '-')
                
                # Extract product information in YAML format using LLM
                yaml_content = extract_product_yaml(
                    file_content, 
                    additional_context, 
                    product_url,
                    uploaded_file.name,
                    product_handle
                )
                
                # Generate individual YAML file
                yaml_file_path = generate_product_yaml_file(yaml_content, product_handle, products_dir)
                
                # Extract product name and category from YAML for summary
                try:
                    import yaml as yaml_parser
                    yaml_data = yaml_parser.safe_load(yaml_content)
                    product_name = yaml_data.get('meta', {}).get('display_name', product_handle)
                    product_category = yaml_data.get('meta', {}).get('category', 'Unknown')
                except:
                    product_name = product_handle
                    product_category = 'Unknown'
                
                # Add to processed products list
                processed_products.append({
                    'name': product_name,
                    'category': product_category,
                    'handle': product_handle,
                    'file': uploaded_file.name,
                    'yaml_file': f"{product_handle}.yaml",
                    'file_type': file_extension.upper()
                })
                
                st.success(f"Generated YAML file for {product_handle}.yaml from {file_extension.upper()} file")
                
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
                continue
                
        return processed_products
        
    except Exception as e:
        raise Exception(f"Failed to process product files: {str(e)}")

def extract_product_information(file_content, additional_context, product_url, filename):
    """
    Use LLM to extract structured product information from file content.
    Uses the brand's preferred language for extraction.
    
    Args:
        file_content: Raw content from uploaded file
        additional_context: User-provided context
        product_url: Product URL
        filename: Original filename
        
    Returns:
        dict: Structured product information
    """
    try:
        # Get API key from session state
        api_key = st.session_state.get('api_key_OpenAI')
        if not api_key:
            raise Exception("OpenAI API key not found")
        
        # Get brand's preferred language from context
        context = st.session_state.get('context', {})
        preferred_language = context.get('preferred_language', 'en_US')
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0.1
        )
        
        # Language-specific prompts
        prompts = {
            'pt_BR': """
        Você é um especialista em análise de produtos de beleza e cuidados capilares.
        
        Analise o conteúdo fornecido e extraia informações estruturadas sobre o produto.
        
        CONTEÚDO PARA ANALISAR:
        {content}
        
        CONTEXTO ADICIONAL: {additional_context}
        URL DO PRODUTO: {product_url}
        ARQUIVO FONTE: {filename}
        
        Extraia e estruture as seguintes informações em formato JSON:
        {{
            "product_name": "Nome do produto",
            "product_url": "URL do produto",
            "category": "Categoria (ex: shampoo, condicionador, booster, primer, etc.)",
            "purpose": "Finalidade/função principal do produto",
            "main_ingredients": ["Lista", "dos", "ingredientes", "principais"],
            "target_hair_type": "Indicação para tipo de cabelo",
            "key_benefits": ["Lista", "dos", "principais", "benefícios"],
            "usage_instructions": "Como usar o produto",
            "claims": ["Claims", "específicos", "do", "produto"],
            "technical_info": "Informações técnicas relevantes (se houver)",
            "source_file": "Nome do arquivo fonte"
        }}
        
        IMPORTANTE:
        - Seja preciso e extraia apenas informações que estão claramente presentes no conteúdo
        - Use a terminologia técnica apropriada para produtos capilares
        - Mantenha consistência com o padrão da marca GE Beauty
        - Se alguma informação não estiver disponível, use null
        - Responda APENAS com o JSON válido, sem texto adicional
        - Todas as informações devem estar em PORTUGUÊS BRASILEIRO
        """,
            'en_US': """
        You are an expert in beauty and hair care product analysis.
        
        Analyze the provided content and extract structured product information.
        
        CONTENT TO ANALYZE:
        {content}
        
        ADDITIONAL CONTEXT: {additional_context}
        PRODUCT URL: {product_url}
        SOURCE FILE: {filename}
        
        Extract and structure the following information in JSON format:
        {{
            "product_name": "Product name",
            "product_url": "Product URL",
            "category": "Category (e.g., shampoo, conditioner, booster, primer, etc.)",
            "purpose": "Main purpose/function of the product",
            "main_ingredients": ["List", "of", "main", "ingredients"],
            "target_hair_type": "Hair type indication",
            "key_benefits": ["List", "of", "main", "benefits"],
            "usage_instructions": "How to use the product",
            "claims": ["Specific", "product", "claims"],
            "technical_info": "Relevant technical information (if any)",
            "source_file": "Source file name"
        }}
        
        IMPORTANT:
        - Be precise and extract only information that is clearly present in the content
        - Use appropriate technical terminology for hair care products
        - Maintain consistency with GE Beauty brand standards
        - If any information is not available, use null
        - Respond ONLY with valid JSON, no additional text
        - All information should be in ENGLISH
        """
        }
        
        # Get the appropriate prompt based on preferred language
        prompt_text = prompts.get(preferred_language, prompts['en_US'])
        
        # Create extraction prompt
        extraction_prompt = ChatPromptTemplate.from_template(prompt_text)
        
        # Language-specific default messages
        if preferred_language == 'pt_BR':
            default_context = additional_context or "Nenhum contexto adicional fornecido"
            default_url = product_url or "URL não fornecida"
        else:
            default_context = additional_context or "No additional context provided"
            default_url = product_url or "No URL provided"
        
        # Execute extraction
        messages = extraction_prompt.format_messages(
            content=file_content,
            additional_context=default_context,
            product_url=default_url,
            filename=filename
        )
        
        response = llm.invoke(messages)
        
        # Parse JSON response
        import json
        try:
            structured_info = json.loads(response.content.strip())
            # Ensure product_url is included
            if product_url:
                structured_info['product_url'] = product_url
            structured_info['source_file'] = filename
            return structured_info
        except json.JSONDecodeError:
            # Language-specific fallback messages
            if preferred_language == 'pt_BR':
                fallback_data = {
                    "product_name": f"Produto de {filename}",
                    "product_url": product_url,
                    "category": "Não especificado",
                    "purpose": "Informações extraídas do arquivo carregado",
                    "main_ingredients": [],
                    "target_hair_type": "Não especificado",
                    "key_benefits": [],
                    "usage_instructions": "Ver conteúdo original",
                    "claims": [],
                    "technical_info": file_content[:500] + "..." if len(file_content) > 500 else file_content,
                    "source_file": filename
                }
            else:
                fallback_data = {
                    "product_name": f"Product from {filename}",
                    "product_url": product_url,
                    "category": "Not specified",
                    "purpose": "Information extracted from uploaded file",
                    "main_ingredients": [],
                    "target_hair_type": "Not specified",
                    "key_benefits": [],
                    "usage_instructions": "See original content",
                    "claims": [],
                    "technical_info": file_content[:500] + "..." if len(file_content) > 500 else file_content,
                    "source_file": filename
                }
            
            return fallback_data
        
    except Exception as e:
        st.error(f"Error extracting product information: {str(e)}")
        
        # Get preferred language for error fallback
        context = st.session_state.get('context', {})
        preferred_language = context.get('preferred_language', 'en_US')
        
        # Language-specific error fallback
        if preferred_language == 'pt_BR':
            error_fallback = {
                "product_name": f"Produto de {filename}",
                "product_url": product_url,
                "category": "Não especificado",
                "purpose": "Erro na extração - ver arquivo original",
                "main_ingredients": [],
                "target_hair_type": "Não especificado",
                "key_benefits": [],
                "usage_instructions": "Ver arquivo original",
                "claims": [],
                "technical_info": str(e),
                "source_file": filename
            }
        else:
            error_fallback = {
                "product_name": f"Product from {filename}",
                "product_url": product_url,
                "category": "Not specified",
                "purpose": "Extraction error - see original file",
                "main_ingredients": [],
                "target_hair_type": "Not specified",
                "key_benefits": [],
                "usage_instructions": "See original file",
                "claims": [],
                "technical_info": str(e),
                "source_file": filename
            }
        
        return error_fallback

def update_products_with_structured_info(structured_info, products_file_path):
    """
    Update products.md with properly formatted structured information.
    
    Args:
        structured_info: Structured product information from LLM extraction
        products_file_path: Path to the products.md file
    """
    try:
        # Format the product entry according to existing structure
        product_entry = format_product_entry(structured_info)
        
        # Read existing content
        existing_content = ""
        if products_file_path.exists():
            with open(products_file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # Find appropriate insertion point (before claims section or at end)
        claims_section = "## 7. Claims e Certificações"
        if claims_section in existing_content:
            # Insert before claims section
            parts = existing_content.split(claims_section)
            new_content = parts[0] + product_entry + "\n" + claims_section + parts[1]
        else:
            # Append at end
            new_content = existing_content.rstrip() + "\n\n" + product_entry
        
        # Write updated content
        with open(products_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
    except Exception as e:
        raise Exception(f"Failed to update products file with structured info: {str(e)}")

def format_product_entry(info):
    """
    Format structured product information into the products.md format.
    
    Args:
        info: Structured product information dictionary
        
    Returns:
        str: Formatted product entry
    """
    product_name = info.get('product_name', 'Produto Desconhecido')
    product_url = info.get('product_url', '')
    category = info.get('category', 'Diversos')
    purpose = info.get('purpose', 'Não especificado')
    ingredients = info.get('main_ingredients', [])
    target_hair = info.get('target_hair_type', 'Não especificado')
    benefits = info.get('key_benefits', [])
    usage = info.get('usage_instructions', 'Ver instruções originais')
    claims = info.get('claims', [])
    technical = info.get('technical_info', '')
    source_file = info.get('source_file', 'Arquivo desconhecido')
    
    # Build formatted entry
    entry = f"\n### {product_name}"
    if product_url:
        entry += f" ({product_url})"
    entry += "\n"
    
    entry += f"- **Finalidade:** {purpose}\n"
    
    if ingredients:
        if isinstance(ingredients, list):
            ingredients_str = ", ".join(ingredients)
        else:
            ingredients_str = str(ingredients)
        entry += f"- **Ingredientes principais:** {ingredients_str}\n"
    
    entry += f"- **Indicação:** {target_hair}\n"
    
    if benefits:
        entry += f"- **Principais benefícios:** {', '.join(benefits) if isinstance(benefits, list) else benefits}\n"
    
    if usage and usage != "Ver instruções originais":
        entry += f"- **Como usar:** {usage}\n"
    
    if claims:
        entry += f"- **Claims:** {', '.join(claims) if isinstance(claims, list) else claims}\n"
    
    if technical:
        entry += f"\n**Informações técnicas:**\n{technical}\n"
    
    entry += f"\n*Fonte: {source_file}*\n"
    
    return entry

def update_products_file_entry(content, metadata, products_file_path):
    """
    Update the products file with a new entry.
    
    Args:
        content: The processed file content
        metadata: File metadata including source, type, and context
        products_file_path: Path to the products file
    """
    try:
        # Append new entry to products file
        with open(products_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## New Product Information: {metadata.get('source', 'unknown')}\n\n")
            
            # Add additional context if provided
            if metadata.get('additional_context'):
                f.write(f"### Context:\n{metadata['additional_context']}\n\n")
            
            # Add file metadata
            f.write(f"### Source Information:\n")
            f.write(f"- **File**: {metadata.get('source', 'unknown')}\n")
            f.write(f"- **Type**: {metadata.get('type', 'unknown')}\n")
            if metadata.get('product_url'):
                f.write(f"- **Product URL**: {metadata['product_url']}\n")
            f.write(f"\n")
            
            # Add the content
            f.write(f"### Content:\n{content}\n\n---\n")
            
    except Exception as e:
        raise Exception(f"Failed to update products file: {str(e)}")

def extract_handle_from_url(product_url):
    """
    Extract product handle/slug from URL.
    
    Args:
        product_url: Product URL string
        
    Returns:
        str: Product handle/slug
    """
    try:
        if not product_url:
            return None
        
        # Remove protocol and domain, get the path
        from urllib.parse import urlparse
        parsed_url = urlparse(product_url)
        path = parsed_url.path.strip('/')
        
        # Get the last segment as handle
        if '/' in path:
            handle = path.split('/')[-1]
        else:
            handle = path
        
        # Clean up the handle
        handle = handle.lower().replace(' ', '-').replace('_', '-')
        
        # Remove file extensions if any
        if '.' in handle:
            handle = handle.split('.')[0]
            
        return handle if handle else None
        
    except Exception as e:
        st.warning(f"Could not extract handle from URL {product_url}: {str(e)}")
        return None

def extract_product_yaml(file_content, additional_context, product_url, filename, product_handle):
    """
    Use LLM to extract product information and generate YAML according to the template.
    Analyzes both uploaded file content and web content from product URL if provided.
    Uses the brand's preferred language for extraction.
    
    Args:
        file_content: Raw content from uploaded file
        additional_context: User-provided context
        product_url: Product URL to analyze
        filename: Original filename
        product_handle: Product handle extracted from URL
        
    Returns:
        str: Generated YAML content
    """
    try:
        # Get API key from session state
        api_key = st.session_state.get('api_key_OpenAI')
        if not api_key:
            raise Exception("OpenAI API key not found")
        
        # Get brand's preferred language from context
        context = st.session_state.get('context', {})
        preferred_language = context.get('preferred_language', 'en_US')
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=api_key,
            temperature=0.1
        )
        
        # Extract web content if URL is provided
        web_content = ""
        web_analysis_note = ""
        if product_url and product_url.strip():
            try:
                from tools.file_reader import web_reader
                web_content = web_reader(product_url.strip())
                web_analysis_note = f"\n\nWEB CONTENT FROM {product_url}:\n{web_content}\n"
                st.info(f"Successfully extracted content from product URL: {product_url}")
            except Exception as web_error:
                st.warning(f"Could not extract content from URL {product_url}: {str(web_error)}")
                web_analysis_note = f"\n\nWEB CONTENT EXTRACTION FAILED: {str(web_error)}\n"
        
        # Define language-specific prompts
        prompts = {
            'pt_BR': """
        Você é um especialista em análise de produtos de beleza e cuidados capilares com conhecimento regulatório e de marketing.
        
        Analise o conteúdo fornecido e extraia informações para preencher o template YAML exatamente como especificado.
        
        CONTEÚDO DO ARQUIVO CARREGADO:
        {content}
        {web_analysis_note}
        
        CONTEXTO ADICIONAL: {additional_context}
        URL DO PRODUTO: {product_url}
        IDENTIFICADOR DO PRODUTO: {product_handle}
        ARQUIVO FONTE: {filename}
        
        INSTRUÇÕES ABRANGENTES DE EXTRAÇÃO:
        1. PROFUNDIDADE DE ANÁLISE: Extraia TODAS as informações disponíveis, não apenas fatos básicos
           - Procure por descrições detalhadas do produto, não apenas nomes
           - Extraia claims específicos, percentuais, cronogramas e resultados mensuráveis
           - Capture benefícios diferenciados (imediatos vs longo prazo, funcionais vs emocionais)
           - Encontre especificações técnicas, detalhes de aplicação e cenários de uso
           
        2. INTEGRAÇÃO MULTI-FONTE: Combine arquivo carregado E conteúdo web minuciosamente
           - Faça referências cruzadas para precisão e completude
           - Use conteúdo web para copy de marketing, preços, avaliações de clientes
           - Use conteúdo de arquivo para especificações técnicas, detalhes de ingredientes, dados clínicos
           - Sintetize informações complementares de ambas as fontes
           
        3. CONTEÚDO PRONTO PARA MARKETING: Extraia informações otimizadas para criação de conteúdo
           - Capture linguagem emocional e descrições sensoriais
           - Extraia pontos de dor do cliente e narrativas de solução
           - Encontre vantagens competitivas e proposições únicas de venda
           - Colete prova social, depoimentos e endossos de especialistas
           
        4. CIENTÍFICO E REGULATÓRIO: Extraia todas as informações técnicas e de conformidade
           - Análise detalhada de ingredientes com concentrações e funções
           - Resultados de estudos clínicos com percentuais específicos e cronogramas
           - Informações de segurança, contraindicações e limitações de uso
           - Claims regulatórios e certificações
           
        5. DETALHES DA EXPERIÊNCIA DO USUÁRIO: Capture informações abrangentes de uso
           - Métodos de aplicação passo a passo com cronometragem e quantidades
           - Compatibilidade com tipos de cabelo com condições e texturas específicas
           - Instruções de camadas e compatibilidade com ferramentas de styling
           - Dicas de solução de problemas e variações sazonais
           
        6. ATRIBUIÇÃO DE FONTE: Mantenha rastreabilidade perfeita
           - Conteúdo do arquivo: # página: X ou # arquivo: {filename}
           - Conteúdo web: # web: {product_url}
           - Para informações sintetizadas, cite ambas as fontes
           
        7. PRIORIDADE DE COMPLETUDE: Preencha o máximo de campos possível
           - Use null apenas quando a informação não estiver genuinamente disponível
           - Infira informações razoáveis quando o contexto permitir
           - Extraia benefícios implícitos de listas de ingredientes e claims
           - Derive cenários de uso do posicionamento do produto
           
        8. QUALIDADE YAML: Mantenha estrutura e legibilidade perfeitas
           - Use indentação de 2 espaços consistentemente
           - Assegure que todas as listas e blocos de texto estejam formatados adequadamente
           - Retorne APENAS o YAML preenchido sem texto adicional
           - Valide que todas as aspas e caracteres especiais estejam adequadamente escapados
        
        IMPORTANTE: Todas as informações extraídas devem estar em PORTUGUÊS BRASILEIRO.
        """,
            'en_US': """
        You are an expert in beauty and hair care product analysis with regulatory and marketing knowledge.
        
        Analyze the provided content sources and extract information to fill the YAML template exactly as specified.
        
        UPLOADED FILE CONTENT:
        {content}
        {web_analysis_note}
        
        ADDITIONAL CONTEXT: {additional_context}
        PRODUCT URL: {product_url}
        PRODUCT HANDLE: {product_handle}
        SOURCE FILE: {filename}
        
        COMPREHENSIVE EXTRACTION INSTRUCTIONS:
        1. DEPTH OF ANALYSIS: Extract ALL available information, not just basic facts
           - Look for detailed product descriptions, not just names
           - Extract specific claims, percentages, timeframes, and measurable results
           - Capture nuanced benefits (immediate vs long-term, functional vs emotional)
           - Find technical specifications, application details, and usage scenarios
           
        2. MULTI-SOURCE INTEGRATION: Combine uploaded file AND web content thoroughly
           - Cross-reference information for accuracy and completeness
           - Use web content for marketing copy, pricing, customer reviews
           - Use file content for technical specs, ingredient details, clinical data
           - Synthesize complementary information from both sources
           
        3. MARKETING-READY CONTENT: Extract information optimized for content creation
           - Capture emotional language and sensory descriptions
           - Extract customer pain points and solution narratives
           - Find competitive advantages and unique selling propositions
           - Gather social proof, testimonials, and expert endorsements
           
        4. SCIENTIFIC AND REGULATORY: Extract all technical and compliance information
           - Detailed ingredient analysis with concentrations and functions
           - Clinical study results with specific percentages and timeframes
           - Safety information, contraindications, and usage limitations
           - Regulatory claims and certifications
           
        5. USER EXPERIENCE DETAILS: Capture comprehensive usage information
           - Step-by-step application methods with timing and amounts
           - Hair type compatibility with specific conditions and textures
           - Layering instructions and styling tool compatibility
           - Troubleshooting tips and seasonal variations
           
        6. SOURCE ATTRIBUTION: Maintain perfect traceability
           - File content: # page: X or # file: {filename}
           - Web content: # web: {product_url}
           - For synthesized information, cite both sources
           
        7. COMPLETENESS PRIORITY: Fill as many fields as possible
           - Use null only when information is genuinely unavailable
           - Infer reasonable information when context allows
           - Extract implied benefits from ingredient lists and claims
           - Derive usage scenarios from product positioning
           
        8. YAML QUALITY: Maintain perfect structure and readability
           - Use 2 spaces indentation consistently
           - Ensure all lists and text blocks are properly formatted
           - Return ONLY the filled YAML with no additional text
           - Validate that all quotes and special characters are properly escaped
        
        IMPORTANT: All extracted information should be in ENGLISH.
        """
        }
        
        # Get the appropriate prompt based on preferred language
        prompt_template = prompts.get(preferred_language, prompts['en_US'])
        
        # Create extraction prompt for YAML generation  
        yaml_extraction_prompt = ChatPromptTemplate.from_template(prompt_template + """
        
        COMPREHENSIVE YAML TEMPLATE TO FILL:
        
        meta:
          product_id: "{product_handle}"
          display_name: ""
          brand: "GE Beauty"
          slug: "{product_handle}"
          category: ""
          subcategory: ""
          version: 1
          last_update: "{current_date}"
          launch_date: ""
          price_range: ""
          sizes_available: []

        product_description:
          short: ""
          detailed: |
            ""
          key_differentiators: []
          positioning: ""
          target_customer: ""

        benefits:
          immediate_results: []
          short_term: []
          long_term: []
          functional: []
          emotional: []
          aesthetic: []
          protective: []

        actives:
          - id: ""
            name: ""
            concentration: ""
            function: ""
            mechanism: ""
            benefits: []
            source: ""
            certifications: []

        formulation:
          texture: ""
          viscosity: ""
          absorption: ""
          finish: ""
          scent_profile: ""
          color: ""
          ph_level: ""
          full_inci: |
            ""

        hair_compatibility:
          hair_types: []
          textures: []
          conditions: []
          porosity_levels: []
          scalp_types: []
          excluded_types: []

        application:
          frequency: ""
          method: |
            ""
          amount_guide: ""
          timing: ""
          layering: []
          styling_compatibility: []
          removal_method: ""

        performance_metrics:
          clinical_results: []
          user_study_results: []
          before_after_claims: []
          duration_of_effects: ""
          improvement_timeline: ""

        technical_specs:
          heat_protection_temp: ""
          humidity_resistance: ""
          water_resistance: ""
          uv_protection: ""
          hold_strength: ""
          shine_level: ""

        usage_scenarios:
          daily_routine: |
            ""
          special_occasions: |
            ""
          professional_use: |
            ""
          troubleshooting: []
          seasonal_tips: []

        safety_information:
          contraindications: []
          precautions: []
          storage_requirements: ""
          shelf_life: ""
          pregnancy_safe: null
          child_safe: null

        regulatory_claims:
          dermatologically_tested: null
          hypoallergenic: null
          non_comedogenic: null
          cruelty_free: null
          vegan: null
          sulfate_free: null
          paraben_free: null
          silicone_free: null
          artificial_fragrance_free: null

        certifications:
          organic: []
          sustainable: []
          professional: []
          awards: []

        marketing_copy:
          hero_headline: ""
          subheadlines: []
          elevator_pitch: ""
          key_messages: []
          call_to_action: []
          social_proof: []
          comparison_points: []

        content_hooks:
          problem_statements: []
          solution_narratives: []
          transformation_stories: []
          expert_insights: []
          ingredient_spotlights: []
          routine_integration: []

        disclaimers:
          results_variability: []
          usage_limitations: []
          regulatory_required: []

        CRITICAL: Every extracted piece of information must include proper source references.
         """)
        
        # Get current date for metadata
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Execute extraction
        messages = yaml_extraction_prompt.format_messages(
            content=file_content,
            web_analysis_note=web_analysis_note,
            additional_context=additional_context or "No additional context provided",
            product_url=product_url or "No URL provided",
            filename=filename,
            product_handle=product_handle,
            current_date=current_date
        )
        
        response = llm.invoke(messages)
        
        # Return the YAML content
        return response.content.strip()
        
    except Exception as e:
        st.error(f"Error extracting product YAML: {str(e)}")
        # Return basic fallback YAML structure
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get brand's preferred language for fallback messages
        context = st.session_state.get('context', {})
        preferred_language = context.get('preferred_language', 'en_US')
        
        # Language-specific fallback messages
        if preferred_language == 'pt_BR':
            fallback_messages = {
                'extraction_failed': 'Extração de informações falhou',
                'failed_to_extract': 'Falha ao extrair',
                'see_original': 'Ver arquivo original',
                'see_documentation': 'Ver documentação original',
                'refer_original': 'Falha na extração - consulte a documentação original'
            }
        else:
            fallback_messages = {
                'extraction_failed': 'Information extraction failed',
                'failed_to_extract': 'Failed to extract',
                'see_original': 'See original document file',
                'see_documentation': 'See original documentation',
                'refer_original': 'Information extraction failed - refer to original documentation'
            }
        
        fallback_yaml = f"""meta:
  product_id: "{product_handle}"
  display_name: "Product from {filename}"
  brand: "GE Beauty"
  slug: "{product_handle}"
  category: null
  subcategory: null
  version: 1
  last_update: "{current_date}"
  launch_date: null
  price_range: null
  sizes_available: []

product_description:
  short: "{fallback_messages['refer_original']}" # file: {filename}
  detailed: |
    {fallback_messages['extraction_failed']}. Error: {str(e)} # file: {filename}
  key_differentiators: []
  positioning: null
  target_customer: null

benefits:
  immediate_results: []
  short_term: []
  long_term: []
  functional: 
    - "{fallback_messages['extraction_failed']}" # file: {filename}
  emotional: []
  aesthetic: []
  protective: []

actives:
  - id: "unknown"
    name: "{fallback_messages['failed_to_extract']}" # file: {filename}
    concentration: null
    function: null
    mechanism: null
    benefits: []
    source: null
    certifications: []

formulation:
  texture: null
  viscosity: null
  absorption: null
  finish: null
  scent_profile: null
  color: null
  ph_level: null
  full_inci: null

hair_compatibility:
  hair_types: []
  textures: []
  conditions: []
  porosity_levels: []
  scalp_types: []
  excluded_types: []

application:
  frequency: null
  method: |
    {fallback_messages['see_original']} # file: {filename}
  amount_guide: null
  timing: null
  layering: []
  styling_compatibility: []
  removal_method: null

performance_metrics:
  clinical_results: []
  user_study_results: []
  before_after_claims: []
  duration_of_effects: null
  improvement_timeline: null

technical_specs:
  heat_protection_temp: null
  humidity_resistance: null
  water_resistance: null
  uv_protection: null
  hold_strength: null
  shine_level: null

usage_scenarios:
  daily_routine: null
  special_occasions: null
  professional_use: null
  troubleshooting: []
  seasonal_tips: []

safety_information:
  contraindications: []
  precautions: []
  storage_requirements: null
  shelf_life: null
  pregnancy_safe: null
  child_safe: null

regulatory_claims:
  dermatologically_tested: null
  hypoallergenic: null
  non_comedogenic: null
  cruelty_free: null
  vegan: null
  sulfate_free: null
  paraben_free: null
  silicone_free: null
  artificial_fragrance_free: null

certifications:
  organic: []
  sustainable: []
  professional: []
  awards: []

marketing_copy:
  hero_headline: "{fallback_messages['see_documentation']}" # file: {filename}
  subheadlines: []
  elevator_pitch: null
  key_messages: []
  call_to_action: []
  social_proof: []
  comparison_points: []

content_hooks:
  problem_statements: []
  solution_narratives: []
  transformation_stories: []
  expert_insights: []
  ingredient_spotlights: []
  routine_integration: []

disclaimers:
  results_variability: 
    - "{fallback_messages['refer_original']}" # file: {filename}
  usage_limitations: []
  regulatory_required: []
"""
        return fallback_yaml

def generate_product_yaml_file(yaml_content, product_handle, products_dir):
    """
    Generate individual YAML file for the product.
    
    Args:
        yaml_content: Generated YAML content string
        product_handle: Product handle for filename
        products_dir: Directory to save the YAML file
    """
    try:
        # Create filename
        yaml_filename = f"{product_handle}.yaml"
        yaml_file_path = products_dir / yaml_filename
        
        # Write YAML content to file
        with open(yaml_file_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
            
        return yaml_file_path
        
    except Exception as e:
        raise Exception(f"Failed to generate YAML file: {str(e)}")

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
    file_voice = brand_folder / 'voice.md'
    file_products = brand_folder / 'products.md'
    
    if not file_registration.exists() or not file_voice.exists() or not file_products.exists():
        raise FileNotFoundError(LANG['missing_files'].format(brand_name))

    with open(file_registration, 'r', encoding='utf-8') as f:
        registration = yaml.safe_load(f)

    with open(file_voice, 'r', encoding='utf-8') as f:
        voice = escape_braces(f.read())

    with open(file_products, 'r', encoding='utf-8') as f:
        products = escape_braces(f.read())

    # Load format recommendations from platform-based system
    platform = registration.get('platform', 'shopify')  # Default to shopify if not specified
    format_file = base_dir / 'chats' / 'seo_lab' / 'formats' / f'{platform}.md'
    
    if format_file.exists():
        with open(format_file, 'r', encoding='utf-8') as f:
            format_recommendations = escape_braces(f.read())
    else:
        # Fallback - empty string
        format_recommendations = ""

    # Get preferred language, default to English if not specified
    preferred_language = registration.get('preferred_language', 'en_US')

    return registration['brand'], registration['brand_category'], registration['blog'], registration['benchmarks'], voice, products, format_recommendations, preferred_language

intro = ConversationBufferMemory()

def load_model(chosen_provider, version_id, api_key):
    context = st.session_state.get('context', {})

    brand = context.get('brand', '')
    blog = context.get('blog', '')
    benchmarks = context.get('benchmarks', '')
    voice = context.get('voice', '')
    products = context.get('products', '')
    
    # Check if brand context is fully loaded - CRITICAL for proper AI responses
    missing_context = []
    if not brand:
        missing_context.append("brand")
    if not blog:
        missing_context.append("blog")
    if not benchmarks:
        missing_context.append("benchmarks")
    if not voice:
        missing_context.append("voice")
    if not products:
        missing_context.append("products")
    
    if missing_context:
        st.error(LANG['brand_context_critical_error'])
        st.error(LANG['brand_context_missing_fields'].format(', '.join(missing_context)))
        st.error(LANG['brand_context_ai_generic'])
        
        # Provide specific guidance based on what's missing
        if not context.get('brand_id'):
            st.error(LANG['brand_context_select_brand_first'])
        else:
            st.error(LANG['brand_context_auto_load_ai'])
        
        # Set placeholder values that clearly indicate missing data
        brand = "[BRAND NOT LOADED - Please complete settings]"
        blog = "[BLOG NOT LOADED - Please complete settings]"
        benchmarks = "[BENCHMARKS NOT LOADED - Please complete settings]"
        voice = "[VOICE NOT LOADED - Please complete settings]"
        products = "[PRODUCTS NOT LOADED - Please complete settings]"

    # Always load the correct guidelines for the selected function
    chosen_function = st.session_state.get('chosen_function', 'copilot')
    base_dir = Path(__file__).resolve().parent
    file_guidelines = base_dir / 'chats' / chosen_function / 'guidelines.md'
    
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
    brand_id = context.get('brand_id')

    prompt = f'''
    You have several information about the user's business:
    - {brand}
    - {products}
    - {voice}
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
    page_title='Nami',
    page_icon='🦊',
    layout='wide',
    )

def sidebar_menu():
    chosen_function = st.session_state.get('chosen_function', 'copilot')
    context_info = get_function_context(chosen_function)
    
    # Show function-specific sidebar if enabled
    if chosen_function != 'copilot' and context_info.get('sidebar_enabled', False):
        render_function_sidebar(chosen_function, context_info)
    else:
        render_default_sidebar()

def settings_menu():
    """Render the settings menu with brand selection and reset functionality"""
    # Brand selection section
    # Import available brands from brands_config.py
    from brands_config import client_brands
    available_brands = client_brands
    
    # Get current brand selection from session state
    current_brand = st.session_state.get('selected_brand', list(available_brands.keys())[0])
    
    # Brand selector
    selected_brand_display = st.selectbox(
        LANG['brand_selector_title'],
        options=list(available_brands.keys()),
        index=list(available_brands.keys()).index(current_brand),
        help=LANG['brand_selector_help']
    )
    
    # Get the brand ID from the display name
    selected_brand_id = available_brands[selected_brand_display]
    
    # Update session state if brand changed
    if selected_brand_display != current_brand:
        st.session_state['selected_brand'] = selected_brand_display
        st.session_state['selected_brand_id'] = selected_brand_id
        
        # Update context with new brand
        if 'context' not in st.session_state:
            st.session_state['context'] = {}
        st.session_state['context']['brand_id'] = selected_brand_id
        
        # CRITICAL FIX: Load brand context immediately when brand is selected
        try:
            with st.spinner(LANG['brand_context_loading'].format(selected_brand_display)):
                brand, brand_category, blog, benchmarks, voice, products, format_recommendations, preferred_language = load_brand_files(selected_brand_id)
                
                st.session_state['context'] = {
                    'brand': brand,
                    'brand_id': selected_brand_id,
                    'brand_category': brand_category,
                    'blog': blog,
                    'benchmarks': benchmarks,
                    'voice': voice,
                    'products': products,
                    'format_recommendations': format_recommendations,
                    'preferred_language': preferred_language,
                }
            st.success(LANG['brand_context_loaded_success'].format(selected_brand_display))
            
        except FileNotFoundError as e:
            st.error(LANG['brand_context_failed'].format(str(e)))
            st.error(LANG['brand_context_missing_files'])
            st.error(LANG['brand_context_registration_yaml'])
            st.error(LANG['brand_context_voice_md']) 
            st.error(LANG['brand_context_products_md'])
            st.error(LANG['brand_context_format_md'])
            st.stop()
        
        # Clear the chain to force reload with new brand context
        if 'Chain' in st.session_state:
            del st.session_state['Chain']
        
        # Clear memory to start fresh with new brand
        if 'memory' in st.session_state:
            del st.session_state['memory']
        
        st.success(LANG['brand_selection_updated'])
        time.sleep(2)
        st.rerun()
    
    # Show current brand selection
    if st.session_state.get('selected_brand'):
        st.info(f"🎯 {LANG['brand_selection_confirmed'].format(st.session_state['selected_brand'])}")
        
        # Show brand context status with detailed information
        context = st.session_state.get('context', {})
        brand_id = st.session_state.get('selected_brand_id')
        
        if context.get('brand_id') == brand_id:
            # Check if all required context fields are loaded
            required_fields = ['brand', 'blog', 'benchmarks', 'voice', 'products']
            missing_fields = [field for field in required_fields if not context.get(field)]
            
            if not missing_fields:
                st.success(LANG['brand_context_fully_loaded'])
            else:
                # Show loading status instead of warning
                st.info(LANG['brand_context_loading_status'])
                st.info(LANG['brand_context_loading_wait'])
        else:
            st.info(LANG['brand_context_auto_load'])
            st.info(LANG['brand_context_auto_load_wait'])
    
    # Reset session state button
    st.markdown("---")
    
    if st.button(LANG['reset_session_button'], type="secondary", use_container_width=True, help=LANG['reset_session_help']):
        # Clear all session state except essential ones
        keys_to_keep = ['selected_brand', 'selected_brand_id', 'context']
        keys_to_clear = [key for key in st.session_state.keys() if key not in keys_to_keep]
        
        for key in keys_to_clear:
            del st.session_state[key]
        
        # Reset essential states to defaults
        st.session_state['chosen_function'] = 'copilot'
        st.session_state['memory'] = None
        st.session_state['Chain'] = None
        
        st.success(LANG['reset_session_success'])
        st.rerun()

def content_menu():
    # SEO Lab and CRM Lab buttons
    if st.button(f"{LANG['seo_lab']}", use_container_width=True, key="func_btn_seo_lab"):
        st.session_state['chosen_function'] = 'seo_lab'
        st.session_state['memory'] = ConversationBufferMemory()
        st.rerun()
    
    if st.button(f"{LANG['crm_lab']}", use_container_width=True, key="func_btn_crm_lab"):
        st.session_state['chosen_function'] = 'crm_lab'
        st.session_state['memory'] = ConversationBufferMemory()
        st.rerun()

def chats_menu():
    # Other chat functions (excluding content)
    for fname, fid in available_chats.items():
        if fid not in ['seo_lab', 'crm_lab']:
            btn = st.button(fname, use_container_width=True, key=f"func_btn_{fid}")
            if btn:
                st.session_state['chosen_function'] = fid
                st.rerun()

def analysis_menu():
    for fname, fid in available_analyses.items():
        is_selected = st.session_state.get('chosen_function', 'copilot') == fid
        btn = st.button(fname, use_container_width=True, key=f"func_btn_{fid}")
        if btn:
            st.session_state['chosen_function'] = fid
            st.rerun()

def render_function_sidebar(function_id, context_info):
    """
    Renders the sidebar menu for a specific function.
    """
    # Back button at the top
    if st.button(LANG.get('back_to_main', '← Back'), key="back_to_main"):
        st.session_state['chosen_function'] = 'copilot'
        st.rerun()
    
    tabs = st.tabs([context_info['title']])
    with tabs[0]:   
        
        # Function-specific content
        if function_id == 'seo_lab':
            seo_lab_sidebar()


def render_default_sidebar():
    """Render the default sidebar with function selection tabs"""

    with st.expander(LANG['settings_tab'], expanded=True):
        settings_menu()

    tabs = st.tabs([LANG['content_tab'], LANG['analysis_tab']])

    with tabs[0]:
        content_menu()
    with tabs[1]:
        analysis_menu()

    # Footer with knowledge functionality

def knowledge_menu():

    with st.expander(f"📚 {LANG['footer_add_knowledge']}", expanded=False):
        st.write(LANG['upload_files'])
        
        # Add choice for knowledge type
        knowledge_type = st.radio(
            LANG['knowledge_type_label'],
            [LANG['general_knowledge'], LANG['product_information']],
            index=0,
            help=LANG['knowledge_type_help']
        )
        
        # File uploader with clearing functionality
        if 'clear_files' not in st.session_state:
            st.session_state['clear_files'] = False
        
        # Clear the file uploader if requested
        if st.session_state['clear_files']:
            st.session_state['clear_files'] = False
            uploaded_files = None
        else:
            uploaded_files = st.file_uploader(
                "Choose files", 
                accept_multiple_files=True,
                type=['pdf', 'txt', 'doc', 'docx', 'md', 'csv', 'json', 'xlsx', 'pptx'],
                key="product_file_uploader"
            )
        
        # Additional context input field with clearing functionality
        if 'clear_context' not in st.session_state:
            st.session_state['clear_context'] = False
        
        if st.session_state['clear_context']:
            additional_context = ""
            st.session_state['clear_context'] = False
        else:
            additional_context = st.text_area(
                LANG['additional_context'],
                placeholder=LANG['context_placeholder'],
                height=100,
                key="product_context_area"
            )
        
        # Product URL field (only shown for product information) with clearing functionality
        product_url = ""
        if knowledge_type == LANG['product_information']:
            if 'clear_url' not in st.session_state:
                st.session_state['clear_url'] = False
            
            if st.session_state['clear_url']:
                product_url = ""
                st.session_state['clear_url'] = False
            else:
                product_url = st.text_input(
                    LANG['product_url_label'],
                    placeholder=LANG['product_url_placeholder'],
                    help=LANG['product_url_help'],
                    key="product_url_input"
                )
        
        # Send button with conditional processing
        if st.button(LANG['send_knowledge'], use_container_width=True):
            if not uploaded_files:
                st.warning(LANG['no_files_selected'])
            else:
                try:
                    if knowledge_type == LANG['general_knowledge']:
                        # Process uploaded files and add to knowledge base
                        process_knowledge_files(uploaded_files, additional_context)
                        st.success(LANG['knowledge_success'])
                        # Clear form after success
                        st.session_state['clear_files'] = True
                        st.session_state['clear_context'] = True
                    else:  # Product Information
                        # Show processing status for product extraction
                        with st.status(LANG['processing_product_info'], expanded=True) as status:
                            st.write("📁 Loading and analyzing file content...")
                            # Process uploaded files and add to products file
                            processed_products = process_product_files(uploaded_files, additional_context, product_url)
                            st.write("🎯 Extracting product information...")
                            st.write("📝 Generating YAML files...")
                            status.update(label="✅ Product processing complete!", state="complete")
                        
                        # Enhanced success message with details
                        if processed_products:
                            st.success("🎉 **Product Information Successfully Processed!**")
                            
                            # Show what was processed
                            with st.expander("📋 Processing Summary", expanded=True):
                                for product_info in processed_products:
                                    col1, col2 = st.columns([2, 1])
                                    with col1:
                                        st.write(f"✅ **{product_info['name']}**")
                                        if product_info.get('category'):
                                            st.write(f"   📂 Category: {product_info['category']}")
                                    with col2:
                                        st.write(f"📄 `{product_info['file']}`")
                                
                                st.markdown("**Files generated:**")
                                for product_info in processed_products:
                                    st.code(f"z_brands/gebeauty/products/{product_info['yaml_file']}")
                            
                            st.info("💡 These products are now available in the Blog Lab product selector!")
                        else:
                            st.success(LANG['product_extraction_success'])
                        
                        # Clear form after success
                        st.session_state['clear_files'] = True
                        st.session_state['clear_context'] = True
                        st.session_state['clear_url'] = True
                    
                    # Trigger rerun to clear the form
                    st.rerun()
                except Exception as e:
                    st.error(LANG['knowledge_error'].format(str(e)))

    # Check if brand is selected
    brand_id = st.session_state.get('selected_brand_id')
    
    if not brand_id:
        st.warning(f"⚠️ {LANG['brand_id_missing']}")
        st.info("Please select a brand in the Settings tab first.")
        return

    # Set default LLM (GPT-4o Mini)
    chosen_provider = 'OpenAI'
    version_id = 'gpt-4o-mini'
    api_key_env = os.getenv('OPENAI_API_KEY')
    api_key = api_key_env
    
    # Check if API key is available
    if not api_key:
        st.warning("⚠️ OPENAI_API_KEY environment variable not set. Please set it to use chat functions.")
        st.info("You can still use non-chat functions like GeoCommerce analysis.")
    else:
        st.session_state[f'api_key_{chosen_provider}'] = api_key

def handle_chat_interaction(prompt_message: str, chain, memory, key: str = "main_chat"):
    """
    Legacy function for backward compatibility.
    Chat interaction is now handled directly in the main nami() function.
    """
    # This function is kept for backward compatibility but is no longer used
    # Chat interaction is now handled directly in the main nami() function
    return None

# Updated _nami.py with automatic initialization and renamed function



def nami():
    """
    Main Nami application with automatic model initialization
    """
    # Set default function if not already set
    if 'chosen_function' not in st.session_state:
        st.session_state['chosen_function'] = 'copilot'
    chosen_function = st.session_state.get('chosen_function')
    context_info = get_function_context(chosen_function)

    # CRITICAL FIX: Ensure brand context is loaded on page refresh/load
    brand_id = st.session_state.get('selected_brand_id')
    if brand_id and not st.session_state.get('context', {}).get('brand'):
        try:
            with st.spinner(LANG['brand_context_loading'].format(st.session_state.get('selected_brand', 'Unknown'))):
                brand, brand_category, blog, benchmarks, voice, products, format_recommendations, preferred_language = load_brand_files(brand_id)
                
                st.session_state['context'] = {
                    'brand': brand,
                    'brand_id': brand_id,
                    'brand_category': brand_category,
                    'blog': blog,
                    'benchmarks': benchmarks,
                    'voice': voice,
                    'products': products,
                    'format_recommendations': format_recommendations,
                    'preferred_language': preferred_language,
                }
            st.success(LANG['brand_context_loaded_success'].format(st.session_state.get('selected_brand', 'Unknown')))
            
        except FileNotFoundError as e:
            st.error(LANG['brand_context_failed'].format(str(e)))
            st.error(LANG['brand_context_missing_files'])
            st.error(LANG['brand_context_registration_yaml'])
            st.error(LANG['brand_context_voice_md']) 
            st.error(LANG['brand_context_products_md'])
            st.error(LANG['brand_context_format_md'])
            st.stop()

    with st.sidebar:
        sidebar_menu()

    # Check if this is the initial state (no function selected yet)
    is_initial_state = (
        chosen_function == 'copilot' and 
        'Chain' not in st.session_state and 
        not st.session_state.get('memory')
    )

    if is_initial_state:
        # Show default welcome content only on initial load
        st.header('🦊 Nami', divider='red')
        st.subheader('Leveling the playing field for CPG startups with AI')
        st.write('Select a function to get started!')
        return

    # Show function-specific content
    st.header(context_info['title'], divider='red')

    if context_info['chat_enabled']:
        # Brand context should already be loaded from sidebar selection
        brand_id = st.session_state.get('selected_brand_id')
        if not brand_id:
            st.warning(LANG['brand_context_select_first'])
            return
            
        context = st.session_state.get('context', {})
        if not context.get('brand') or not context.get('blog') or not context.get('benchmarks') or not context.get('voice') or not context.get('products'):
            st.warning(LANG['brand_context_not_loaded'])
            return
        
        # Auto-initialize the model if not loaded - ONLY after brand context is ready
        if 'Chain' not in st.session_state:
            context = st.session_state.get('context', {})
            
            # CRITICAL FIX: Only load model if brand context is complete
            required_context_fields = ['brand', 'blog', 'benchmarks', 'voice', 'products']
            missing_context = [field for field in required_context_fields if not context.get(field)]
            
            if missing_context:
                st.warning(LANG['brand_context_waiting_load'].format(', '.join(missing_context)))
                st.info(LANG['brand_context_auto_load_features'])
                return  # Don't try to load model yet
            
            chosen_provider = 'OpenAI' if 'api_key_OpenAI' in st.session_state else 'Groq'
            version_id = st.session_state.get('version_id', 'gpt-4o-mini')
            api_key = st.session_state.get(f'api_key_{chosen_provider}', None)

            if api_key:
                try:
                    load_model(chosen_provider, version_id, api_key)
                    # Verify that the chain was actually loaded
                    if 'Chain' not in st.session_state or st.session_state['Chain'] is None:
                        st.error("⚠️ Model loading failed. Chain not properly initialized.")
                        st.stop()
                    brand_name = st.session_state.get('selected_brand', 'Unknown')
                    st.success(LANG['brand_context_model_success'].format(brand_name))
                except Exception as e:
                    st.error(f"Failed to load model: {str(e)}")
                    st.stop()
            else:
                st.warning("⚠️ No API Key found. Please set OPENAI_API_KEY environment variable to use chat functions.")
                st.info("You can still use non-chat functions like GeoCommerce analysis.")
                # Don't stop here, just disable chat functionality
                return
        
        # Chat-enabled functions: display context as system message only ONCE per session/function switch
        system_message_just_added = False
        if 'Chain' in st.session_state:
            memory = st.session_state.get('memory', intro)
            if memory is not None:
                system_message_exists = any(
                    msg.content == context_info['description'] and msg.type == 'ai' 
                    for msg in memory.buffer_as_messages
                )
                if not system_message_exists:
                    system_message = st.chat_message('ai', avatar='🦊')
                    system_message.markdown(context_info['description'])
                    memory.chat_memory.add_ai_message(context_info['description'])
                    st.session_state['memory'] = memory
                    system_message_just_added = True
            else:
                # If memory is None, initialize it to intro
                memory = intro
                st.session_state['memory'] = memory

        chain = st.session_state.get('Chain')

        # Check if chain is properly loaded
        if chain is None:
            st.error("⚠️ Model not properly loaded. Please check your API key and try again.")
            st.stop()

        # Product selector is now handled internally by the blog lab module

        # Display chat history (excluding the system message we just added to prevent duplication)
        # Skip chat history if in editor phase
        if not st.session_state.get('editor_phase_active', False):
            memory = st.session_state.get('memory', intro)
            if memory is not None:
                for message in memory.buffer_as_messages:
                    # Skip displaying the system message if we just added it to prevent duplication
                    if system_message_just_added and message.content == context_info['description'] and message.type == 'ai':
                        continue
                    chat = st.chat_message(message.type, avatar='👤' if message.type == 'human' else '🦊')
                    chat.markdown(message.content)

        # Check if we should hide chat input for SEO lab manual mode or editing phase
        hide_chat_input = False
        if chosen_function == 'seo_lab':
            # Hide chat input during manual mode, editor phase, or when themes are ready for editing
            hide_chat_input = (
                st.session_state.get('manual_mode_active', False) or
                st.session_state.get('editor_phase_active', False) or
                (st.session_state.get('themes_displayed', False) and 
                 st.session_state.get('themes') and 
                 st.session_state.get('seo_themes') and 
                 st.session_state.get('brief_summaries') and
                 not st.session_state.get('combined_brief_summary'))
            )
        
        # Only show chat input if not hidden
        if not hide_chat_input:
            # CRITICAL FIX: Ensure model is loaded before allowing chat interactions
            if 'Chain' not in st.session_state:
                st.warning(LANG['brand_context_model_not_loaded'])
                st.info(LANG['brand_context_model_auto_load'])
                return
            
            # Handle chat interaction (always at bottom)
            interaction = st.chat_input(LANG['chat_placeholder'], key="main_chat")
            if interaction:
                chat = st.chat_message('human', avatar='👤')
                chat.markdown(interaction)

                chat = st.chat_message('ai', avatar='🦊')
                try:
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
                except Exception as e:
                    st.error(f"Error in chat interaction: {str(e)}")
                    st.error("Please check your API key and try again.")

    else:
        # Only show "Como usar" expander if the context has the required fields
        if 'how_to_use_col1' in context_info and 'how_to_use_col2' in context_info:
            with st.expander("ℹ️ Como usar", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(context_info['how_to_use_col1'])
                with col2:
                    st.markdown(context_info['how_to_use_col2'])

    if chosen_function == 'seo_lab':
        # SEO Lab uses direct input interface - run the flow directly
        from chats.seo_lab._seo_lab import handle_seo_lab_flow
        # Run the SEO Lab flow with input interface (chain and memory not used in SEO lab)
        handle_seo_lab_flow(handle_chat_interaction, None, None)
    elif chosen_function == 'crm_lab':
        # Reset content generation flag when switching away from SEO lab
        if 'content_generation_started' in st.session_state:
            st.session_state['content_generation_started'] = False
        # Run the CRM Lab flow
        from chats.crm_lab._crm_lab import handle_crm_lab_flow
        handle_crm_lab_flow(handle_chat_interaction, chain, memory)
    elif chosen_function == 'copilot':
        # Reset content generation flag when switching away from SEO lab
        if 'content_generation_started' in st.session_state:
            st.session_state['content_generation_started'] = False
        from chats.copilot._copilot import handle_copilot_flow
        handle_copilot_flow(handle_chat_interaction, chain, memory)
    elif chosen_function == 'insighter':
        # Reset content generation flag when switching away from SEO lab
        if 'content_generation_started' in st.session_state:
            st.session_state['content_generation_started'] = False
        from chats.insighter._insighter import handle_insighter_flow
        handle_insighter_flow(handle_chat_interaction, chain, memory)
    elif chosen_function == 'geocommerce':
        # Reset content generation flag when switching away from SEO lab
        if 'content_generation_started' in st.session_state:
            st.session_state['content_generation_started'] = False
        # Import and run the GeoCommerce system
        from tools.geocommerce.geocommerce import GeoCommerceManualApp
        # Create app instance without initializing Streamlit config (already done in nami.py)
        app = GeoCommerceManualApp()
        # Run the app content without calling app.run() to avoid double page config
        app.render_geocommerce_content()
    elif chosen_function == 'rfmify':
        # Reset content generation flag when switching away from SEO lab
        if 'content_generation_started' in st.session_state:
            st.session_state['content_generation_started'] = False
        # Import and run the RFMify system
        from tools.rfmify.rfmify_core import handle_rfmify_flow
        handle_rfmify_flow()


if __name__ == "__main__":
    nami()