# Editorial Themes System Guide

## Overview

The Editorial Themes System enhances the copywriter crew by providing consistent content structure, tone, and guidelines for each type of blog post. This ensures that all content follows a predictable pattern while maintaining brand voice and SEO optimization.

## How It Works

### 1. **Editorial Theme Definition**
Each editorial theme defines:
- **Structure**: Specific sections and flow for the content
- **Tone**: Emotional and linguistic approach
- **Guidelines**: Word count, heading style, examples, CTA style, product limits

### 2. **Theme Mapping**
Existing content themes are mapped to editorial styles:
```python
theme_editorial_mapping = {
    "Your theme name": "editorial_theme_key",
    "Another theme": "product_showcase"
}
```

### 3. **Automatic Injection**
The system automatically injects editorial context into the crew workflow:
- Content strategist receives structure guidelines
- Copywriter follows specific tone and format requirements
- All agents respect editorial constraints

## Available Editorial Themes

### 🎓 **Educational Guide**
- **Purpose**: Comprehensive, step-by-step guides
- **Structure**: Introduction → Concept explanation → Implementation → Mistakes to avoid → Products → Conclusion
- **Tone**: Warm, knowledgeable, encouraging
- **Best for**: How-to content, concept explanations, beginner guides

### 🎯 **Product Showcase**
- **Purpose**: Deep dive into specific products
- **Structure**: Problem → Product intro → How it works → User scenarios → Comparison → Integration
- **Tone**: Confident, detailed, solution-focused
- **Best for**: Product launches, feature explanations, benefit demonstrations

### 🔄 **Routine Builder**
- **Purpose**: Help readers build personalized routines
- **Structure**: Understanding needs → Building blocks → Combinations → Lifestyle adaptation → Progress tracking
- **Tone**: Personal, empowering, practical
- **Best for**: Routine creation, product combinations, lifestyle integration

### 🛠️ **Problem Solver**
- **Purpose**: Address specific problems with targeted solutions
- **Structure**: Problem identification → Root causes → Traditional vs. modern → Your solution → Implementation → Results
- **Tone**: Empathetic, solution-oriented, reassuring
- **Best for**: Troubleshooting, problem resolution, alternative solutions

### 🌟 **Lifestyle Integration**
- **Purpose**: Connect products to broader lifestyle concepts
- **Structure**: Lifestyle connection → Daily habits → Seasonal considerations → Stress relationship → Busy schedules → Long-term approach
- **Tone**: Holistic, mindful, inspiring
- **Best for**: Wellness content, lifestyle tips, holistic approaches

## Implementation Steps

### Step 1: Create Editorial Themes File
Copy the template from `z_brands/editorial_themes_template.py` to your brand folder.

### Step 2: Customize for Your Brand
1. **Update theme descriptions** to match your industry
2. **Adjust structure** based on your content strategy
3. **Modify tone** to align with your brand voice
4. **Add examples** from your existing content

### Step 3: Map Existing Themes
```python
theme_editorial_mapping = {
    "Your existing theme 1": "educational_guide",
    "Your existing theme 2": "product_showcase",
    # Add more mappings
}
```

### Step 4: Customize Guidelines
Adjust word counts, heading styles, and requirements based on your content strategy.

## Benefits

### ✅ **Consistency**
- All content follows predictable structure
- Consistent tone across different themes
- Uniform product mention limits

### ✅ **Quality Control**
- Predefined word count targets
- Structured heading requirements
- Clear example and CTA guidelines

### ✅ **Efficiency**
- Agents know exactly what to produce
- Reduced revision cycles
- Faster content approval

### ✅ **Brand Alignment**
- Consistent voice across all content
- Aligned with brand strategy
- Professional content standards

## Example Usage

### Before (Without Editorial Themes)
```
Content strategist: "Create a blog post about our new product"
Copywriter: "I'll write something about the product"
Result: Inconsistent structure, varying tone, unpredictable length
```

### After (With Editorial Themes)
```
Content strategist: "Create a product showcase blog post"
Copywriter: "I'll follow the product showcase structure: Problem → Product intro → How it works → User scenarios → Comparison → Integration. Target: 1000-1300 words, 1-2 products, strong product-specific CTA"
Result: Consistent structure, aligned tone, predictable quality
```

## Customization Options

### 1. **Add New Editorial Themes**
```python
"custom_theme": {
    "name": "Custom Theme Name",
    "description": "What this theme accomplishes",
    "structure": ["Section 1", "Section 2", "Section 3"],
    "tone": "Your desired tone",
    "examples": ["Example 1", "Example 2"]
}
```

### 2. **Modify Existing Structures**
Update the structure arrays to match your preferred content flow.

### 3. **Adjust Guidelines**
Modify word counts, heading styles, and requirements based on your needs.

### 4. **Brand-Specific Examples**
Add real examples from your content library to guide future production.

## Troubleshooting

### ❌ **Editorial Theme Not Found**
- Check that the theme key exists in `editorial_themes`
- Verify the mapping in `theme_editorial_mapping`
- Ensure the file is properly loaded

### ❌ **Guidelines Not Applied**
- Verify that `editorial_guidelines` contains the theme key
- Check that the crew is receiving the editorial context
- Ensure agents are using the injected variables

### ❌ **Inconsistent Results**
- Review the editorial structure for clarity
- Check that tone descriptions are specific enough
- Verify that guidelines are comprehensive

## Best Practices

### 1. **Start Simple**
Begin with 2-3 editorial themes and expand gradually.

### 2. **Test and Iterate**
Use the system for a few content pieces and adjust based on results.

### 3. **Train Your Team**
Ensure all content creators understand the editorial themes and their purpose.

### 4. **Regular Updates**
Review and update editorial themes quarterly to maintain relevance.

### 5. **Monitor Performance**
Track content performance to see which editorial themes work best.

## Integration with Existing Systems

The Editorial Themes System works seamlessly with:
- **Existing theme structure** (`themes.py`)
- **SEO optimization** (`seo_themes.py`)
- **Content briefs** (`brief_summary.py`)
- **Product mapping** (`products.py`)
- **Context chunking** system

## Support

For questions or issues with the Editorial Themes System:
1. Check this documentation
2. Review the template file
3. Examine existing implementations
4. Contact the development team

---

**The Editorial Themes System transforms your content production from ad-hoc creation to systematic, high-quality, brand-aligned content generation.**

