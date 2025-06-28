# Oráculo - Enhanced Knowledge Extraction System

## Overview

The upgraded **Oráculo** system is a comprehensive knowledge extraction and management tool that processes uploaded files through a Streamlit interface, extracts valuable insights, and creates structured knowledge bases for brand management.

## New Features

### 🚀 File Upload & Processing
- **Multiple File Support**: Upload single or multiple files simultaneously
- **Format Support**: TXT, PDF, DOCX, DOC, MD files
- **Real-time Processing**: Progress tracking with visual feedback
- **Error Handling**: Robust error handling for unsupported formats

### 📊 Knowledge Extraction
- **Comprehensive Analysis**: Advanced NLP and LLM-powered content analysis
- **Entity Recognition**: Automatic extraction of key entities using spaCy
- **Statistical Data Mining**: Pattern-based extraction of numerical data
- **Topic Identification**: AI-powered topic and theme discovery

### 📝 Knowledge Management
- **Structured Output**: Creates `new_knowledge.md` with standardized sections:
  - **TITLE**: Comprehensive title about extracted knowledge
  - **SUMMARY**: Concise summary of key findings
  - **ANALYTICAL VERSION**: Detailed analytical breakdown
  - **DATA**: Statistical information and metrics
- **Smart File Management**: Automatic handling of existing knowledge bases
- **Content Merging**: Intelligent merging of new content with existing knowledge

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Language Model Setup
```bash
# Install Portuguese spaCy model
python -m spacy download pt_core_news_md
```

## Usage

### 1. File Upload Interface
1. Navigate to the Oráculo section in the application
2. Use the "📁 Upload and Process Knowledge Files" expander
3. Click "Choose files to process" to select your documents
4. Review the selected files and their sizes
5. Click "🚀 Process Files" to start extraction

### 2. Knowledge Processing Flow
The system follows this workflow:
1. **File Text Extraction**: Extracts text content from uploaded files
2. **Comprehensive Analysis**: Uses AI to analyze content structure and meaning
3. **Knowledge Structuring**: Organizes findings into standardized sections
4. **File Management**: Handles knowledge.md creation/updating

### 3. Knowledge File Management Rules

#### If `knowledge.md` doesn't exist:
- Creates `new_knowledge.md` with extracted content
- Copies `new_knowledge.md` to `knowledge.md`
- Deletes temporary `new_knowledge.md`

#### If `knowledge.md` already exists:
- Extracts **TITLE** and **SUMMARY** from new content
- Appends **TITLE** and **SUMMARY** to existing **SUMMARY** section
- Adds **ANALYTICAL VERSION** and **DATA** sections to the end
- Deletes temporary `new_knowledge.md`

## Supported File Formats

| Format | Extension | Requirements |
|--------|-----------|--------------|
| Text | .txt | Built-in support |
| PDF | .pdf | PyPDF2 library |
| Word | .docx, .doc | python-docx library |
| Markdown | .md | Built-in support |

## Features in Detail

### Knowledge Extraction Components

1. **Summary Generation**
   - Uses LangChain's map-reduce summarization
   - Processes large documents in chunks
   - Generates coherent, comprehensive summaries

2. **Entity Recognition**
   - Identifies people, organizations, locations
   - Extracts dates, monetary values, percentages
   - Categorizes entities by type

3. **Statistical Data Mining**
   - Percentage values (e.g., 45%, 12.5%)
   - Currency amounts (e.g., $1,000, $2.5M)
   - Large numbers with formatting
   - Decimal values and metrics

4. **Analytical Processing**
   - Theme identification
   - Key insight extraction
   - Methodology recognition
   - Conclusion highlighting
   - Concept relationship mapping

### User Interface Features

- **Progress Tracking**: Real-time progress bars and status updates
- **File Preview**: Shows selected files with sizes
- **Knowledge Base Info**: Displays current knowledge base statistics
- **Preview Capability**: Option to preview existing knowledge content
- **Success Feedback**: Visual confirmation with balloons and success messages

## Technical Architecture

### Core Functions

- `extract_text_from_uploaded_file()`: Handles file text extraction
- `extract_comprehensive_knowledge()`: Performs AI-powered analysis
- `generate_new_knowledge_md()`: Creates structured markdown output
- `manage_knowledge_file()`: Handles file creation/updating logic
- `process_uploaded_files()`: Orchestrates the entire workflow

### Error Handling

- Graceful handling of missing dependencies
- Format-specific error messages
- Fallback mechanisms for unsupported files
- User-friendly error reporting

## Legacy Compatibility

The system maintains backward compatibility with the original directory scanning functionality through the "📂 Scan Directory (Legacy)" popover, ensuring existing workflows continue to function.

## Brand Integration

The system automatically integrates with the brand context, saving knowledge files to the appropriate brand folder structure:
```
z_brands/
  └── [brand_id]/
      ├── knowledge.md          # Main knowledge base
      ├── legacy_knowledge.md   # Legacy scan results
      └── [other brand files]
```

## Best Practices

1. **File Organization**: Upload related documents together for comprehensive analysis
2. **Format Selection**: Use text-based formats (TXT, MD) for best results
3. **Regular Processing**: Process new documents regularly to keep knowledge base current
4. **Review Content**: Check processed knowledge for accuracy and completeness

## Troubleshooting

### Common Issues

1. **Module Not Found**: Install missing dependencies from requirements.txt
2. **spaCy Model Missing**: Run `python -m spacy download pt_core_news_md`
3. **PDF Processing**: Ensure PyPDF2 is installed for PDF support
4. **Word Documents**: Install python-docx for DOCX/DOC support

### Performance Notes

- Large files may take longer to process
- PDF processing is slower than text formats
- Multiple files are processed sequentially
- Progress bars provide real-time feedback

## Future Enhancements

- Support for additional file formats (Excel, PowerPoint)
- Batch processing optimization
- Advanced entity relationship mapping
- Multi-language support expansion
- Custom knowledge templates