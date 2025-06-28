import json
import os
import re
import shutil
import spacy
import sys
from io import StringIO

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
try:
    import leitor_arquivos as file_reader
except (ImportError, ModuleNotFoundError):
    file_reader = None
    print("File reader module not available. Some features may be limited.")

# Loading spaCy model for text analysis
try:
    nlp = spacy.load("pt_core_news_md")
except (OSError, IOError):
    print("Portuguese spaCy model not found. Install with: python -m spacy download pt_core_news_md")
    nlp = None

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

def extract_text_from_uploaded_file(uploaded_file) -> str:
    """
    Extract text content from uploaded file.
    
    Parameters:
    uploaded_file: Streamlit uploaded file object
    
    Returns:
    str: Extracted text content
    """
    try:
        if uploaded_file.type == "text/plain":
            # Handle text files
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            return stringio.read()
        elif uploaded_file.type == "application/pdf":
            # Handle PDF files (basic implementation)
            try:
                import PyPDF2
                from io import BytesIO
                
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                st.error("PyPDF2 not installed. Cannot process PDF files.")
                return ""
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            # Handle Word documents
            try:
                import docx
                from io import BytesIO
                
                doc = docx.Document(BytesIO(uploaded_file.getvalue()))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                st.error("python-docx not installed. Cannot process Word documents.")
                return ""
        else:
            # Try reading as text for other formats
            try:
                return uploaded_file.getvalue().decode("utf-8")
            except UnicodeDecodeError:
                st.error(f"Unable to read file {uploaded_file.name}. Unsupported format or encoding.")
                return ""
    except Exception as e:
        st.error(f"Error extracting text from {uploaded_file.name}: {str(e)}")
        return ""

def extract_comprehensive_knowledge(text: str, filename: str = "unknown") -> Dict:
    """
    Extracts comprehensive knowledge from text using advanced NLP and LLM analysis.
    
    Parameters:
    text (str): Input text to analyze
    filename (str): Name of the source file
    
    Returns:
    Dict: Comprehensive knowledge structure
    """
    try:
        # Initialize LLM for analysis
        llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o-mini")
        
        # Split text into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=300
        )
        text_chunks = text_splitter.split_text(text)
        
        # Generate comprehensive summary
        summarization_chain = load_summarize_chain(llm, chain_type="map_reduce")
        summary = summarization_chain.run(text_chunks)
        
        # Extract entities using spaCy if available
        entities = {}
        topics = []
        
        if nlp:
            doc = nlp(text[:10000])  # Limit to first 10k chars for performance
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                if ent.text not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text)
            
            # Extract key topics from sentences
            for sent in doc.sents:
                if len(sent.text.strip()) > 20 and any(token.pos_ in ["NOUN", "PROPN"] for token in sent):
                    topics.append(sent.text.strip())
        
        # Generate analytical version using LLM
        analytical_prompt = f"""
        Analyze the following text comprehensively and provide a structured analytical version:
        
        Text: {text[:5000]}...
        
        Please provide:
        1. Main themes and concepts
        2. Key insights and findings
        3. Methodologies or approaches mentioned
        4. Important conclusions or recommendations
        5. Relationships between different concepts
        
        Format your response in a clear, structured manner.
        """
        
        analytical_version = llm.invoke(analytical_prompt).content
        
        # Extract statistical data using pattern matching
        data_patterns = [
            r'\d+%',  # Percentages
            r'\d+\.\d+%',  # Decimal percentages
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Currency
            r'\d+(?:,\d{3})*',  # Large numbers with commas
            r'\d+\.\d+',  # Decimal numbers
        ]
        
        statistical_data = []
        for pattern in data_patterns:
            matches = re.findall(pattern, text)
            statistical_data.extend(matches)
        
        # Remove duplicates and limit
        statistical_data = list(set(statistical_data))[:20]
        
        return {
            'filename': filename,
            'summary': summary,
            'analytical_version': analytical_version,
            'entities': entities,
            'topics': topics[:10],  # Limit topics
            'statistical_data': statistical_data,
            'word_count': len(text.split()),
            'char_count': len(text)
        }
        
    except Exception as e:
        st.error(f"Error in comprehensive knowledge extraction: {str(e)}")
        return {
            'filename': filename,
            'summary': f"Error extracting summary: {str(e)}",
            'analytical_version': f"Error in analysis: {str(e)}",
            'entities': {},
            'topics': [],
            'statistical_data': [],
            'word_count': len(text.split()) if text else 0,
            'char_count': len(text) if text else 0
        }

