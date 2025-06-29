# Knowledge Base Functionality

## Overview

The ChatCPG system now includes a comprehensive knowledge base functionality that allows users to upload and process documents to create a centralized knowledge repository for each brand.

## Features

### 📁 File Upload
- **Supported Formats**: PDF, TXT, DOC, DOCX, CSV, XLSX, JSON, MD
- **Multiple Files**: Upload multiple files simultaneously
- **Progress Tracking**: Real-time progress bar and status updates

### 📂 Directory Scanning
- **Batch Processing**: Scan entire directories for compatible files
- **Automatic Detection**: Automatically identifies and processes supported file types
- **Error Handling**: Gracefully handles unsupported files with warnings

### 🧠 Intelligent Processing
- **NLP Analysis**: Uses spaCy for entity extraction and topic identification
- **LLM Summarization**: Generates intelligent summaries using GPT models
- **Noise Filtering**: Automatically removes irrelevant content and formatting artifacts

## How to Use

### 1. Access the Knowledge Tab
- Open the ChatCPG application
- Navigate to the sidebar
- Click on the "Adicionar conhecimento" (Add Knowledge) tab

### 2. Upload Files
- **File Upload Tab**: 
  - Click "Escolher arquivos" to select files
  - Select multiple files of supported formats
  - Click "Enviar" to process them

- **Directory Scan Tab**:
  - Enter the full path to a directory
  - Click "Enviar" to scan and process all compatible files

### 3. Monitor Progress
- Progress bar shows current processing status
- Real-time updates on file processing
- Success/error messages for each file

## File Storage

### Brand-Specific Storage
- Knowledge files are saved in the corresponding brand folder
- **Path**: `z_brands/{brand_id}/knowledge.md`
- **Example**: `z_brands/gebeauty/knowledge.md`

### File Structure
The knowledge base file contains:
- **Document Metadata**: Source file information
- **Summary**: AI-generated document summary
- **Main Topics**: Key topics identified in the document
- **Entities**: Named entities extracted using NLP
- **Full Content**: Complete document content (collapsible)

## Technical Details

### Dependencies
- **spaCy**: Natural language processing for entity extraction
- **LangChain**: Document processing and LLM integration
- **Streamlit**: User interface components
- **file_reader**: Custom file processing module

### Installation
```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_md
```

### Configuration
- **Language Support**: Bilingual interface (Portuguese/English)
- **Brand Context**: Automatically uses current brand settings
- **API Keys**: Requires OpenAI API key for LLM processing

## Error Handling

### Common Issues
1. **Missing spaCy Model**: Install Portuguese language model
2. **Unsupported Files**: System warns and skips incompatible files
3. **API Key Issues**: Check OpenAI API key configuration
4. **File Permissions**: Ensure write access to brand folders

### Troubleshooting
- Check console output for detailed error messages
- Verify file formats are supported
- Ensure brand folder exists and is writable
- Confirm API keys are properly configured

## Integration

### With ChatCPG Functions
- Knowledge base is available to both "Redação CPG" and "Oráculo CPG" functions
- Context is automatically loaded from brand-specific knowledge files
- Seamless integration with existing chat functionality

### Future Enhancements
- Knowledge base search functionality
- Document versioning and history
- Advanced filtering and categorization
- Export capabilities for processed knowledge

## Security

### Data Privacy
- Files are processed locally
- No data is sent to external services except for LLM processing
- Knowledge files are stored in brand-specific folders
- Temporary files are automatically cleaned up

### Access Control
- Knowledge base access is tied to brand context
- File uploads are restricted to supported formats
- Directory scanning respects file system permissions 