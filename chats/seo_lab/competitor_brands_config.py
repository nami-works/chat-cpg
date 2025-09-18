"""
Competitor Brands Configuration
Defines brands that should be filtered out from keyword analysis
"""

# Major competitor brands in the haircare industry
MAJOR_COMPETITORS = [
    "loreal",
    "pantene", 
    "head shoulders",
    "dove",
    "tresemme",
    "garnier",
    "nivea",
    "johnson",
    "avon",
    "revlon"
]

# Premium/luxury competitor brands
PREMIUM_COMPETITORS = [
    "kerastase",
    "redken",
    "matrix",
    "wella",
    "schwarzkopf",
    "goldwell",
    "paul mitchell",
    "aveda",
    "bumble and bumble",
    "living proof"
]

# Drugstore/mass market competitors
MASS_MARKET_COMPETITORS = [
    "herbal essences",
    "suave",
    "finesse",
    "white rain",
    "vo5",
    "alberto",
    "clairol",
    "nice and easy",
    "natural instincts",
    "loving care"
]

# Professional salon brands
PROFESSIONAL_COMPETITORS = [
    "joico",
    "kenra",
    "redken",
    "matrix",
    "wella",
    "goldwell",
    "schwarzkopf",
    "paul mitchell",
    "aveda",
    "bumble and bumble"
]

# Natural/organic competitors
NATURAL_COMPETITORS = [
    "aubrey organics",
    "giovanni",
    "kiss my face",
    "alba botanica",
    "desert essence",
    "nature's gate",
    "jason",
    "tom's of maine",
    "burts bees",
    "alaffia"
]

# All competitor brands combined
ALL_COMPETITORS = (
    MAJOR_COMPETITORS + 
    PREMIUM_COMPETITORS + 
    MASS_MARKET_COMPETITORS + 
    PROFESSIONAL_COMPETITORS + 
    NATURAL_COMPETITORS
)

# Brand categories for different filtering strategies
COMPETITOR_CATEGORIES = {
    'major': MAJOR_COMPETITORS,
    'premium': PREMIUM_COMPETITORS,
    'mass_market': MASS_MARKET_COMPETITORS,
    'professional': PROFESSIONAL_COMPETITORS,
    'natural': NATURAL_COMPETITORS,
    'all': ALL_COMPETITORS
}

def get_competitor_brands(category: str = 'all') -> list:
    """
    Get competitor brands by category
    
    Args:
        category: 'major', 'premium', 'mass_market', 'professional', 'natural', or 'all'
    
    Returns:
        List of competitor brand names
    """
    return COMPETITOR_CATEGORIES.get(category, ALL_COMPETITORS)

def get_custom_competitor_list(brands: list) -> list:
    """
    Create a custom competitor list
    
    Args:
        brands: List of custom brand names
    
    Returns:
        List of competitor brand names
    """
    return [brand.lower().strip() for brand in brands if brand.strip()] 