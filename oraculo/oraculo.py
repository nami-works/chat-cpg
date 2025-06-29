import json
import os
import re
import spacy
import sys
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from docling_core.types import DoclingDocument
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from typing import Dict, List, Optional, Tuple
from unstructured.documents.elements import Element

# Absolute path for importing custom tools
tools_path = r'G:\Meu Drive\Pessoal\nAmI\ferramentas'

# Add to sys.path if not already present
if tools_path not in sys.path:
    sys.path.append(tools_path)

# Import tools
import leitor_arquivos as file_reader

# Get the absolute path to the project root
base_dir = Path(__file__).resolve().parent.parent

# Add the project root to Python path
if str(base_dir) not in sys.path:
    sys.path.append(str(base_dir))

# Import the file_reader from the project
sys.path.append(str(base_dir))
import file_reader as project_file_reader

# Loading spaCy model for text analysis
try:
    nlp = spacy.load("pt_core_news_md")
except OSError:
    st.warning("Portuguese spaCy model not found. Using English model instead.")
    nlp = spacy.load("en_core_web_sm")

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

def extract_data_statistics(text: str) -> List[str]:
    """
    Extract statistical data and numbers from text.
    
    Parameters:
    text (str): Text to analyze
    
    Returns:
    List[str]: List of statistical information found
    """
    data_patterns = [
        r'\d+%',  # Percentages
        r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Money values
        r'\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|thousand|milhão|bilhão|mil))?',  # Large numbers
        r'\d+(?:\.\d+)?\s*(?:kg|g|ml|l|cm|m|km)',  # Measurements
        r'(?:increased|decreased|cresceu|diminuiu)\s+(?:by\s+)?\d+%',  # Growth/decline rates
    ]
    
    statistics = []
    for pattern in data_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        statistics.extend(matches)
    
    # Also look for sentences containing numerical data
    sentences = text.split('.')
    for sentence in sentences:
        if re.search(r'\d+', sentence) and any(keyword in sentence.lower() for keyword in 
                                              ['revenue', 'profit', 'sales', 'growth', 'market', 'share', 
                                               'receita', 'lucro', 'vendas', 'crescimento', 'mercado', 'participação']):
            statistics.append(sentence.strip())
    
    return list(set(statistics))[:10]  # Remove duplicates and limit to 10

def process_uploaded_files(uploaded_files: List, brand_id: str = "gebeauty") -> Optional[str]:
    """
    Process uploaded files and extract knowledge.
    
    Parameters:
    uploaded_files (List): List of uploaded files from Streamlit
    brand_id (str): Brand identifier for organizing files
    
    Returns:
    str: Path to the generated new_knowledge.md file
    """
    if not uploaded_files:
        return None
    
    all_extracted_content = []
    all_summaries = []
    all_entities = {}
    all_statistics = []
    
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        try:
            # Extract content using file_reader
            content = project_file_reader.load_input(uploaded_file, uploaded_file.name)
            
            # Extract relevant information
            summary, entities, topics = extract_relevant_information(content)
            statistics = extract_data_statistics(content)
            
            all_extracted_content.append({
                'filename': uploaded_file.name,
                'content': content,
                'summary': summary,
                'topics': topics
            })
            
            all_summaries.append(f"**{uploaded_file.name}**: {summary}")
            
            # Merge entities
            for entity_type, entity_list in entities.items():
                if entity_type not in all_entities:
                    all_entities[entity_type] = []
                all_entities[entity_type].extend(entity_list)
            
            all_statistics.extend(statistics)
            
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")
            continue
    
    # Generate comprehensive title
    file_names = [f['filename'] for f in all_extracted_content]
    title = f"Knowledge Base Update - {datetime.now().strftime('%Y-%m-%d %H:%M')} - Files: {', '.join(file_names)}"
    
    # Create new_knowledge.md content
    knowledge_content = f"""# {title}

## **SUMMARY**
{chr(10).join(all_summaries)}

## **ANALYTICAL VERSION**
"""
    
    # Add analytical content for each file
    for file_data in all_extracted_content:
        knowledge_content += f"""
### Analysis of {file_data['filename']}

**Summary**: {file_data['summary']}

**Main Topics Identified**:
"""
        for topic in file_data['topics']:
            knowledge_content += f"- {topic}\n"
        
        knowledge_content += f"""
**Key Content**:
{file_data['content'][:2000]}{'...' if len(file_data['content']) > 2000 else ''}

---
"""
    
    # Add entities section
    knowledge_content += f"""
**Entities Identified**:
```json
{json.dumps(all_entities, indent=2, ensure_ascii=False)}
```

## **DATA**
"""
    
    # Add statistics section
    if all_statistics:
        knowledge_content += "**Statistical Information Found**:\n"
        for stat in set(all_statistics):  # Remove duplicates
            knowledge_content += f"- {stat}\n"
    else:
        knowledge_content += "No statistical data identified in the uploaded files.\n"
    
    knowledge_content += f"""
**Processing Details**:
- Number of files processed: {len(uploaded_files)}
- Total content length: {sum(len(f['content']) for f in all_extracted_content)} characters
- Processing timestamp: {datetime.now().isoformat()}
"""
    
    # Save new_knowledge.md
    temp_knowledge_path = base_dir / 'new_knowledge.md'
    with open(temp_knowledge_path, 'w', encoding='utf-8') as f:
        f.write(knowledge_content)
    
    return str(temp_knowledge_path)

