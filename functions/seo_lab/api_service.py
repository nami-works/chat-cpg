#!/usr/bin/env python3
"""
FastAPI service for CrewAI SEO Lab integration
Deploy this to Render.com or similar platform
"""

import os
import time
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import your existing CrewAI setup
from src.copywriter_crew.crew import SEOLab_CPG
from context_chunking import ContextChunker, get_task_stage

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CrewAI SEO Lab API",
    description="API for generating SEO blog content using CrewAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class GeneratePayload(BaseModel):
    brand: str
    topic: str
    keywords: Optional[list[str]] = None
    outline: Optional[list[str]] = None
    tone: Optional[str] = None
    wordCount: Optional[int] = None
    language: Optional[str] = "pt-BR"
    additionalContext: Optional[str] = None

class GenerateResponse(BaseModel):
    html: str
    meta: Optional[Dict[str, Any]] = None
    stats: Optional[Dict[str, Any]] = None
    traceId: Optional[str] = None

# Configuration
API_KEY = os.getenv("API_KEY", "your-secret-key-here")
BASE_DIR = Path(__file__).resolve().parent

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    import re
    invalid_chars = r'[<>:"|?*\\\/]'
    sanitized = re.sub(invalid_chars, '', filename)
    sanitized = sanitized.strip(' .')
    if not sanitized:
        sanitized = 'untitled'
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized

