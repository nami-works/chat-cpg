import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import re

class KeywordDatabase:
    def __init__(self, csv_path: str = None, competitor_brands: List[str] = None, target_brand: str = None, brand_id: str = None):
        # Get brand_id from session state if not provided
        if brand_id is None and csv_path is None:
            try:
                import streamlit as st
                context = st.session_state.get('context', {})
                brand_id = context.get('brand_id')
            except ImportError:
                brand_id = None
        
        # Set default CSV path based on brand_id
        if csv_path is None:
            if brand_id:
                self.csv_path = f"z_brands/{brand_id}/prioritized_keywords.csv"
            else:
                # Try to find any available keywords file as fallback
                brands_dir = Path("z_brands")
                if brands_dir.exists():
                    for brand_dir in brands_dir.iterdir():
                        if brand_dir.is_dir():
                            keywords_file = brand_dir / "prioritized_keywords.csv"
                            if keywords_file.exists():
                                self.csv_path = str(keywords_file)
                                print(f"📝 Using fallback keywords from: {keywords_file}")
                                break
                    else:
                        self.csv_path = "z_brands/default/prioritized_keywords.csv"  # Generic fallback
                else:
                    self.csv_path = "z_brands/default/prioritized_keywords.csv"  # Generic fallback
        else:
            self.csv_path = csv_path
            
        self.competitor_brands = competitor_brands or []
        self.target_brand = target_brand or ""
        self.keywords_df = self._load_keywords()
    
    def _load_keywords(self) -> pd.DataFrame:
        """Load and clean the keyword database"""
        # Try different separators - CSV might use comma or semicolon
        try:
            df = pd.read_csv(self.csv_path, sep=',')
        except:
            try:
                df = pd.read_csv(self.csv_path, sep=';')
            except:
                # Last resort - let pandas auto-detect
                df = pd.read_csv(self.csv_path)
        
        # Clean column names
        df.columns = [col.strip() for col in df.columns]
        
        # Print available columns for debugging
        print(f"📊 Available columns in CSV: {list(df.columns)}")
        
        # Convert numeric columns - handle both English and Portuguese column names
        # Handle Search Volume column - multiple possible names
        volume_col = None
        volume_patterns = [
            'volume de buscas',  # Portuguese
            'search volume',     # English
            'volume',           # English fallback
            'busca volume',     # Portuguese variation
            'volume busca'      # Portuguese variation
        ]
        
        for pattern in volume_patterns:
            for col in df.columns:
                if pattern in col.lower():
                    volume_col = col
                    print(f"✅ Found volume column: '{col}'")
                    break
            if volume_col:
                break
        
        if volume_col:
            # Handle Portuguese number format (e.g., "74.000" -> 74000)
            df['Volume'] = df[volume_col].astype(str).str.replace('.', '').str.replace(',', '.')
            df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce').fillna(0)
        else:
            print(f"⚠️ No volume column found. Available columns: {list(df.columns)}")
            df['Volume'] = 0  # Default value if no volume column found
        
        # Handle SEO Difficulty column - multiple possible names
        seo_difficulty_col = None
        seo_difficulty_patterns = [
            'seo difficulty',    # English
            'difficulty',        # English fallback
            'dificuldade seo',   # Portuguese
            'dificuldade',       # Portuguese fallback
            'seo dificuldade'    # Portuguese variation
        ]
        
        for pattern in seo_difficulty_patterns:
            for col in df.columns:
                if pattern in col.lower():
                    seo_difficulty_col = col
                    print(f"✅ Found SEO difficulty column: '{col}'")
                    break
            if seo_difficulty_col:
                break
        
        if seo_difficulty_col:
            df['SEO Difficulty'] = pd.to_numeric(df[seo_difficulty_col], errors='coerce').fillna(50)
        else:
            print(f"⚠️ No SEO difficulty column found. Available columns: {list(df.columns)}")
            df['SEO Difficulty'] = 50  # Default value if no difficulty column found
        
        # Handle Position column - multiple possible names
        position_col = None
        position_patterns = [
            'position',          # English
            'posição',           # Portuguese
            'posicao',           # Portuguese without accent
            'ranking',           # Alternative
            'rank'               # Alternative
        ]
        
        for pattern in position_patterns:
            for col in df.columns:
                if pattern in col.lower():
                    position_col = col
                    print(f"✅ Found position column: '{col}'")
                    break
            if position_col:
                break
        
        if position_col:
            df['Position'] = pd.to_numeric(df[position_col], errors='coerce').fillna(999)
        else:
            print(f"⚠️ No position column found. Available columns: {list(df.columns)}")
            df['Position'] = 999  # Default value if no position column found
        
        # Handle Keyword column - multiple possible names
        keyword_col = None
        keyword_patterns = [
            'palavra-chave',     # Portuguese
            'palavra chave',     # Portuguese without hyphen
            'keyword',           # English
            'keywords',          # English plural
            'termo',             # Portuguese alternative
            'termos'             # Portuguese alternative
        ]
        
        for pattern in keyword_patterns:
            for col in df.columns:
                if pattern in col.lower():
                    keyword_col = col
                    print(f"✅ Found keyword column: '{col}'")
                    break
            if keyword_col:
                break
        
        if keyword_col:
            df['Keywords'] = df[keyword_col]
        else:
            print(f"⚠️ No keyword column found. Available columns: {list(df.columns)}")
            # Try to use the first column as fallback
            if len(df.columns) > 0:
                df['Keywords'] = df.iloc[:, 0]  # Use first column as keywords
                print(f"⚠️ Using first column '{df.columns[0]}' as keywords")
            else:
                df['Keywords'] = ''  # Empty column if no data
        
        # Handle Search Intent column - multiple possible names
        intent_col = None
        intent_patterns = [
            'intenção de busca',  # Portuguese
            'intencao de busca',  # Portuguese without accent
            'search intent',      # English
            'intent',             # English fallback
            'intenção',           # Portuguese fallback
            'intencao'            # Portuguese fallback without accent
        ]
        
        for pattern in intent_patterns:
            for col in df.columns:
                if pattern in col.lower():
                    intent_col = col
                    print(f"✅ Found search intent column: '{col}'")
                    break
            if intent_col:
                break
        
        if intent_col:
            df['Search Intent'] = df[intent_col]
        else:
            print(f"⚠️ No search intent column found. Available columns: {list(df.columns)}")
            df['Search Intent'] = 'undefined'  # Default value
        
        # Handle CPC column - multiple possible names
        cpc_col = None
        cpc_patterns = [
            'cpc',               # English
            'cost per click',    # English full
            'custo por clique',  # Portuguese
            'custo clique'       # Portuguese variation
        ]
        
        for pattern in cpc_patterns:
            for col in df.columns:
                if pattern in col.lower():
                    cpc_col = col
                    print(f"✅ Found CPC column: '{col}'")
                    break
            if cpc_col:
                break
        
        if cpc_col:
            # Handle currency format (e.g., "R$1,20" -> 1.20)
            df['CPC'] = df[cpc_col].astype(str).str.replace('R$', '').str.replace(',', '.')
            df['CPC'] = pd.to_numeric(df['CPC'], errors='coerce').fillna(0)
        else:
            print(f"⚠️ No CPC column found. Available columns: {list(df.columns)}")
            df['CPC'] = 0  # Default value
        
        # Filter out competitor brand keywords
        df = self._filter_competitor_brands(df)
        
        print(f"✅ Successfully loaded {len(df)} keywords from database")
        return df
    
    def _filter_competitor_brands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out keywords containing competitor brand names"""
        if not self.competitor_brands:
            return df
        
        # Create patterns for competitor brands
        competitor_patterns = []
        for brand in self.competitor_brands:
            # Create variations of the brand name
            brand_variations = self._create_brand_variations(brand)
            competitor_patterns.extend(brand_variations)
        
        # Filter out keywords containing competitor brands
        filtered_df = df.copy()
        for pattern in competitor_patterns:
            mask = ~filtered_df['Keywords'].str.contains(pattern, case=False, na=False)
            filtered_df = filtered_df[mask]
        
        print(f"🔍 Filtered out {len(df) - len(filtered_df)} keywords containing competitor brands")
        return filtered_df
    
    def _create_brand_variations(self, brand: str) -> List[str]:
        """Create variations of a brand name for filtering"""
        variations = []
        
        # Original brand name
        variations.append(brand.lower())
        
        # Common variations
        brand_lower = brand.lower()
        
        # Remove spaces and common separators
        variations.append(brand_lower.replace(' ', ''))
        variations.append(brand_lower.replace(' ', '-'))
        variations.append(brand_lower.replace(' ', '_'))
        
        # Handle common brand name patterns
        if ' ' in brand_lower:
            # Split brand name and create variations
            parts = brand_lower.split()
            if len(parts) > 1:
                # First word only
                variations.append(parts[0])
                # Last word only
                variations.append(parts[-1])
                # Combined without space
                variations.append(''.join(parts))
        
        # Handle common brand suffixes/prefixes
        common_suffixes = ['brand', 'company', 'inc', 'ltd', 'corp']
        for suffix in common_suffixes:
            if brand_lower.endswith(suffix):
                variations.append(brand_lower.replace(suffix, '').strip())
        
        return list(set(variations))  # Remove duplicates
    
    def add_competitor_brands(self, competitor_brands: List[str]):
        """Add competitor brands to filter out"""
        self.competitor_brands.extend(competitor_brands)
        # Reload keywords with new filter
        self.keywords_df = self._load_keywords()
    
    def set_target_brand(self, target_brand: str):
        """Set the target brand name"""
        self.target_brand = target_brand
    
    def get_keywords_for_theme(self, theme: str, min_volume: int = 100) -> List[Dict]:
        """Get relevant keywords for a specific theme"""
        # Create search patterns for the theme
        theme_patterns = self._create_theme_patterns(theme)
        
        relevant_keywords = []
        for pattern in theme_patterns:
            matches = self.keywords_df[
                self.keywords_df['Keywords'].str.contains(pattern, case=False, na=False)
            ]
            relevant_keywords.extend(matches.to_dict('records'))
        
        # Remove duplicates and filter by volume
        unique_keywords = self._remove_duplicates(relevant_keywords)
        return [kw for kw in unique_keywords if kw['Volume'] >= min_volume]
    
    def get_high_volume_keywords(self, theme: str, min_volume: int = 500) -> List[Dict]:
        """Get high-volume keywords for a theme"""
        keywords = self.get_keywords_for_theme(theme)
        return [kw for kw in keywords if kw['Volume'] >= min_volume]
    
    def get_low_difficulty_keywords(self, theme: str, max_difficulty: int = 30) -> List[Dict]:
        """Get low-competition keywords for a theme"""
        keywords = self.get_keywords_for_theme(theme)
        return [kw for kw in keywords if kw['SEO Difficulty'] <= max_difficulty]
    
    def get_opportunity_keywords(self, theme: str, min_volume: int = 200, max_difficulty: int = 25) -> List[Dict]:
        """Get keywords with high volume and low difficulty (opportunities)"""
        keywords = self.get_keywords_for_theme(theme)
        return [
            kw for kw in keywords 
            if kw['Volume'] >= min_volume and kw['SEO Difficulty'] <= max_difficulty
        ]
    
    def get_product_keywords(self, product_name: str) -> List[Dict]:
        """Get keywords related to a specific product"""
        product_patterns = self._create_product_patterns(product_name)
        
        relevant_keywords = []
        for pattern in product_patterns:
            matches = self.keywords_df[
                self.keywords_df['Keywords'].str.contains(pattern, case=False, na=False)
            ]
            relevant_keywords.extend(matches.to_dict('records'))
        
        return self._remove_duplicates(relevant_keywords)
    
    def _create_theme_patterns(self, theme: str) -> List[str]:
        """Create search patterns for a theme"""
        # Extract key terms from theme
        theme_terms = theme.lower().split()
        
        # Create variations
        patterns = []
        for term in theme_terms:
            if len(term) > 3:  # Only meaningful terms
                patterns.append(term)
                # Add common variations
                if term.endswith('o'):
                    patterns.append(term[:-1] + 'a')  # masculine to feminine
                if term.endswith('a'):
                    patterns.append(term[:-1] + 'o')  # feminine to masculine
        
        return patterns
    
    def _create_product_patterns(self, product_name: str) -> List[str]:
        """Create search patterns for a product"""
        product_terms = product_name.lower().split()
        patterns = []
        
        for term in product_terms:
            if len(term) > 2:
                patterns.append(term)
        
        return patterns
    
    def _remove_duplicates(self, keywords: List[Dict]) -> List[Dict]:
        """Remove duplicate keywords based on the keyword text"""
        seen = set()
        unique_keywords = []
        
        for kw in keywords:
            keyword_text = kw['Keywords'].lower().strip()
            if keyword_text not in seen:
                seen.add(keyword_text)
                unique_keywords.append(kw)
        
        return unique_keywords
    
    def get_keyword_clusters(self, theme: str) -> Dict[str, List[Dict]]:
        """Group keywords by intent and volume"""
        keywords = self.get_keywords_for_theme(theme)
        
        clusters = {
            'high_volume': [kw for kw in keywords if kw['Volume'] >= 1000],
            'medium_volume': [kw for kw in keywords if 200 <= kw['Volume'] < 1000],
            'low_volume': [kw for kw in keywords if kw['Volume'] < 200],
            'low_difficulty': [kw for kw in keywords if kw['SEO Difficulty'] <= 25],
            'opportunities': self.get_opportunity_keywords(theme)
        }
        
        return clusters
    
    def get_competitor_analysis(self) -> Dict:
        """Analyze what competitor brands were filtered out"""
        if not self.competitor_brands:
            return {'filtered_brands': [], 'total_filtered': 0}
        
        # This would require keeping track of filtered keywords
        # For now, return basic info
        return {
            'filtered_brands': self.competitor_brands,
            'total_filtered': len(self.competitor_brands),
            'target_brand': self.target_brand
        } 