def generate_new_knowledge_md(knowledge_data: List[Dict]) -> str:
    """
    Generate a comprehensive new_knowledge.md file from extracted knowledge data.
    
    Parameters:
    knowledge_data (List[Dict]): List of knowledge dictionaries from processed files
    
    Returns:
    str: Formatted markdown content for new_knowledge.md
    """
    if not knowledge_data:
        return "# No Knowledge Extracted\n\nNo valid knowledge data was processed."
    
    # Generate comprehensive title
    filenames = [kd['filename'] for kd in knowledge_data]
    if len(filenames) == 1:
        title = f"Knowledge Extracted from {filenames[0]}"
    else:
        title = f"Comprehensive Knowledge Base from {len(filenames)} Documents"
    
    # Combine all summaries
    combined_summary = "\n\n".join([kd['summary'] for kd in knowledge_data if kd['summary']])
    
    # Combine analytical versions
    combined_analytical = "\n\n---\n\n".join([
        f"**Source: {kd['filename']}**\n\n{kd['analytical_version']}" 
        for kd in knowledge_data if kd['analytical_version']
    ])
    
    # Combine all statistical data
    all_stats = []
    for kd in knowledge_data:
        all_stats.extend(kd['statistical_data'])
    unique_stats = list(set(all_stats))
    
    # Create the markdown content
    md_content = f"""# {title}

## SUMMARY

{combined_summary}

## ANALYTICAL VERSION

{combined_analytical}

## DATA

### Statistical Information Found:
"""
    
    if unique_stats:
        for stat in unique_stats:
            md_content += f"- {stat}\n"
    else:
        md_content += "- No statistical data found in the processed files\n"
    
    # Add metadata section
    md_content += f"""
### Processing Metadata:
- **Total Files Processed**: {len(knowledge_data)}
- **Total Word Count**: {sum(kd['word_count'] for kd in knowledge_data)}
- **Total Character Count**: {sum(kd['char_count'] for kd in knowledge_data)}
- **Files**: {', '.join(filenames)}

### Entities Extracted:
"""
    
    # Combine entities from all files
    all_entities = {}
    for kd in knowledge_data:
        for entity_type, entity_list in kd['entities'].items():
            if entity_type not in all_entities:
                all_entities[entity_type] = []
            all_entities[entity_type].extend(entity_list)
    
    # Remove duplicates from entities
    for entity_type in all_entities:
        all_entities[entity_type] = list(set(all_entities[entity_type]))
    
    if all_entities:
        for entity_type, entities in all_entities.items():
            md_content += f"**{entity_type}**: {', '.join(entities[:10])}\n"  # Limit to 10 per type
    else:
        md_content += "No named entities were extracted from the files.\n"
    
    return md_content

