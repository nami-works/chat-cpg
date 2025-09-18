# Brand Voice Template Guide

## Overview

The Brand Voice Template provides a structured approach to defining and maintaining consistent brand voice across all blog content. This template ensures that every piece of content reflects your brand's unique personality, values, and communication style.

## What's Included

### 1. **Core Voice Definition**
- **Primary & Secondary Tones**: Define your main voice characteristics
- **How to Apply**: Specific instructions for implementing your voice
- **Examples**: Concrete examples showing your voice in action

### 2. **Brand Persona**
- **Character Profile**: Who represents your brand voice
- **Communication Style**: How this persona communicates
- **Characteristics**: Key traits that define your persona

### 3. **Values & Approach**
- **Core Values**: How your brand values translate to content
- **Product Presentation**: Guidelines for showcasing products
- **Content Boundaries**: What to avoid in your content

### 4. **Content Structure**
- **Blog Structure**: Preferred content flow and organization
- **Theme Categories**: Main themes and sub-themes for your brand
- **Content Guidelines**: Word counts, formatting, and style requirements

### 5. **Language Specifics**
- **Pronouns & Formality**: Language level and gender considerations
- **Technical Terms**: How to handle jargon and complex concepts
- **Slang & Emojis**: Guidelines for informal language elements

## How to Use

### Step 1: Copy the Template
```bash
cp z_brands/z_templates/voice_template.py z_brands/your_brand/voice.py
```

### Step 2: Customize for Your Brand
1. **Update Brand Information**
   ```python
   "brand_name": "Your Actual Brand Name",
   "brand_category": "Your Industry (e.g., Beauty, Food, Tech)",
   "preferred_language": "pt_BR"  # or "en_US"
   ```

2. **Define Your Voice**
   ```python
   "voice_tone": {
       "primary": "Your primary tone (e.g., Inspirador, Real, Acessível)",
       "secondary": "Your secondary tone (e.g., Coloquial, Didático, Afetivo)",
       "description": "How your voice sounds and feels to readers"
   }
   ```

3. **Create Your Persona**
   ```python
   "persona": {
       "name": "Your Brand Persona Name",
       "profile": "Who this persona is and what they represent",
       "characteristics": ["Trait 1", "Trait 2", "Trait 3"]
   }
   ```

4. **Set Your Values**
   ```python
   "brand_values": {
       "core_values": {
           "value_1": "How this value appears in content",
           "value_2": "How this value appears in content"
       }
   }
   ```

### Step 3: Add Real Examples
Replace placeholder examples with actual content from your brand:
```python
"example": "Real example from your blog showing your voice"
```

### Step 4: Test and Refine
Use the template with your content team and adjust based on results.

## Template Sections Explained

### 🎯 **Voice Tone**
Defines the emotional and linguistic characteristics of your brand voice.

**Example from GE Beauty:**
```python
"voice_tone": {
    "primary": "Inspirador, Real, Acessível",
    "how_to_apply": [
        "Use linguagem simples e direta, como uma conversa entre amigas",
        "Evite jargões técnicos ou palavras rebuscadas",
        "Valorize o bem-estar e a leveza do dia a dia"
    ]
}
```

### 👤 **Persona**
Creates a consistent character who represents your brand voice.

**Example from Nude:**
```python
"persona": {
    "name": "Amigo(a) Especialista Acessível",
    "profile": "Pessoa próxima, que entende do assunto mas fala sem arrogância",
    "communication_style": [
        "Use perguntas retóricas que convidem à reflexão",
        "Seja empático: reconheça inseguranças e medos do leitor"
    ]
}
```

### 💎 **Brand Values**
Translates your brand values into practical content guidelines.

**Example:**
```python
"brand_values": {
    "core_values": {
        "sustentabilidade": "Trazer responsabilidade ambiental para o cotidiano",
        "transparência": "Explicar dados e processos de forma simples"
    }
}
```

### 📝 **Content Structure**
Defines how your content should be organized and presented.

**Example:**
```python
"blog_structure": {
    "general_structure": [
        "Abertura leve (pergunta, reflexão, insight)",
        "Contexto com informação ou dica prática",
        "Solução com produto como aliado",
        "Fechamento com convite à experimentação"
    ]
}
```

## Integration with Editorial Themes

The Brand Voice Template works seamlessly with the Editorial Themes System:

1. **Voice Consistency**: Editorial themes respect your brand voice
2. **Tone Alignment**: Each content type maintains your voice characteristics
3. **Persona Consistency**: All content reflects your brand persona
4. **Value Integration**: Content aligns with your brand values

## Best Practices

### ✅ **Do**
- Use real examples from your existing content
- Be specific about what makes your voice unique
- Include both positive and negative examples
- Test with your content team
- Update regularly based on performance

### ❌ **Don't**
- Use generic descriptions that could apply to any brand
- Forget to include examples
- Ignore your audience's language preferences
- Set unrealistic voice guidelines
- Forget to train your team on the voice

## Voice Consistency Checklist

Use the included checklist to ensure every piece of content maintains your voice:

- [ ] Does the content reflect our primary tone?
- [ ] Is the persona consistent throughout?
- [ ] Are we avoiding the 'don't' items?
- [ ] Does the product approach align with our values?
- [ ] Is the language appropriate for our audience?
- [ ] Does the structure follow our guidelines?
- [ ] Are we maintaining our unique voice markers?
- [ ] Does the content feel authentic to our brand?

## Examples from Real Brands

### GE Beauty Voice
- **Tone**: Inspirador, Real, Acessível
- **Persona**: Marcela Costa (mulher real, ativa, curiosa)
- **Approach**: Conversa entre amigas, linguagem simples, foco no bem-estar

### Nude Voice
- **Tone**: Coloquial, Didático, Afetivo, Engajador
- **Persona**: Amigo(a) Especialista Acessível
- **Approach**: Conversa direta, gírias leves, humor com ~tildes~

## Troubleshooting

### ❌ **Voice Too Generic**
- Add specific examples from your brand
- Define unique characteristics
- Include brand-specific language markers

### ❌ **Inconsistent Application**
- Train your content team
- Use the consistency checklist
- Review content regularly

### ❌ **Voice Doesn't Resonate**
- Test with your audience
- Adjust based on feedback
- Refine examples and guidelines

## Customization Tips

### 1. **Start with What You Know**
Begin with your existing voice.md file and translate it to the template structure.

### 2. **Add Real Examples**
Include actual content examples that demonstrate your voice perfectly.

### 3. **Be Specific**
Avoid generic descriptions - make everything specific to your brand.

### 4. **Test with Your Team**
Use the template with your content creators and adjust based on their feedback.

### 5. **Iterate and Improve**
Refine the template based on content performance and team feedback.

## Support

For questions about the Brand Voice Template:
1. Check this documentation
2. Review the template file
3. Examine existing implementations (GE Beauty, Nude)
4. Contact the development team

---

**The Brand Voice Template ensures consistent, authentic, and engaging content that truly represents your brand's unique personality and values.**