def merge_knowledge_files(new_knowledge_path: str, brand_id: str = "gebeauty") -> None:
    """
    Merge new knowledge with existing knowledge base or create new one.
    
    Parameters:
    new_knowledge_path (str): Path to the new_knowledge.md file
    brand_id (str): Brand identifier
    """
    brand_folder = base_dir / 'z_brands' / brand_id
    existing_knowledge_path = brand_folder / 'knowledge.md'
    
    # Ensure brand folder exists
    os.makedirs(brand_folder, exist_ok=True)
    
    # Read new knowledge content
    with open(new_knowledge_path, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    # Extract sections from new content
    new_title_match = re.search(r'^# (.+?)$', new_content, re.MULTILINE)
    new_title = new_title_match.group(1) if new_title_match else "Unknown Title"
    
    new_summary_match = re.search(r'## \*\*SUMMARY\*\*\s*\n(.*?)(?=## \*\*ANALYTICAL VERSION\*\*)', 
                                 new_content, re.DOTALL)
    new_summary = new_summary_match.group(1).strip() if new_summary_match else ""
    
    new_analytical_match = re.search(r'## \*\*ANALYTICAL VERSION\*\*(.*?)## \*\*DATA\*\*', 
                                    new_content, re.DOTALL)
    new_analytical = new_analytical_match.group(1).strip() if new_analytical_match else ""
    
    new_data_match = re.search(r'## \*\*DATA\*\*(.*?)$', new_content, re.DOTALL)
    new_data = new_data_match.group(1).strip() if new_data_match else ""
    
    if not existing_knowledge_path.exists():
        # Create new knowledge.md file
        shutil.copy2(new_knowledge_path, existing_knowledge_path)
        st.success(f"✅ Created new knowledge base at {existing_knowledge_path}")
    else:
        # Merge with existing knowledge.md
        with open(existing_knowledge_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Find the end of the SUMMARY section
        summary_end_pattern = r'(## \*\*SUMMARY\*\*.*?)(\n## \*\*ANALYTICAL VERSION\*\*)'
        summary_match = re.search(summary_end_pattern, existing_content, re.DOTALL)
        
        if summary_match:
            # Insert new title and summary at the end of existing summary
            existing_summary = summary_match.group(1)
            rest_of_content = existing_content[summary_match.end(1):]
            
            updated_summary = f"{existing_summary}\n\n### {new_title}\n{new_summary}"
            updated_content = f"{updated_summary}{rest_of_content}\n\n## **NEW ANALYTICAL SECTION - {datetime.now().strftime('%Y-%m-%d %H:%M')}**\n{new_analytical}\n\n## **NEW DATA SECTION - {datetime.now().strftime('%Y-%m-%d %H:%M')}**\n{new_data}"
        else:
            # If the existing file doesn't have the expected structure, append everything
            updated_content = f"{existing_content}\n\n---\n\n# {new_title}\n\n## **SUMMARY**\n{new_summary}\n\n## **ANALYTICAL VERSION**\n{new_analytical}\n\n## **DATA**\n{new_data}"
        
        # Write updated content
        with open(existing_knowledge_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        st.success(f"✅ Updated existing knowledge base at {existing_knowledge_path}")
    
    # Delete the temporary new_knowledge.md file
    try:
        os.remove(new_knowledge_path)
        st.info("🧹 Cleaned up temporary files")
    except Exception as e:
        st.warning(f"Could not remove temporary file: {e}")

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

def update_knowledge_base(result: str, metadata: dict, save_path):
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

def handle_file_upload_flow():
    """
    Handle the file upload and knowledge extraction flow.
    """
    st.header("📁 Knowledge Base File Upload")
    
    # Brand selection
    available_brands = [d for d in (base_dir / 'z_brands').iterdir() if d.is_dir()]
    brand_names = [brand.name for brand in available_brands]
    
    if not brand_names:
        st.error("No brand folders found in z_brands directory")
        return
    
    selected_brand = st.selectbox(
        "Select Brand:",
        brand_names,
        index=0 if "gebeauty" not in brand_names else brand_names.index("gebeauty")
    )
    
    # File upload interface
    uploaded_files = st.file_uploader(
        "Upload files to extract knowledge from:",
        type=['pdf', 'txt', 'docx', 'doc', 'csv', 'xlsx', 'xls', 'json', 'md', 'pptx', 'ppt'],
        accept_multiple_files=True,
        help="Supported formats: PDF, Word, Excel, PowerPoint, Text, CSV, JSON, Markdown"
    )
    
    if uploaded_files:
        st.info(f"📊 {len(uploaded_files)} file(s) selected for processing")
        
        # Show file details
        with st.expander("📋 File Details"):
            for file in uploaded_files:
                st.write(f"- **{file.name}** ({file.size:,} bytes)")
        
        # Process files button
        if st.button("🚀 Process Files and Update Knowledge Base", type="primary"):
            with st.spinner("Processing files and extracting knowledge..."):
                try:
                    # Process uploaded files
                    new_knowledge_path = process_uploaded_files(uploaded_files, selected_brand)
                    
                    if new_knowledge_path:
                        # Merge with existing knowledge base
                        merge_knowledge_files(new_knowledge_path, selected_brand)
                        
                        # Show success message and download option
                        st.success("✅ Files processed successfully!")
                        
                        # Provide link to view updated knowledge base
                        knowledge_path = base_dir / 'z_brands' / selected_brand / 'knowledge.md'
                        if knowledge_path.exists():
                            with open(knowledge_path, 'r', encoding='utf-8') as f:
                                updated_content = f.read()
                            
                            st.download_button(
                                label="📥 Download Updated Knowledge Base",
                                data=updated_content,
                                file_name=f"{selected_brand}_knowledge_base.md",
                                mime="text/markdown"
                            )
                    else:
                        st.error("❌ Failed to process files")
                        
                except Exception as e:
                    st.error(f"❌ Error processing files: {e}")

def handle_oraculo_flow(chat_interaction, chain, memory):
    """
    Handle the oraculo-specific chat flow.
    Uses the centralized chat_interaction function for UI.
    """
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["💬 Chat", "📁 File Upload"])
    
    with tab1:
        # Render file processing UI (legacy directory scanning)
        with st.expander("🗂️ Legacy Directory Processing"):
            directory_path = st.text_input("Enter the directory path to scan:",
                                         placeholder="e.g., C:/Users/Documents")

            if st.button("Start Scanning"):
                if not directory_path:
                    st.warning("⚠️ Please enter a directory path")
                    return

                found_files = scan_directory(directory_path)

                if not found_files:
                    st.warning(f"⚠️ No files found in directory: {directory_path}")
                    return

                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                                 total_files = len(found_files)
                 processed_files = 0
                 
                 for file_path in found_files:
                     try:
                         with open(file_path, 'rb') as f:
                             processed_result = project_file_reader.load_input(f, os.path.basename(file_path))
                         file_metadata = {"source": file_path}
                         update_knowledge_base(processed_result, file_metadata, base_dir / 'legacy_knowledge.md')
                        
                        processed_files += 1
                        progress_bar.progress(processed_files / total_files)
                        progress_text.text(f"Processing files... ({processed_files}/{total_files})")
                        
                    except Exception as error:
                        st.error(f"❌ Error processing file {file_path}: {error}")

                progress_text.text("✅ Processing completed!")

        # Handle chat interaction
        response = chat_interaction('Como posso te ajudar hoje?', chain, memory, key="oraculo_chat")
        
        if response:
            process_oraculo_response(response)
            st.rerun()
    
    with tab2:
        # Handle file upload flow
        handle_file_upload_flow()
