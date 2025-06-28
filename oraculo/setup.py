#!/usr/bin/env python3
"""
Setup script for the Enhanced Oráculo Knowledge Extraction System
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True

def install_requirements():
    """Install Python requirements."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    command = f"{sys.executable} -m pip install -r {requirements_file}"
    return run_command(command, "Installing Python requirements")

def install_spacy_model():
    """Install Portuguese spaCy model."""
    command = f"{sys.executable} -m spacy download pt_core_news_md"
    success = run_command(command, "Installing Portuguese spaCy model")
    
    if not success:
        print("⚠️  You can install the spaCy model manually later with:")
        print("   python -m spacy download pt_core_news_md")
    
    return success

def verify_installation():
    """Verify that key components are installed correctly."""
    print("\n🔍 Verifying installation...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not found")
        return False
    
    try:
        import langchain
        print(f"✅ LangChain {langchain.__version__}")
    except ImportError:
        print("❌ LangChain not found")
        return False
    
    try:
        import spacy
        print(f"✅ spaCy {spacy.__version__}")
        
        # Check if Portuguese model is available
        try:
            nlp = spacy.load("pt_core_news_md")
            print("✅ Portuguese spaCy model loaded successfully")
        except OSError:
            print("⚠️  Portuguese spaCy model not found")
            print("   Run: python -m spacy download pt_core_news_md")
    except ImportError:
        print("❌ spaCy not found")
        return False
    
    try:
        import PyPDF2
        print(f"✅ PyPDF2 available for PDF processing")
    except ImportError:
        print("⚠️  PyPDF2 not found - PDF processing will be limited")
    
    try:
        import docx
        print(f"✅ python-docx available for Word document processing")
    except ImportError:
        print("⚠️  python-docx not found - Word document processing will be limited")
    
    return True

def create_test_knowledge_structure():
    """Create basic directory structure for testing."""
    print("\n📁 Creating test directory structure...")
    
    base_dir = Path(__file__).parent.parent
    test_brand_dir = base_dir / "z_brands" / "test_brand"
    
    try:
        test_brand_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a basic test knowledge file
        test_knowledge = test_brand_dir / "knowledge.md"
        if not test_knowledge.exists():
            test_content = """# Test Brand Knowledge Base

## SUMMARY

This is a test knowledge base created by the setup script.

## ANALYTICAL VERSION

This section will contain detailed analysis from processed documents.

## DATA

This section will contain statistical information and metrics.
"""
            with open(test_knowledge, 'w', encoding='utf-8') as f:
                f.write(test_content)
        
        print(f"✅ Test directory structure created at: {test_brand_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test structure: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Enhanced Oráculo Setup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Install spaCy model
    install_spacy_model()
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        sys.exit(1)
    
    # Create test structure
    create_test_knowledge_structure()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run your Streamlit application")
    print("2. Navigate to the Oráculo section")
    print("3. Upload files to test the knowledge extraction")
    print("\n📚 See README.md for detailed usage instructions")

if __name__ == "__main__":
    main()