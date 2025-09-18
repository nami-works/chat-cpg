# Product Slug Authority Fix - SEO Lab Prompt Enhancement

## Issue Addressed
The SEO Lab prompt incorrectly allowed product slugs to be referenced from secondary sources (brand guides, hardcoded lists, etc.), creating inconsistencies with the actual e-commerce catalog.

## Changes Made

### 1. Removed Hardcoded Product Slug References
- **Removed**: All hardcoded product slug lists from the prompt
- **Examples removed**:
  - `booster-antifrizz`, `booster-antioxidante`, `booster-fortificante`
  - `mascara-condicionadora`, `primer-cachos-definidos`
  - `shampoo-sem-sulfato`, etc.

### 2. Added Critical Authority Rule Section
- **New section**: "🚨 CRITICAL: Product Slug Authority Rule"
- **Key message**: "THE ONLY AUTHORITATIVE SOURCE FOR PRODUCT SLUGS IS THE `products.csv` FILE"
- **Mandatory requirements**:
  - All slugs must come from `Handle` column in `products.csv`
  - Never reference hardcoded lists or secondary sources
  - Every slug must exist in actual e-commerce store (Shopify)

### 3. Enhanced Product Mapping Guidelines
- **Updated**: Product Slug Mapping section with CSV-only requirements
- **Added**: Validation notes for e-commerce alignment
- **Emphasized**: Consistency with actual Shopify store

### 4. Updated Quality Validation Checklist
- **Added**: CSV Authority check
- **Added**: E-commerce Alignment verification
- **Added**: No Hardcoded References validation

### 5. Enhanced Examples and Documentation
- **Updated**: All product examples now include CSV authority notes
- **Added**: Validation reminders in code examples
- **Emphasized**: SEO and conversion tracking importance

## Benefits
- **Guarantees alignment** with actual e-commerce store (Shopify)
- **Prevents broken product links** from non-existent slugs
- **Ensures consistency** between blog content and product URLs
- **Critical for SEO** and conversion tracking
- **Eliminates inconsistencies** from multiple slug sources

## Implementation Notes
- All product slug references now point exclusively to `products.csv`
- System validates slug existence before content generation
- Maintains token optimization while ensuring accuracy
- Preserves content focus and performance benefits

## Files Modified
- `chats/seo_lab/_gpt/[seo_lab]prompt.md`

## Date
December 2024
