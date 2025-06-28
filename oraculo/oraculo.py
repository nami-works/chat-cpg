import json
import os
import re
import spacy
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import streamlit as st
from docling_core.types import DoclingDocument
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from unstructured.documents.elements import Element

# Absolute path for importing custom tools
tools_path = r'G:\Meu Drive\Pessoal\nAmI\ferramentas'

# Add to sys.path if not already present
if tools_path not in sys.path:
    sys.path.append(tools_path)

# Import tools
import leitor_arquivos as file_reader

# Loading spaCy model for text analysis
nlp = spacy.load("pt_core_news_md")

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
    
    # Extract key entities using spaCy
    document = nlp(text)
    extracted_entities = {}
    for entity in document.ents:
        if entity.label_ not in extracted_entities:
            extracted_entities[entity.label_] = []
        if entity.text not in extracted_entities[entity.label_]:
            extracted_entities[entity.label_].append(entity.text)
    
    # Identify main topics using keywords and phrases
    identified_topics = []
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

def get_brand_folders() -> List[str]:
    """
    Get list of available brand folders in z_brands directory.
    
    Returns:
    List[str]: List of brand folder names
    """
    brands_path = Path("z_brands")
    if not brands_path.exists():
        return []
    
    return [folder.name for folder in brands_path.iterdir() if folder.is_dir()]

def generate_comprehensive_title(content: str, entities: Dict, topics: List[str]) -> str:
    """
    Generate a comprehensive title based on extracted content analysis.
    
    Parameters:
    content (str): Processed content
    entities (Dict): Extracted entities
    topics (List[str]): Main topics identified
    
    Returns:
    str: Generated comprehensive title
    """
    # Extract key terms from entities and topics
    key_terms = []
    
    # Add organization/person names
    if 'ORG' in entities:
        key_terms.extend(entities['ORG'][:2])
    if 'PERSON' in entities:
        key_terms.extend(entities['PERSON'][:2])
    
    # Add main topics (first 2)
    key_terms.extend([topic.split('.')[0].strip() for topic in topics[:2]])
    
    # Clean and format key terms
    clean_terms = [term for term in key_terms if len(term) > 3][:3]
    
    if clean_terms:
        title = f"Base de Conhecimento: {' | '.join(clean_terms)}"
    else:
        title = f"Base de Conhecimento - Análise de Documentos"
    
    return title[:100]  # Limit title length