def create_mock_inputs(payload: GeneratePayload) -> Dict[str, Any]:
    """Create mock inputs for the CrewAI system based on the payload."""
    
    # Create a temporary brand folder structure
    temp_dir = tempfile.mkdtemp()
    brand_folder = Path(temp_dir) / "temp_brand"
    posts_folder = brand_folder / "posts"
    posts_folder.mkdir(parents=True, exist_ok=True)
    
    # Create basic brand context files
    editorials_file = brand_folder / "editorials.md"
    editorials_file.write_text(f"""
# Editorial Guidelines for {payload.brand}

## Voice and Tone
- Professional yet approachable
- Focus on {payload.topic}
- Language: {payload.language}

## Content Structure
- Clear headings and subheadings
- SEO-optimized content
- Engaging narrative flow
""", encoding='utf-8')
    
    # Create brief summary
    brief_summary_file = posts_folder / "brief_summary.py"
    brief_summary_content = f"""
brief_summary = {{
    "{payload.topic}": "Comprehensive guide about {payload.topic} for {payload.brand} audience. Focus on practical insights and actionable advice."
}}
"""
    brief_summary_file.write_text(brief_summary_content, encoding='utf-8')
    
    # Create keywords file
    keywords_file = posts_folder / "keywords.py"
    keywords_content = f"""
keywords = {{
    "{payload.topic}": {{
        "primary_keywords": {payload.keywords or []},
        "long_tail_keywords": [],
        "related_searches": [],
        "search_volume": {{}},
        "competition_level": "medium"
    }}
}}
"""
    keywords_file.write_text(keywords_content, encoding='utf-8')
    
    # Create products file
    products_file = posts_folder / "products.py"
    products_content = f"""
products = {{
    "{payload.topic}": []
}}
"""
    products_file.write_text(products_content, encoding='utf-8')
    
    # Build the inputs dictionary that matches your existing system
    inputs = {
        'themes': {payload.topic: payload.topic},
        'voice': f"Professional voice for {payload.brand}",
        'brand': payload.brand,
        'products': payload.additionalContext or f"Products and services from {payload.brand}",
        'blog': f"Blog content for {payload.brand} focusing on {payload.topic}",
        'benchmarks': f"Industry benchmarks for {payload.topic}",
        'format_recommendations': "HTML format with proper SEO structure",
        'semantic_fields': [payload.topic] + (payload.keywords or []),
        'brand_folder': str(brand_folder),
        'macro_name': datetime.now().strftime("%H_%M"),
        'preferred_language': payload.language or 'pt_BR',
        'selected_products': [],
        'selected_product_names': [],
        'context': {
            'brand_id': 'temp_brand',
            'brand': payload.brand
        }
    }
    
    return inputs, brand_folder

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "CrewAI SEO Lab API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/seo/generate", response_model=GenerateResponse)
async def generate_blog(
    payload: GeneratePayload,
    x_api_key: str = Header(alias="x-api-key")
):
    """
    Generate SEO blog content using CrewAI
    """
    # Validate API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    start_time = time.time()
    trace_id = f"trace_{int(time.time())}"
    
    try:
        # Create mock inputs for the CrewAI system
        inputs, brand_folder = create_mock_inputs(payload)
        
        # Initialize the CrewAI system
        seo_lab_cpg = SEOLab_CPG(brand_folder)
        seo_lab_cpg.initialize_context_chunker(inputs)
        
        # Get the first (and only) theme
        theme_name = list(inputs['themes'].keys())[0]
        theme = inputs['themes'][theme_name]
        
        # Build theme inputs
        theme_inputs = {
            'voice': inputs['voice'],
            'brand': inputs['brand'],
            'name': theme_name,
            'theme': theme,
            'products': inputs['products'],
            'blog': inputs['blog'],
            'benchmarks': inputs['benchmarks'],
            'format_recommendations': inputs['format_recommendations'],
            'semantic_fields': inputs['semantic_fields'],
            'theme_keywords': payload.keywords or [],
            'keyword_opportunities': (payload.keywords or [])[:5],
            'preferred_language': inputs['preferred_language'],
            'brief_summary': f"Comprehensive guide about {theme} for {inputs['brand']} audience",
            'theme_products': [],
            'theme_keywords_data': {
                'primary_keywords': payload.keywords or [],
                'long_tail_keywords': [],
                'related_searches': [],
                'search_volume': {},
                'competition_level': 'medium'
            },
            'primary_keywords': payload.keywords or [],
            'long_tail_keywords': [],
            'related_searches': [],
            'search_volume': {},
            'competition_level': 'medium',
            'editorial_guidelines': f"Professional content for {inputs['brand']} focusing on {theme}"
        }
        
        # Run the CrewAI system
        crew_instance = seo_lab_cpg.crew()
        result = crew_instance.kickoff(inputs=theme_inputs)
        
        # Read the generated content
        content_file = brand_folder / 'posts' / 'content.html'
        metafields_file = brand_folder / 'posts' / 'metafields.md'
        
        if not content_file.exists():
            raise FileNotFoundError("Content file not generated")
        
        # Read the HTML content
        html_content = content_file.read_text(encoding='utf-8')
        
        # Read metadata if available
        meta_data = {}
        if metafields_file.exists():
            metafields_content = metafields_file.read_text(encoding='utf-8')
            # Parse basic metadata from the markdown file
            lines = metafields_content.split('\n')
            for line in lines:
                if line.startswith('title:'):
                    meta_data['title'] = line.replace('title:', '').strip()
                elif line.startswith('description:'):
                    meta_data['description'] = line.replace('description:', '').strip()
                elif line.startswith('keywords:'):
                    keywords_str = line.replace('keywords:', '').strip()
                    meta_data['keywords'] = [k.strip() for k in keywords_str.split(',') if k.strip()]
        
        # If no metadata was found, create basic ones
        if not meta_data:
            meta_data = {
                'title': f"{payload.topic} - {payload.brand}",
                'description': f"Comprehensive guide about {payload.topic} for {payload.brand}",
                'keywords': payload.keywords or []
            }
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Cleanup temporary files
        try:
            shutil.rmtree(brand_folder.parent)
        except:
            pass  # Ignore cleanup errors
        
        return GenerateResponse(
            html=html_content,
            meta=meta_data,
            stats={
                'durationMs': duration_ms,
                'tokens': 0  # Add actual token count if available
            },
            traceId=trace_id
        )
        
    except Exception as e:
        # Cleanup on error
        try:
            if 'brand_folder' in locals():
                shutil.rmtree(brand_folder.parent)
        except:
            pass
        
        raise HTTPException(
            status_code=500, 
            detail=f"Content generation failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
