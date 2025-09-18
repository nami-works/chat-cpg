#!/usr/bin/env python
"""
Enhanced Keyword Filtering System with Streamlit Interface

This module implements the 4-step approach for efficient keyword selection:
1. Identify keywords relevant to themes
2. Create SEO/EEAT shortlist of 20 most effective keywords
3. Streamlit interface for user selection
4. Inject prioritized keywords into crew context
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional, Tuple
from chats.seo_lab.keyword_database import KeywordDatabase
import json
from translations import LANG


class EnhancedKeywordFilteringSystem:
    """
    Enhanced keyword filtering system with 4-step workflow
    Integrates with existing Streamlit interface without system changes
    """
    
    def __init__(self, csv_path: str, competitor_brands: List[str] = None, target_brand: str = None):
        self.csv_path = csv_path
        self.competitor_brands = competitor_brands or []
        self.target_brand = target_brand or ""
        self.keyword_db = KeywordDatabase(csv_path, competitor_brands, target_brand)
        
        # Initialize session state for keyword selection
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state for keyword selection"""
        if 'enhanced_keyword_filtering' not in st.session_state:
            st.session_state['enhanced_keyword_filtering'] = {
                'relevant_keywords': {},
                'shortlist_keywords': {},
                'selected_keywords': {},
                'final_keywords': {}
            }
    
    def step1_identify_relevant_keywords(self, theme: str) -> List[Dict]:
        """
        Step 1: Identify keywords relevant to the theme
        
        Args:
            theme: Theme description to find keywords for
            
        Returns:
            List of relevant keyword dictionaries
        """
        st.info(f"🔍 **Step 1**: Identifying keywords relevant to theme: '{theme}'")
        
        # Get all relevant keywords for the theme
        relevant_keywords = self.keyword_db.get_keywords_for_theme(theme)
        
        # Store in session state
        st.session_state['enhanced_keyword_filtering']['relevant_keywords'][theme] = relevant_keywords
        
        st.success(f"✅ Found {len(relevant_keywords)} relevant keywords for theme: '{theme}'")
        
        return relevant_keywords
    
    def step2_create_seo_eeat_shortlist(self, theme: str, max_keywords: int = 20) -> List[Dict]:
        """
        Step 2: Create SEO/EEAT shortlist of most effective keywords
        
        Args:
            theme: Theme to create shortlist for
            max_keywords: Maximum number of keywords in shortlist
            
        Returns:
            List of shortlisted keywords with SEO/EEAT scores
        """
        st.info(f"📊 **Step 2**: Creating SEO/EEAT shortlist for theme: '{theme}'")
        
        # Get relevant keywords from step 1
        relevant_keywords = st.session_state['enhanced_keyword_filtering']['relevant_keywords'].get(theme, [])
        
        if not relevant_keywords:
            st.warning(f"No relevant keywords found for theme: '{theme}'. Please run Step 1 first.")
            return []
        
        # Create SEO/EEAT scoring system
        shortlist_keywords = self._create_seo_eeat_shortlist(relevant_keywords, max_keywords)
        
        # Store in session state
        st.session_state['enhanced_keyword_filtering']['shortlist_keywords'][theme] = shortlist_keywords
        
        st.success(f"✅ Created shortlist of {len(shortlist_keywords)} SEO/EEAT optimized keywords")
        
        return shortlist_keywords
    
    def _create_seo_eeat_shortlist(self, keywords: List[Dict], max_keywords: int) -> List[Dict]:
        """Create SEO/EEAT shortlist based on multiple criteria"""
        scored_keywords = []
        
        for kw in keywords:
            # SEO Score (0-100)
            seo_score = self._calculate_seo_score(kw)
            
            # EEAT Score (0-100)
            eeat_score = self._calculate_eeat_score(kw)
            
            # Combined Score (SEO 60% + EEAT 40%)
            combined_score = (seo_score * 0.6) + (eeat_score * 0.4)
            
            scored_keywords.append({
                **kw,
                'seo_score': seo_score,
                'eeat_score': eeat_score,
                'combined_score': combined_score,
                'selected': False  # For user selection
            })
        
        # Sort by combined score and take top keywords
        scored_keywords.sort(key=lambda x: x['combined_score'], reverse=True)
        return scored_keywords[:max_keywords]
    
    def _calculate_seo_score(self, keyword: Dict) -> float:
        """Calculate SEO score based on volume, difficulty, and position"""
        volume = keyword.get('Volume', 0)
        difficulty = keyword.get('SEO Difficulty', 50)
        position = keyword.get('Position', 999)
        
        # Volume score (0-40 points)
        volume_score = min(40, volume / 25)  # Max 40 points for 1000+ volume
        
        # Difficulty score (0-30 points) - lower difficulty = higher score
        difficulty_score = max(0, 30 - (difficulty * 0.6))  # 30 points for difficulty 0, 0 for 50+
        
        # Position score (0-30 points) - lower position = higher score
        position_score = max(0, 30 - (position * 0.03))  # 30 points for position 1, 0 for 1000+
        
        return volume_score + difficulty_score + position_score
    
    def _calculate_eeat_score(self, keyword: Dict) -> float:
        """Calculate EEAT (Experience, Expertise, Authority, Trust) score"""
        keyword_text = keyword.get('Keywords', '').lower()
        
        # Experience indicators (0-25 points)
        experience_indicators = ['como', 'como usar', 'tutorial', 'guia', 'dicas', 'dicas de', 'how to', 'guide', 'tips']
        experience_score = min(25, sum(5 for indicator in experience_indicators if indicator in keyword_text))
        
        # Expertise indicators (0-25 points)
        expertise_indicators = ['melhor', 'melhores', 'top', 'recomendado', 'especialista', 'profissional', 'best', 'expert', 'professional']
        expertise_score = min(25, sum(5 for indicator in expertise_indicators if indicator in keyword_text))
        
        # Authority indicators (0-25 points)
        authority_indicators = ['reviews', 'avaliação', 'teste', 'comparativo', 'análise', 'estudo', 'review', 'test', 'comparison', 'analysis']
        authority_score = min(25, sum(5 for indicator in authority_indicators if indicator in keyword_text))
        
        # Trust indicators (0-25 points)
        trust_indicators = ['natural', 'orgânico', 'seguro', 'testado', 'aprovado', 'garantia', 'organic', 'safe', 'tested', 'approved', 'guarantee']
        trust_score = min(25, sum(5 for indicator in trust_indicators if indicator in keyword_text))
        
        return experience_score + expertise_score + authority_score + trust_score
    
    def step3_streamlit_keyword_selection_interface(self, theme: str) -> List[Dict]:
        """
        Step 3: Streamlit interface for user keyword selection
        
        Args:
            theme: Theme to display keywords for
            
        Returns:
            List of selected keywords
        """
        shortlist_keywords = st.session_state['enhanced_keyword_filtering']['shortlist_keywords'].get(theme, [])
        
        if not shortlist_keywords:
            st.warning(LANG['no_keywords_available'])
            return []
        
        # Display keyword selection interface
        st.markdown(f"### 📋 Select Keywords for: {theme}")
        
        # Create columns for better layout
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Keyword selection with checkboxes
            selected_keywords = []
            
            for i, kw in enumerate(shortlist_keywords):
                # Create a unique key for each checkbox
                checkbox_key = f"keyword_{theme}_{i}_{kw['Keywords']}"
                
                # Create keyword display container
                with st.container():
                    # Keyword header with checkbox
                    is_selected = st.checkbox(
                        f"**{kw['Keywords']}**",
                        key=checkbox_key,
                        value=kw.get('selected', False)
                    )
                    
                    # Display metrics in columns
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        st.caption(f"📊 Volume: {kw['Volume']:,}")
                    
                    with metric_col2:
                        st.caption(f"🎯 Difficulty: {kw['SEO Difficulty']}")
                    
                    with metric_col3:
                        st.caption(f"🔍 SEO: {kw['seo_score']:.1f}")
                    
                    with metric_col4:
                        st.caption(f"⭐ EEAT: {kw['eeat_score']:.1f}")
                    
                    # Combined score bar
                    st.progress(kw['combined_score'] / 100, text=f"Combined Score: {kw['combined_score']:.1f}/100")
                    
                    if is_selected:
                        selected_keywords.append(kw)
                        kw['selected'] = True
                    else:
                        kw['selected'] = False
                    
                    st.divider()
        
        with col2:
            # Summary and controls
            st.markdown(f"### 📊 {LANG['selection_summary']}")
            
            total_keywords = len(shortlist_keywords)
            selected_count = len(selected_keywords)
            
            st.metric("Total Keywords", total_keywords)
            st.metric("Selected Keywords", selected_count)
            if total_keywords > 0:
                st.metric("Selection Rate", f"{(selected_count/total_keywords)*100:.1f}%")
            
            # Quick selection buttons
            st.markdown(f"### ⚡ {LANG['quick_actions']}")
            
            button_col1, button_col2 = st.columns(2)
            
            with button_col1:
                if st.button(LANG['select_all'], key=f"select_all_{theme}"):
                    for kw in shortlist_keywords:
                        kw['selected'] = True
                    st.rerun()
                
                if st.button(LANG['select_top_10'], key=f"select_top_10_{theme}"):
                    for i, kw in enumerate(shortlist_keywords[:10]):
                        kw['selected'] = True
                    for kw in shortlist_keywords[10:]:
                        kw['selected'] = False
                    st.rerun()
            
            with button_col2:
                if st.button(LANG['deselect_all'], key=f"deselect_all_{theme}"):
                    for kw in shortlist_keywords:
                        kw['selected'] = False
                    st.rerun()
                
                if st.button(LANG['high_seo_70'], key=f"select_high_seo_{theme}"):
                    for kw in shortlist_keywords:
                        kw['selected'] = kw['seo_score'] > 70
                    st.rerun()
        
        # Store selected keywords in session state
        st.session_state['enhanced_keyword_filtering']['selected_keywords'][theme] = selected_keywords
        
        if selected_keywords:
            st.success(f"✅ Selected {len(selected_keywords)} keywords for theme: '{theme}'")
        
        return selected_keywords
    
    def step4_inject_prioritized_keywords(self, theme: str) -> Dict:
        """
        Step 4: Inject prioritized keywords into crew context
        
        Args:
            theme: Theme to inject keywords for
            
        Returns:
            Lightweight keyword context for crew
        """
        selected_keywords = st.session_state['enhanced_keyword_filtering']['selected_keywords'].get(theme, [])
        
        if not selected_keywords:
            st.warning(LANG['no_keywords_selected'])
            return {}
        
        # Create lightweight keyword context for crew
        keyword_context = self._create_lightweight_context(selected_keywords, theme)
        
        # Store final keywords in session state
        st.session_state['enhanced_keyword_filtering']['final_keywords'][theme] = keyword_context
        
        st.success(f"✅ Injected {len(selected_keywords)} prioritized keywords for theme: '{theme}'")
        
        return keyword_context
    
    def _create_lightweight_context(self, selected_keywords: List[Dict], theme: str) -> Dict:
        """Create lightweight keyword context for crew agents"""
        # Extract just the essential data
        keywords_list = [kw['Keywords'] for kw in selected_keywords]
        
        # Calculate summary metrics
        if selected_keywords:
            avg_volume = sum(kw['Volume'] for kw in selected_keywords) / len(selected_keywords)
            avg_difficulty = sum(kw['SEO Difficulty'] for kw in selected_keywords) / len(selected_keywords)
            avg_seo_score = sum(kw['seo_score'] for kw in selected_keywords) / len(selected_keywords)
            avg_eeat_score = sum(kw['eeat_score'] for kw in selected_keywords) / len(selected_keywords)
        else:
            avg_volume = avg_difficulty = avg_seo_score = avg_eeat_score = 0
        
        return {
            'theme': theme,
            'keywords': keywords_list,
            'keyword_count': len(keywords_list),
            'summary': {
                'avg_volume': avg_volume,
                'avg_difficulty': avg_difficulty,
                'avg_seo_score': avg_seo_score,
                'avg_eeat_score': avg_eeat_score,
                'total_keywords': len(keywords_list)
            },
            'top_keywords': keywords_list[:5],  # Top 5 for immediate use
            'opportunities': [kw['Keywords'] for kw in selected_keywords if kw['Volume'] >= 500 and kw['SEO Difficulty'] <= 25]
        }
    
    def get_final_keywords_for_theme(self, theme: str) -> Dict:
        """Get final lightweight keywords for a specific theme"""
        return st.session_state['enhanced_keyword_filtering']['final_keywords'].get(theme, {})
    
    def get_all_final_keywords(self) -> Dict:
        """Get all final keywords for all themes"""
        return st.session_state['enhanced_keyword_filtering']['final_keywords']


def create_enhanced_keyword_filtering_system(csv_path: str = "keywords.csv") -> EnhancedKeywordFilteringSystem:
    """
    Create enhanced keyword filtering system with default settings
    
    Args:
        csv_path: Path to keyword CSV file
        
    Returns:
        EnhancedKeywordFilteringSystem instance
    """
    # Get brand context from session state
    try:
        import streamlit as st
        context = st.session_state.get('context', {})
        target_brand = context.get('brand', 'Selected Brand')
        competitor_brands = context.get('benchmarks', ['Leading brands in the category'])
    except ImportError:
        target_brand = 'Selected Brand'
        competitor_brands = ['Leading brands in the category']
    
    return EnhancedKeywordFilteringSystem(
        csv_path=csv_path,
        competitor_brands=competitor_brands,
        target_brand=target_brand
    )