def create_or_update_knowledge_file(brand: str, content: str, metadata: dict, summary: str, entities: Dict, topics: List[str]):
    """
    Create or update knowledge file in the brand folder within z_brands.
    
    Parameters:
    brand (str): Brand name
    content (str): Processed content
    metadata (dict): File metadata
    summary (str): Content summary
    entities (Dict): Extracted entities
    topics (List[str]): Main topics
    """
    try:
        brand_path = Path("z_brands") / brand
        knowledge_file_path = brand_path / "base_conhecimento.md"
        
        # Ensure brand directory exists
        brand_path.mkdir(parents=True, exist_ok=True)
        
        # Check if knowledge file exists and has substantial content
        file_exists = knowledge_file_path.exists()
        has_content = False
        
        if file_exists:
            with open(knowledge_file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read().strip()
                has_content = len(existing_content) > 50 and "nothing to see here" not in existing_content.lower()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Filter entities
        filtered_entities = {k: filter_categories({e: k for e in v}) for k, v in entities.items()}
        
        # Prepare new content section
        new_section = f"""
## 📄 Análise de Documento - {timestamp}

**Fonte:** {metadata.get('filename', 'Arquivo carregado')}

### 📋 Resumo Executivo
{summary}

### 🎯 Tópicos Principais
"""
        for i, topic in enumerate(topics, 1):
            new_section += f"{i}. {topic}\n"
        
        new_section += f"""
### 🔍 Entidades Identificadas
```json
{json.dumps(filtered_entities, indent=2, ensure_ascii=False)}
```

### 📚 Conteúdo Completo
<details>
<summary>Expandir para ver o conteúdo completo</summary>

{content}

</details>

---

"""
        
        if not file_exists or not has_content:
            # Create new knowledge file with comprehensive title
            title = generate_comprehensive_title(content, entities, topics)
            
            with open(knowledge_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"*Base de conhecimento criada em: {timestamp}*\n\n")
                f.write("---\n")
                f.write(new_section)
            
            st.success(f"✅ Nova base de conhecimento criada para a marca **{brand}**")
        else:
            # Append to existing knowledge file
            with open(knowledge_file_path, 'a', encoding='utf-8') as f:
                f.write(new_section)
            
            st.success(f"✅ Base de conhecimento atualizada para a marca **{brand}**")
        
        # Display file path for reference
        st.info(f"📂 Arquivo atualizado: `{knowledge_file_path}`")
        
    except Exception as error:
        st.error(f"❌ Erro ao criar/atualizar base de conhecimento: {error}")

def process_uploaded_files(uploaded_files, selected_brand: str):
    """
    Process multiple uploaded files and update knowledge base.
    
    Parameters:
    uploaded_files: Streamlit uploaded files
    selected_brand (str): Selected brand for knowledge base update
    """
    if not uploaded_files:
        st.warning("⚠️ Nenhum arquivo foi carregado.")
        return
    
    if not selected_brand:
        st.warning("⚠️ Por favor, selecione uma marca.")
        return
    
    progress_bar = st.progress(0)
    progress_text = st.empty()
    
    total_files = len(uploaded_files)
    processed_files = 0
    
    st.write(f"🔄 Processando {total_files} arquivo(s) para a marca **{selected_brand}**...")
    
    for uploaded_file in uploaded_files:
        try:
            progress_text.text(f"Processando: {uploaded_file.name}")
            
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process file using existing file reader
            extracted_content = file_reader.load_input(temp_path)
            
            # Extract relevant information
            summary, entities, topics = extract_relevant_information(extracted_content)
            
            # Create metadata
            file_metadata = {
                "filename": uploaded_file.name,
                "size": uploaded_file.size,
                "type": uploaded_file.type,
                "processed_at": datetime.now().isoformat()
            }
            
            # Update knowledge base
            create_or_update_knowledge_file(
                selected_brand, 
                extracted_content, 
                file_metadata, 
                summary, 
                entities, 
                topics
            )
            
            # Clean up temporary file
            os.remove(temp_path)
            
            processed_files += 1
            progress_bar.progress(processed_files / total_files)
            
        except Exception as error:
            st.error(f"❌ Erro ao processar {uploaded_file.name}: {error}")
            # Clean up temporary file if it exists
            temp_path = f"temp_{uploaded_file.name}"
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    progress_text.text("✅ Processamento concluído!")
    st.balloons()

def update_knowledge_base(result: str, metadata: dict, save_path=None):
    """
    Legacy function maintained for compatibility.
    Updates the consolidated knowledge base in a .md file with the new processed result,
    applying noise filtering on categories and organizing relevant information.

    Parameters:
    result (str): Extracted text.
    metadata (dict): Document associated metadata.
    save_path (str): Path to the consolidated knowledge base file.
    """
    if save_path is None:
        save_path = "knowledge_base.md"
    
    try:
        # Extract key information
        text_summary, entity_list, topic_list = extract_relevant_information(result)
        
        # Filter out noise from categories
        filtered_entity_list = {k: filter_categories({e: k for e in v}) for k, v in entity_list.items()}
        
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

def process_oraculo_response(response: str):
    """
    Process the oracle's response and update the knowledge base if needed.
    This function is called when the oracle generates a response.
    """
    try:
        # Add any specific processing for oracle responses here
        # For example, you might want to:
        # - Extract specific patterns
        # - Update knowledge base
        # - Generate additional metadata
        st.session_state['resposta_oraculo'] = response
    except Exception as error:
        st.error(f"Error processing oracle response: {error}")

def handle_oraculo_flow(chat_interaction, chain, memory):
    """
    Handle the oraculo-specific chat flow.
    Uses the centralized chat_interaction function for UI.
    """
    st.title("🔮 Oráculo - Processador de Conhecimento")
    
    # Get available brands
    available_brands = get_brand_folders()
    
    # File upload and processing UI
    with st.expander("📁 Processar Arquivos de Conhecimento", expanded=True):
        st.markdown("### Upload de Arquivos")
        st.markdown("Carregue um ou múltiplos arquivos para análise e processamento.")
        
        # Brand selection
        if available_brands:
            selected_brand = st.selectbox(
                "Selecione a marca:",
                options=[""] + available_brands,
                help="Escolha a marca para a qual os arquivos serão processados"
            )
        else:
            st.warning("⚠️ Nenhuma marca encontrada na pasta z_brands. Criando nova marca...")
            selected_brand = st.text_input(
                "Nome da nova marca:",
                placeholder="Digite o nome da marca"
            )
        
        # File upload
        uploaded_files = st.file_uploader(
            "Escolha os arquivos:",
            accept_multiple_files=True,
            type=['pdf', 'docx', 'doc', 'txt', 'md', 'html', 'xml', 'csv', 'xlsx', 'xls'],
            help="Suporte para: PDF, Word, Texto, Markdown, HTML, XML, CSV, Excel"
        )
        
        # Display uploaded files info
        if uploaded_files:
            st.markdown("#### Arquivos Carregados:")
            for file in uploaded_files:
                file_size = file.size / 1024  # Convert to KB
                st.write(f"- **{file.name}** ({file_size:.1f} KB) - {file.type}")
        
        # Process button
        if st.button("🚀 Processar Arquivos", type="primary"):
            if uploaded_files and selected_brand:
                process_uploaded_files(uploaded_files, selected_brand)
            else:
                st.error("❌ Por favor, carregue arquivos e selecione uma marca.")
    
    # Legacy directory scanning (kept for backward compatibility)
    with st.expander("📂 Processar Diretório (Legacy)"):
        st.markdown("### Escaneamento de Diretório")
        directory_path = st.text_input("Digite o caminho do diretório para escanear:",
                                     placeholder="e.g., C:/Users/Documents")

        if st.button("Iniciar Escaneamento"):
            if not directory_path:
                st.warning("⚠️ Por favor, digite um caminho de diretório")
                return

            found_files = scan_directory(directory_path)

            if not found_files:
                st.warning(f"⚠️ Nenhum arquivo encontrado no diretório: {directory_path}")
                return

            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            total_files = len(found_files)
            processed_files = 0
            
            for file_path in found_files:
                try:
                    processed_result = file_reader.load_input(file_path)
                    file_metadata = {"source": file_path}
                    update_knowledge_base(processed_result, file_metadata)
                    
                    processed_files += 1
                    progress_bar.progress(processed_files / total_files)
                    progress_text.text(f"Processando arquivos... ({processed_files}/{total_files})")
                    
                except Exception as error:
                    st.error(f"❌ Erro ao processar arquivo {file_path}: {error}")

            progress_text.text("✅ Processamento concluído!")

    # Knowledge base viewer
    with st.expander("📊 Visualizar Base de Conhecimento"):
        if available_brands:
            view_brand = st.selectbox(
                "Selecione a marca para visualizar:",
                options=[""] + available_brands,
                key="view_brand"
            )
            
            if view_brand:
                knowledge_file = Path("z_brands") / view_brand / "base_conhecimento.md"
                if knowledge_file.exists():
                    with open(knowledge_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    st.markdown("#### Conteúdo da Base de Conhecimento:")
                    st.markdown(content)
                    
                    # Download button
                    st.download_button(
                        label="📥 Baixar Base de Conhecimento",
                        data=content,
                        file_name=f"{view_brand}_base_conhecimento.md",
                        mime="text/markdown"
                    )
                else:
                    st.info("ℹ️ Base de conhecimento ainda não existe para esta marca.")

    # Handle chat interaction
    st.markdown("### 💬 Chat com o Oráculo")
    response = chat_interaction('Como posso te ajudar hoje?', chain, memory, key="oraculo_chat")
    
    if response:
        process_oraculo_response(response)
        st.rerun()
