// This service integrates with the existing crew system from the original Nami codebase
// It adapts the crew system to work with Shopify app data

const { spawn } = require('child_process');
const path = require('path');

class CrewService {
  constructor() {
    this.crewPath = path.join(__dirname, '../../../crew-system');
  }

  async processContent(inputs) {
    try {
      // Prepare inputs for the crew system
      const crewInputs = this.prepareCrewInputs(inputs);
      
      // Call the crew system
      const result = await this.runCrewSystem(crewInputs);
      
      // Process the results
      const processedContent = this.processCrewResults(result);
      
      return processedContent;
    } catch (error) {
      console.error('Error processing content with crew system:', error);
      throw error;
    }
  }

  async generateSinglePost(inputs) {
    try {
      // Generate a single blog post using the crew system
      const crewInputs = this.prepareCrewInputs(inputs);
      crewInputs.single_post = true;
      
      const result = await this.runCrewSystem(crewInputs);
      const blogPost = this.processCrewResults(result)[0];
      
      return blogPost;
    } catch (error) {
      console.error('Error generating single post:', error);
      throw error;
    }
  }

  async optimizeContent(inputs) {
    try {
      // Optimize content using the crew system
      const crewInputs = this.prepareCrewInputs(inputs);
      crewInputs.optimization_type = inputs.optimization_type;
      
      const result = await this.runCrewSystem(crewInputs);
      const optimizedContent = this.processCrewResults(result);
      
      return optimizedContent;
    } catch (error) {
      console.error('Error optimizing content:', error);
      throw error;
    }
  }

  prepareCrewInputs(inputs) {
    // Convert Shopify app inputs to crew system format
    return {
      themes: inputs.themes.map(theme => ({
        title: theme.title,
        description: theme.description,
        keywords: theme.keywords,
        target_audience: theme.targetAudience,
        content_angle: theme.contentAngle
      })),
      products: inputs.products.map(product => ({
        id: product.id,
        title: product.title,
        handle: product.handle,
        product_type: product.product_type,
        vendor: product.vendor,
        tags: product.tags,
        variants: product.variants,
        images: product.images
      })),
      brand: {
        name: inputs.brand.name,
        domain: inputs.brand.domain,
        currency: inputs.brand.currency
      },
      blog: {
        handle: inputs.blog.handle,
        title: inputs.blog.title
      },
      benchmarks: {
        target_word_count: inputs.benchmarks.target_word_count,
        seo_score_target: inputs.benchmarks.seo_score_target,
        readability_target: inputs.benchmarks.readability_target
      },
      voice: {
        tone: inputs.voice.tone,
        language: inputs.voice.language
      },
      settings: inputs.settings,
      shop: inputs.shop
    };
  }

  async runCrewSystem(inputs) {
    return new Promise((resolve, reject) => {
      // This would call the actual crew system
      // For now, we'll simulate the crew system response
      const mockResult = this.generateMockCrewResult(inputs);
      resolve(mockResult);
    });
  }

  generateMockCrewResult(inputs) {
    // Mock crew system result for development
    const result = {
      themes: inputs.themes,
      content: [],
      metadata: {
        total_posts: inputs.themes.length,
        processing_time: Math.random() * 30 + 10,
        seo_scores: [],
        readability_scores: []
      }
    };

    // Generate mock content for each theme
    for (const theme of inputs.themes) {
      const content = {
        id: Date.now() + Math.random(),
        title: theme.title,
        theme: theme.title,
        content: this.generateMockContent(theme, inputs.products),
        html: this.generateMockHTML(theme, inputs.products),
        wordCount: Math.floor(Math.random() * 1000) + 800,
        status: 'draft',
        seoScore: Math.floor(Math.random() * 30) + 70,
        readabilityScore: Math.floor(Math.random() * 20) + 80,
        targetKeywords: theme.keywords,
        metaDescription: this.generateMetaDescription(theme),
        headingStructure: 'H1 > H2 > H3',
        internalLinks: Math.floor(Math.random() * 5) + 2
      };
      
      result.content.push(content);
      result.metadata.seo_scores.push(content.seoScore);
      result.metadata.readability_scores.push(content.readabilityScore);
    }

    return result;
  }

  generateMockContent(theme, products) {
    return `# ${theme.title}

${theme.description}

## Introduction

This comprehensive guide will help you understand everything about ${theme.title.toLowerCase()}. Whether you're a beginner or looking to enhance your knowledge, this article covers all the essential aspects.

## Key Benefits

1. **Expert Knowledge**: Learn from industry professionals
2. **Practical Tips**: Get actionable advice you can implement today
3. **Product Recommendations**: Discover the best products for your needs

## Product Spotlight

${products.map(product => `### ${product.title}
${product.title} is an excellent choice for ${theme.title.toLowerCase()}. With its ${product.variants[0]?.price ? `$${product.variants[0].price}` : 'competitive pricing'}, it offers great value for money.`).join('\n\n')}

## Conclusion

${theme.title} is an important topic that deserves attention. By following the advice in this guide, you'll be well-equipped to make informed decisions.

## Call to Action

Ready to get started? Check out our recommended products and take the first step towards better results.`;
  }

  generateMockHTML(theme, products) {
    const content = this.generateMockContent(theme, products);
    return content
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^\*\*(.+)\*\*$/gm, '<strong>$1</strong>')
      .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.+)$/gm, '<p>$1</p>');
  }

  generateMetaDescription(theme) {
    return `${theme.description} Learn expert tips and discover the best products for ${theme.title.toLowerCase()}.`;
  }

  processCrewResults(result) {
    // Process the crew system results and return formatted content
    return result.content.map(content => ({
      id: content.id,
      title: content.title,
      theme: content.theme,
      content: content.content,
      html: content.html,
      wordCount: content.wordCount,
      status: content.status,
      seoScore: content.seoScore,
      readabilityScore: content.readabilityScore,
      targetKeywords: content.targetKeywords,
      metaDescription: content.metaDescription,
      headingStructure: content.headingStructure,
      internalLinks: content.internalLinks
    }));
  }
}

module.exports = {
  processContent: (inputs) => new CrewService().processContent(inputs),
  generateSinglePost: (inputs) => new CrewService().generateSinglePost(inputs),
  optimizeContent: (inputs) => new CrewService().optimizeContent(inputs)
};