def manage_knowledge_file(new_knowledge_content: str, brand_folder: Path) -> bool:
    """
    Manage the knowledge.md file in the brand folder according to the specified rules.
    
    Parameters:
    new_knowledge_content (str): Content of the new_knowledge.md file
    brand_folder (Path): Path to the brand folder
    
    Returns:
    bool: True if successful, False otherwise
    """
    try:
        # Ensure brand folder exists
        brand_folder.mkdir(parents=True, exist_ok=True)
        
        knowledge_file = brand_folder / 'knowledge.md'
        new_knowledge_file = brand_folder / 'new_knowledge.md'
        
        # First, save the new_knowledge.md file
        with open(new_knowledge_file, 'w', encoding='utf-8') as f:
            f.write(new_knowledge_content)
        
        if not knowledge_file.exists():
            # If knowledge.md doesn't exist, copy new_knowledge.md to knowledge.md
            shutil.copy(new_knowledge_file, knowledge_file)
            os.remove(new_knowledge_file)  # Delete new_knowledge.md
            st.success(f"✅ Created new knowledge.md file in {brand_folder.name}")
        else:
            # If knowledge.md exists, append the new content
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Extract TITLE and SUMMARY from new_knowledge.md
            new_lines = new_knowledge_content.split('\n')
            title_line = ""
            summary_content = ""
            analytical_and_data = ""
            
            in_summary = False
            in_analytical = False
            
            for line in new_lines:
                if line.startswith('# '):
                    title_line = line
                elif line.startswith('## SUMMARY'):
                    in_summary = True
                    in_analytical = False
                    continue
                elif line.startswith('## ANALYTICAL VERSION'):
                    in_summary = False
                    in_analytical = True
                    analytical_and_data += line + '\n'
                    continue
                elif line.startswith('## DATA'):
                    in_summary = False
                    in_analytical = True
                    analytical_and_data += line + '\n'
                    continue
                elif in_summary:
                    summary_content += line + '\n'
                elif in_analytical:
                    analytical_and_data += line + '\n'
            
            # Find the end of SUMMARY section in existing content
            existing_lines = existing_content.split('\n')
            updated_content = []
            in_existing_summary = False
            summary_ended = False
            
            for line in existing_lines:
                if line.startswith('## SUMMARY'):
                    in_existing_summary = True
                    updated_content.append(line)
                elif line.startswith('## ') and in_existing_summary:
                    # End of summary section, add new title and summary
                    if title_line and summary_content:
                        updated_content.append(f"\n### {title_line[2:].strip()}")  # Remove # and add as subsection
                        updated_content.append(summary_content.strip())
                    updated_content.append(line)
                    in_existing_summary = False
                    summary_ended = True
                else:
                    updated_content.append(line)
            
            # If we didn't find a summary section, add everything at the end
            if not summary_ended and title_line and summary_content:
                updated_content.append(f"\n### {title_line[2:].strip()}")
                updated_content.append(summary_content.strip())
            
            # Add analytical version and data at the end
            if analytical_and_data:
                updated_content.append(f"\n{analytical_and_data.strip()}")
            
            # Write updated content back to knowledge.md
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(updated_content))
            
            # Remove the temporary new_knowledge.md file
            os.remove(new_knowledge_file)
            st.success(f"✅ Updated existing knowledge.md file in {brand_folder.name}")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error managing knowledge file: {str(e)}")
        return False

def process_uploaded_files(uploaded_files: List, brand_folder: Path) -> bool:
    """
    Process uploaded files and create/update knowledge base.
    
    Parameters:
    uploaded_files (List): List of uploaded Streamlit file objects
    brand_folder (Path): Path to the brand folder
    
    Returns:
    bool: True if successful, False otherwise
    """
    if not uploaded_files:
        st.warning("⚠️ No files uploaded")
        return False
    
    try:
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        knowledge_data = []
        total_files = len(uploaded_files)
        
        for i, uploaded_file in enumerate(uploaded_files):
            progress_text.text(f"Processing {uploaded_file.name}... ({i+1}/{total_files})")
            
            # Extract text from uploaded file
            extracted_text = extract_text_from_uploaded_file(uploaded_file)
            
            if extracted_text:
                # Extract comprehensive knowledge
                knowledge = extract_comprehensive_knowledge(extracted_text, uploaded_file.name)
                knowledge_data.append(knowledge)
                
                st.write(f"✅ Processed: {uploaded_file.name} ({knowledge['word_count']} words)")
            else:
                st.write(f"⚠️ Could not extract text from: {uploaded_file.name}")
            
            progress_bar.progress((i + 1) / total_files)
        
        if knowledge_data:
            # Generate new_knowledge.md content
            new_knowledge_content = generate_new_knowledge_md(knowledge_data)
            
            # Manage knowledge file
            success = manage_knowledge_file(new_knowledge_content, brand_folder)
            
            progress_text.text("✅ Processing completed!")
            return success
        else:
            st.error("❌ No knowledge could be extracted from the uploaded files")
            return False
            
    except Exception as e:
        st.error(f"❌ Error processing uploaded files: {str(e)}")
        return False

