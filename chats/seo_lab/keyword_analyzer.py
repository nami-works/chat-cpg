from keyword_database import KeywordDatabase
from typing import List, Dict, Optional

class KeywordAnalyzer:
    def __init__(self, keyword_db: KeywordDatabase = None):
        self.keyword_db = keyword_db or KeywordDatabase()
    
    def analyze_keyword_opportunities(self, theme: str) -> Dict:
        """Analyze keyword opportunities for a theme"""
        opportunities = self.keyword_db.get_opportunity_keywords(theme)
        high_volume = self.keyword_db.get_high_volume_keywords(theme)
        low_difficulty = self.keyword_db.get_low_difficulty_keywords(theme)
        
        analysis = {
            'high_value_keywords': [kw for kw in opportunities if kw['Volume'] >= 500],
            'low_competition_keywords': [kw for kw in opportunities if kw['SEO Difficulty'] <= 20],
            'product_keywords': [],
            'content_gaps': [],
            'total_opportunities': len(opportunities),
            'high_volume_count': len(high_volume),
            'low_difficulty_count': len(low_difficulty)
        }
        
        return analysis
    
    def get_keyword_recommendations(self, theme: str, max_keywords: int = 10) -> List[Dict]:
        """Get prioritized keyword recommendations for a theme"""
        opportunities = self.keyword_db.get_opportunity_keywords(theme)
        
        # Sort by opportunity score (volume / difficulty)
        scored_keywords = []
        for kw in opportunities:
            if kw['SEO Difficulty'] > 0:
                opportunity_score = kw['Volume'] / kw['SEO Difficulty']
                scored_keywords.append({
                    **kw,
                    'opportunity_score': opportunity_score
                })
        
        # Sort by opportunity score (descending)
        scored_keywords.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        return scored_keywords[:max_keywords]
    
    def analyze_product_keywords(self, product_name: str) -> Dict:
        """Analyze keywords for a specific product"""
        product_keywords = self.keyword_db.get_product_keywords(product_name)
        
        analysis = {
            'total_keywords': len(product_keywords),
            'high_volume_keywords': [kw for kw in product_keywords if kw['Volume'] >= 500],
            'low_difficulty_keywords': [kw for kw in product_keywords if kw['SEO Difficulty'] <= 25],
            'opportunities': [kw for kw in product_keywords if kw['Volume'] >= 200 and kw['SEO Difficulty'] <= 25],
            'keyword_list': product_keywords
        }
        
        return analysis
    
    def get_content_optimization_tips(self, theme: str) -> List[str]:
        """Get content optimization tips based on keyword analysis"""
        analysis = self.analyze_keyword_opportunities(theme)
        tips = []
        
        if analysis['high_value_keywords']:
            tips.append(f"Focus on {len(analysis['high_value_keywords'])} high-volume keywords with proven search traffic")
        
        if analysis['low_competition_keywords']:
            tips.append(f"Target {len(analysis['low_competition_keywords'])} low-competition keywords for easier ranking")
        
        if analysis['total_opportunities'] > 0:
            tips.append(f"Found {analysis['total_opportunities']} keyword opportunities with good volume/difficulty ratio")
        
        if analysis['high_volume_count'] > 0:
            tips.append(f"Include {analysis['high_volume_count']} high-volume keywords naturally in content")
        
        return tips
    
    def generate_keyword_report(self, theme: str) -> str:
        """Generate a comprehensive keyword report for a theme"""
        analysis = self.analyze_keyword_opportunities(theme)
        recommendations = self.get_keyword_recommendations(theme)
        
        report = f"""
# Keyword Analysis Report for: {theme}

## Summary
- Total opportunities found: {analysis['total_opportunities']}
- High-volume keywords: {analysis['high_volume_count']}
- Low-difficulty keywords: {analysis['low_difficulty_count']}

## Top Keyword Recommendations
"""
        
        for i, kw in enumerate(recommendations[:5], 1):
            report += f"""
{i}. **{kw['Keywords']}**
   - Search Volume: {kw['Volume']}
   - SEO Difficulty: {kw['SEO Difficulty']}
   - Opportunity Score: {kw.get('opportunity_score', 0):.2f}
"""
        
        report += f"""
## Content Optimization Tips
"""
        
        tips = self.get_content_optimization_tips(theme)
        for tip in tips:
            report += f"- {tip}\n"
        
        return report 