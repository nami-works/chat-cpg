# Installation Guide

## Quick Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install spaCy Portuguese Model (Optional but Recommended)
```bash
python -m spacy download pt_core_news_md
```

### 3. Set Environment Variables
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here  # Optional
```

### 4. Run the Application
```bash
streamlit run chat_cpg.py
```

## Troubleshooting

### Common Issues

#### 1. spaCy Model Not Found
**Error**: `OSError: Can't find model 'pt_core_news_md'`
**Solution**: 
```bash
python -m spacy download pt_core_news_md
```

#### 2. LangChain Deprecation Warnings
**Warning**: `LangChainDeprecationWarning: The method 'Chain.run' was deprecated`
**Status**: ✅ Fixed in latest version - these warnings should no longer appear

#### 3. Torch Runtime Errors
**Error**: `RuntimeError: Tried to instantiate class '__path__._path'`
**Solution**: This is a known compatibility issue between PyTorch and Streamlit. The application will still work, but you may see these warnings in the console.

#### 4. Missing Dependencies
**Error**: `ModuleNotFoundError: No module named 'spacy'`
**Solution**: 
```bash
pip install -r requirements.txt
```

### Optional Dependencies

#### For Better NLP Processing
- **spaCy**: Provides advanced NLP features for entity extraction and topic identification
- **Portuguese Model**: `pt_core_news_md` for Portuguese text processing

#### For File Processing
- **unstructured**: Handles various document formats
- **openpyxl**: Excel file processing
- **python-docx**: Word document processing

## System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 1GB free space for models and dependencies

## Performance Tips

1. **Use GPU**: If available, PyTorch will automatically use GPU acceleration
2. **Limit File Size**: Large files (>10MB) may take longer to process
3. **Batch Processing**: Use directory scanning for multiple files
4. **API Limits**: Be aware of OpenAI API rate limits for large document processing

## Security Notes

- API keys are stored locally in `.env` file
- No data is sent to external services except for LLM processing
- Knowledge files are stored in brand-specific folders
- Temporary files are automatically cleaned up 