def handle_oraculo_flow(chat_interaction, chain, memory):
    """
    Handle the oraculo-specific chat flow with enhanced file upload capabilities.
    Uses the centralized chat_interaction function for UI.
    """
    # Get brand context
    context = st.session_state.get('context', {})
    brand_id = context.get('brand_id', 'gebeauty')  # Default to gebeauty
    
    # Create brand folder path
    base_dir = Path(__file__).resolve().parent.parent  # Go up to main directory
    brand_folder = base_dir / 'z_brands' / brand_id
    
    # Enhanced file processing UI
    with st.expander("📁 Upload and Process Knowledge Files", expanded=True):
        st.write("Upload files to extract and process knowledge for the brand's knowledge base.")
        
        # File uploader for multiple files
        uploaded_files = st.file_uploader(
            "Choose files to process",
            type=['txt', 'pdf', 'docx', 'doc', 'md'],
            accept_multiple_files=True,
            help="Supported formats: TXT, PDF, DOCX, DOC, MD"
        )
        
        if uploaded_files:
            st.write(f"📄 Selected {len(uploaded_files)} file(s):")
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.size} bytes)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Process Files", disabled=not uploaded_files, use_container_width=True):
                if uploaded_files:
                    with st.spinner("Processing files and extracting knowledge..."):
                        success = process_uploaded_files(uploaded_files, brand_folder)
                        if success:
                            st.balloons()
                            st.success("🎉 Knowledge extraction completed successfully!")
                        else:
                            st.error("❌ Failed to process files")
        
        with col2:
            # Directory scanning (legacy functionality)
            with st.popover("📂 Scan Directory (Legacy)"):
                directory_path = st.text_input("Enter directory path to scan:",
                                             placeholder="e.g., C:/Users/Documents")
                
                if st.button("Start Directory Scan"):
                    if not directory_path:
                        st.warning("⚠️ Please enter a directory path")
                    else:
                        found_files = scan_directory(directory_path)
                        
                        if not found_files:
                            st.warning(f"⚠️ No files found in directory: {directory_path}")
                        else:
                            st.write(f"Found {len(found_files)} files. Processing...")
                            # Process directory files using legacy method
                            # This maintains backward compatibility
                            for file_path in found_files:
                                try:
                                    if file_reader:
                                        processed_result = file_reader.load_input(file_path)
                                        file_metadata = {"source": file_path}
                                        update_knowledge_base(processed_result, file_metadata, 
                                                           brand_folder / 'legacy_knowledge.md')
                                except Exception as error:
                                    st.error(f"❌ Error processing file {file_path}: {error}")
    
    # Display current knowledge base info
    knowledge_file = brand_folder / 'knowledge.md'
    if knowledge_file.exists():
        with st.expander("📚 Current Knowledge Base Info"):
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
                    char_count = len(content)
                    
                st.metric("Word Count", word_count)
                st.metric("Character Count", char_count)
                st.metric("File Size", f"{knowledge_file.stat().st_size} bytes")
                
                if st.checkbox("Show preview"):
                    st.text_area("Knowledge Base Preview", content[:1000] + "..." if len(content) > 1000 else content, height=200)
            except Exception as e:
                st.error(f"Error reading knowledge base: {e}")
    else:
        st.info("📝 No knowledge base exists yet. Upload files to create one!")

    # Handle chat interaction
    response = chat_interaction('Como posso te ajudar hoje?', chain, memory, key="oraculo_chat")
    
    if response:
        process_oraculo_response(response)
        st.rerun()
