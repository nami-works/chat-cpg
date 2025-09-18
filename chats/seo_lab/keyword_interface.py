#!/usr/bin/env python
"""
Streamlit Interface Functions for Enhanced Keyword Filtering

This module provides Streamlit interface functions that integrate 
with the existing _seo_lab.py workflow without system changes.
"""

import streamlit as st
from typing import List, Dict, Optional
from pathlib import Path
from chats.seo_lab.enhanced_keyword_filtering import create_enhanced_keyword_filtering_system
from translations import LANG


def display_keyword_filtering_interface():
    """
    Display the enhanced keyword filtering interface
    Integrates with existing blog lab flow after theme generation
    """
    # Check if themes exist in session state
    themes = st.session_state.get('themes', {})
    
    if not themes:
        return False  # No themes available, don't show interface
    
    st.markdown(f"## 🎯 {LANG['keyword_optimization_title']}")
    st.markdown(LANG['keyword_optimization_subtitle'])
    
    # Initialize the filtering system with correct path
    # Get the absolute path to the blog lab directory
    seo_lab_dir = Path(__file__).parent
    csv_path = seo_lab_dir / "keywords.csv"
    filtering_system = create_enhanced_keyword_filtering_system(str(csv_path))
    
    # Track if any keywords were processed
    keywords_processed = False
    
    # Process each theme
    for theme_name, theme_description in themes.items():
        with st.expander(f"📊 Keywords for: {theme_name}", expanded=False):
            keywords_processed = _process_theme_keywords(
                filtering_system, 
                theme_name, 
                theme_description
            ) or keywords_processed
    
    return keywords_processed


def _process_theme_keywords(filtering_system, theme_name: str, theme_description: str) -> bool:
    """
    Process keywords for a specific theme through the 4-step workflow
    
    Args:
        filtering_system: EnhancedKeywordFilteringSystem instance
        theme_name: Name of the theme
        theme_description: Description of the theme
        
    Returns:
        bool: True if keywords were processed for this theme
    """
    keywords_processed = False
    
    # Step 1: Identify relevant keywords
    step1_key = f"step1_{theme_name}"
    if st.button(f"🔍 Step 1: Identify Keywords", key=step1_key):
        with st.spinner(f"Identifying keywords for '{theme_name}'..."):
            relevant_keywords = filtering_system.step1_identify_relevant_keywords(theme_description)
            keywords_processed = True
    
    # Step 2: Create SEO/EEAT shortlist (only if step 1 completed)
    if theme_description in st.session_state['enhanced_keyword_filtering']['relevant_keywords']:
        step2_key = f"step2_{theme_name}"
        if st.button(f"📊 Step 2: Create SEO/EEAT Shortlist", key=step2_key):
            with st.spinner(f"Creating optimized shortlist for '{theme_name}'..."):
                shortlist = filtering_system.step2_create_seo_eeat_shortlist(theme_description)
                keywords_processed = True
    
    # Step 3: User selection interface (only if step 2 completed)
    if theme_description in st.session_state['enhanced_keyword_filtering']['shortlist_keywords']:
        st.markdown(f"### 📋 {LANG['select_keywords_title']}")
        selected_keywords = filtering_system.step3_streamlit_keyword_selection_interface(theme_description)
        keywords_processed = True
        
        # Step 4: Inject keywords (only if keywords selected)
        if selected_keywords:
            step4_key = f"step4_{theme_name}"
            if st.button(f"💉 Step 4: Inject Keywords into Content", key=step4_key):
                with st.spinner(f"Preparing keywords for '{theme_name}'..."):
                    keyword_context = filtering_system.step4_inject_prioritized_keywords(theme_description)
                    if keyword_context:
                        st.success(LANG['keywords_ready_success'])
                        
                        # Show summary of injected keywords
                        with st.expander("Injected Keywords Summary", expanded=False):
                            st.json(keyword_context)
                    
                    keywords_processed = True
    
    return keywords_processed


def get_enhanced_keywords_for_theme(theme_description: str) -> Dict:
    """
    Get enhanced keywords for a specific theme
    
    Args:
        theme_description: Theme description to get keywords for
        
    Returns:
        Dict: Lightweight keyword context or empty dict
    """
    if 'enhanced_keyword_filtering' not in st.session_state:
        return {}
    
    return st.session_state['enhanced_keyword_filtering']['final_keywords'].get(theme_description, {})


def get_all_enhanced_keywords() -> Dict:
    """
    Get all enhanced keywords for all themes
    
    Returns:
        Dict: All lightweight keyword contexts
    """
    if 'enhanced_keyword_filtering' not in st.session_state:
        return {}
    
    return st.session_state['enhanced_keyword_filtering']['final_keywords']


def has_enhanced_keywords() -> bool:
    """
    Check if any enhanced keywords have been processed
    
    Returns:
        bool: True if enhanced keywords exist
    """
    if 'enhanced_keyword_filtering' not in st.session_state:
        return False
    
    final_keywords = st.session_state['enhanced_keyword_filtering']['final_keywords']
    return len(final_keywords) > 0


def clear_enhanced_keywords():
    """Clear all enhanced keyword data from session state"""
    if 'enhanced_keyword_filtering' in st.session_state:
        st.session_state['enhanced_keyword_filtering'] = {
            'relevant_keywords': {},
            'shortlist_keywords': {},
            'selected_keywords': {},
            'final_keywords': {}
        }


def display_keyword_summary():
    """Display a summary of processed keywords"""
    if not has_enhanced_keywords():
        return
    
    final_keywords = get_all_enhanced_keywords()
    
    st.markdown(f"### 📊 {LANG['keyword_processing_summary']}")
    
    total_themes = len(final_keywords)
    total_keywords = sum(kw_data['keyword_count'] for kw_data in final_keywords.values())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Themes Processed", total_themes)
    
    with col2:
        st.metric("Total Keywords Selected", total_keywords)
    
    with col3:
        avg_keywords = total_keywords / total_themes if total_themes > 0 else 0
        st.metric("Avg Keywords/Theme", f"{avg_keywords:.1f}")
    
    # Show details for each theme
    for theme, kw_data in final_keywords.items():
        with st.expander(f"📋 {theme} ({kw_data['keyword_count']} keywords)", expanded=False):
            st.markdown(f"**Top Keywords:** {', '.join(kw_data['top_keywords'])}")
            st.markdown(f"**Opportunities:** {', '.join(kw_data['opportunities'])}")
            st.json(kw_data['summary'])


def inject_keywords_into_theme_inputs(theme_inputs: Dict, theme_description: str) -> Dict:
    """
    Inject enhanced keywords into theme inputs for crew processing
    
    Args:
        theme_inputs: Original theme inputs dictionary
        theme_description: Theme description to get keywords for
        
    Returns:
        Dict: Enhanced theme inputs with lightweight keyword data
    """
    # Get enhanced keywords for this theme
    keyword_context = get_enhanced_keywords_for_theme(theme_description)
    
    if keyword_context:
        # Remove heavy keyword database if present
        if 'keyword_database' in theme_inputs:
            del theme_inputs['keyword_database']
        
        # Inject lightweight keyword data
        theme_inputs.update({
            'keywords': keyword_context['keywords'],
            'keyword_summary': keyword_context['summary'],
            'top_keywords': keyword_context['top_keywords'],
            'opportunities': keyword_context['opportunities'],
            'keyword_count': keyword_context['keyword_count']
        })
        
        # Update existing keyword fields with enhanced data
        theme_inputs['theme_keywords'] = keyword_context['keywords']
        theme_inputs['keyword_opportunities'] = keyword_context['opportunities']
    
    return theme_inputs