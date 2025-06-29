import json
import os
import re
import spacy
import sys

import streamlit as st

from docling_core.types import DoclingDocument
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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

def handle_oraculo_flow(chat_interaction, chain, memory):
    """
    Handle the oraculo-specific chat flow.
    Uses the centralized chat_interaction function for UI.
    """
    # Handle chat interaction
    response = chat_interaction('Como posso te ajudar hoje?', chain, memory, key="oraculo_chat")
    
    if response:
        process_oraculo_response(response)
        st.rerun()
