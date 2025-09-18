const OpenAI = require('openai');

class OpenAIService {
  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }

  async generateThemes(prompt, selectedProducts, shop) {
    try {
      const systemPrompt = `You are an expert content strategist for e-commerce stores. 
      Generate 5-10 specific, actionable blog post themes based on the user's prompt and selected products.
      
      For each theme, provide:
      - A compelling title (max 60 characters)
      - A brief description (max 150 characters)
      - 3-5 relevant keywords
      - Target audience
      - Content angle
      
      Focus on themes that will drive organic traffic and convert visitors to customers.
      Make themes specific to the products and brand, not generic.`;

      const userPrompt = `Store: ${shop.name}
      Products: ${selectedProducts.map(p => p.title).join(', ')}
      
      Content Brief: ${prompt}
      
      Generate themes that will help this store rank for relevant keywords and drive sales.`;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 2000
      });

      const content = response.choices[0].message.content;
      
      // Parse the response into structured themes
      const themes = this.parseThemesResponse(content);
      
      return themes;
    } catch (error) {
      console.error('Error generating themes:', error);
      throw error;
    }
  }

  async generateContent(themes, selectedProducts, settings, shop) {
    try {
      const systemPrompt = `You are an expert content writer and SEO specialist for e-commerce stores.
      Generate high-quality, SEO-optimized blog post content based on the provided themes and products.
      
      For each theme, create:
      - A compelling headline
      - Meta description (150-160 characters)
      - Introduction paragraph
      - 3-5 main sections with subheadings
      - Conclusion with call-to-action
      - Product recommendations integrated naturally
      - Internal linking opportunities
      - SEO-optimized content structure
      
      Content should be:
      - Engaging and valuable to readers
      - SEO-optimized for target keywords
      - Product-focused to drive sales
      - Brand-consistent in tone and voice
      - 1000-2000 words per post
      
      Use the brand's tone: ${settings.tone}
      Target language: ${settings.language}`;

      const content = [];
      
      for (const theme of themes) {
        const userPrompt = `Theme: ${theme.title}
        Description: ${theme.description}
        Keywords: ${theme.keywords.join(', ')}
        Products: ${selectedProducts.map(p => p.title).join(', ')}
        Store: ${shop.name}
        
        Generate a complete blog post for this theme.`;

        const response = await this.openai.chat.completions.create({
          model: 'gpt-4',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
          ],
          temperature: 0.7,
          max_tokens: 4000
        });

        const postContent = response.choices[0].message.content;
        const parsedContent = this.parseContentResponse(postContent, theme);
        
        content.push(parsedContent);
      }

      return content;
    } catch (error) {
      console.error('Error generating content:', error);
      throw error;
    }
  }

  async refineThemes(themes, feedback) {
    try {
      const systemPrompt = `You are an expert content strategist. 
      Refine the provided themes based on the user's feedback.
      
      Maintain the same structure but improve:
      - Relevance to the feedback
      - Specificity and actionability
      - SEO potential
      - Brand alignment
      
      Return the refined themes in the same format.`;

      const userPrompt = `Original themes: ${JSON.stringify(themes)}
      Feedback: ${feedback}
      
      Refine these themes based on the feedback.`;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 2000
      });

      const content = response.choices[0].message.content;
      const refinedThemes = this.parseThemesResponse(content);
      
      return refinedThemes;
    } catch (error) {
      console.error('Error refining themes:', error);
      throw error;
    }
  }

  async generateSEOKeywords(theme, productData) {
    try {
      const systemPrompt = `You are an SEO expert. 
      Generate 10-15 relevant, high-value keywords for the given theme and products.
      
      Include:
      - Primary keywords (1-2)
      - Secondary keywords (3-5)
      - Long-tail keywords (5-8)
      - Product-specific keywords (2-3)
      
      Focus on keywords with good search volume and commercial intent.`;

      const userPrompt = `Theme: ${theme.title}
      Description: ${theme.description}
      Products: ${productData.map(p => p.title).join(', ')}
      
      Generate SEO keywords for this theme.`;

      const response = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 1000
      });

      const content = response.choices[0].message.content;
      const keywords = this.parseKeywordsResponse(content);
      
      return keywords;
    } catch (error) {
      console.error('Error generating SEO keywords:', error);
      throw error;
    }
  }

  parseThemesResponse(content) {
    // Parse the AI response into structured theme objects
    const themes = [];
    const lines = content.split('\n');
    
    let currentTheme = null;
    
    for (const line of lines) {
      if (line.match(/^\d+\./)) {
        // New theme
        if (currentTheme) {
          themes.push(currentTheme);
        }
        currentTheme = {
          id: themes.length + 1,
          title: line.replace(/^\d+\.\s*/, '').trim(),
          description: '',
          keywords: [],
          targetAudience: '',
          contentAngle: ''
        };
      } else if (currentTheme && line.trim()) {
        if (line.includes('Description:') || line.includes('description:')) {
          currentTheme.description = line.replace(/.*[Dd]escription:\s*/, '').trim();
        } else if (line.includes('Keywords:') || line.includes('keywords:')) {
          const keywords = line.replace(/.*[Kk]eywords:\s*/, '').trim();
          currentTheme.keywords = keywords.split(',').map(k => k.trim());
        } else if (line.includes('Audience:') || line.includes('audience:')) {
          currentTheme.targetAudience = line.replace(/.*[Aa]udience:\s*/, '').trim();
        } else if (line.includes('Angle:') || line.includes('angle:')) {
          currentTheme.contentAngle = line.replace(/.*[Aa]ngle:\s*/, '').trim();
        }
      }
    }
    
    if (currentTheme) {
      themes.push(currentTheme);
    }
    
    return themes;
  }

  parseContentResponse(content, theme) {
    // Parse the AI response into structured content object
    const lines = content.split('\n');
    let currentSection = '';
    let sections = [];
    let html = '';
    
    for (const line of lines) {
      if (line.match(/^#\s+/)) {
        // Main heading
        currentSection = line.replace(/^#\s+/, '').trim();
        sections.push({ heading: currentSection, content: '' });
        html += `<h1>${currentSection}</h1>\n`;
      } else if (line.match(/^##\s+/)) {
        // Subheading
        currentSection = line.replace(/^##\s+/, '').trim();
        sections.push({ heading: currentSection, content: '' });
        html += `<h2>${currentSection}</h2>\n`;
      } else if (line.match(/^###\s+/)) {
        // Sub-subheading
        currentSection = line.replace(/^###\s+/, '').trim();
        sections.push({ heading: currentSection, content: '' });
        html += `<h3>${currentSection}</h3>\n`;
      } else if (line.trim()) {
        // Content
        if (sections.length > 0) {
          sections[sections.length - 1].content += line + '\n';
        }
        html += `<p>${line}</p>\n`;
      }
    }
    
    return {
      id: Date.now() + Math.random(),
      title: theme.title,
      theme: theme.title,
      content: content,
      html: html,
      sections: sections,
      wordCount: content.split(' ').length,
      status: 'draft',
      seoScore: Math.floor(Math.random() * 30) + 70, // Mock SEO score
      readabilityScore: Math.floor(Math.random() * 20) + 80, // Mock readability score
      targetKeywords: theme.keywords,
      metaDescription: this.generateMetaDescription(content),
      headingStructure: sections.map(s => s.heading).join(' > '),
      internalLinks: 0 // Mock value
    };
  }

  parseKeywordsResponse(content) {
    // Parse keywords from AI response
    const keywords = [];
    const lines = content.split('\n');
    
    for (const line of lines) {
      if (line.match(/^\d+\./)) {
        const keyword = line.replace(/^\d+\.\s*/, '').trim();
        if (keyword) {
          keywords.push(keyword);
        }
      } else if (line.includes(',')) {
        const lineKeywords = line.split(',').map(k => k.trim());
        keywords.push(...lineKeywords);
      }
    }
    
    return keywords;
  }

  generateMetaDescription(content) {
    // Generate a meta description from the content
    const firstParagraph = content.split('\n\n')[0];
    const words = firstParagraph.split(' ');
    const metaDescription = words.slice(0, 25).join(' ');
    return metaDescription.length > 160 ? metaDescription.substring(0, 157) + '...' : metaDescription;
  }
}

module.exports = {
  generateThemes: (prompt, selectedProducts, shop) => new OpenAIService().generateThemes(prompt, selectedProducts, shop),
  generateContent: (themes, selectedProducts, settings, shop) => new OpenAIService().generateContent(themes, selectedProducts, settings, shop),
  refineThemes: (themes, feedback) => new OpenAIService().refineThemes(themes, feedback),
  generateSEOKeywords: (theme, productData) => new OpenAIService().generateSEOKeywords(theme, productData)
};
